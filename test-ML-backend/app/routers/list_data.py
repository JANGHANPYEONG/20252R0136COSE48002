from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict
# from pydantic import UrlConstraints
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..db.database import get_db
from ..db.db_model import (
    Meat, CategoryInfo, DeepAgingInfo,
    SensoryEval, AI_SensoryEval,
    HeatedmeatSensoryEval, AI_HeatedmeatSeonsoryEval,
    HSISensoryEval, AI_HSISensoryEval, HSIImagesBands, SpectralInfo
)
router = APIRouter()

STATUS_LABEL_TO_CODE = {"정상": 2, "보류": 0, "반려": 1}

# --- 부위(카테고리) 요약 ---
class Part(BaseModel):
    primal: Optional[str] = Field(None, description="대분류 부위명 (primalValue)")
    secondary: Optional[str] = Field(None, description="소분류 부위명 (secondaryValue)")

# --- 이미지 요약(리스트용) ---
# rgb, hsi 이미지는 이미지의 위치를 반환함.
class ImageSummary(BaseModel):
    rgb: Optional[str] = Field(None, description="대표 RGB 이미지 URL")
    hsi: Optional[str] = Field(None, description="대표 HSI 이미지 URL")
    msiCount: int = Field(0, description="MSI 밴드 이미지 개수")

# --- 관능/예측 요약(리스트용) ---
class SensorySummary(BaseModel):
    humanOverall: Optional[float] = Field(None, description="사람 관능 overall")
    aiOverall: Optional[float] = Field(None, description="AI 예측 overall")
    aiGradeNum: Optional[int] = Field(None, description="AI 예측 등급(숫자)")

# --- 스펙트럼 요약(리스트용) ---
class SpectrumPoint(BaseModel):
    wavelength_nm: float = Field(..., description="파장(nm)")
    mean_absorption: float = Field(..., description="평균 흡수율")

# ---- 대시보드 응답 모델 ----
# 이력번호 + sampleNo, 부위, 딥에이징여부, 도축일자, 가공일자, 업로드일시, 
# 이미지, 관능평가 + 예측평가값, 파장별 평균 흡수율
class DashboardItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # 핵심 키
    id: str = Field(..., description="육류 관리번호")
    trace_num: str = Field(..., alias="traceNum", description="이력번호")
    sample_no: int = Field(..., alias="sampleNo", description="샘플 번호(seqno)")
    trace_key: str = Field(..., alias="traceKey", description="이력번호+sampleNo 조합 키 (예: 2300-05)")

    # 부위
    part: Part = Field(..., alias="part", description="부위 정보(primal/secondary)")

    # 상태/일시
    is_deep_aged: bool = Field(..., alias="isDeepAged", description="딥에이징 여부")
    butchery_date: Optional[str] = Field(None, alias="butcheryDate", description="도축일자 YYYY-MM-DD")
    process_date: Optional[str] = Field(None, alias="processDate", description="가공일자(딥에이징 date)")
    uploaded_at: Optional[str] = Field(None, alias="uploadedAt", description="업로드/생성 기준 일시")

    # 이미지 요약
    images: ImageSummary = Field(..., alias="images", description="대표 이미지 요약")

    # 관능 요약
    sensory: SensorySummary = Field(..., alias="sensory", description="관능/예측 요약")

    # 스펙트럼 요약(선택: 리스트에선 생략 가능)
    spectrum: Optional[List[SpectrumPoint]] = Field(
        default=None,
        alias="spectrum",
        description="파장별 평균 흡수율(리스트에서는 Option)"
    )

class DashboardResponse(BaseModel):
    """대시보드 응답"""
    model_config = ConfigDict(populate_by_name=True)
    
    success: bool = Field(..., description="성공 여부")
    total_count: int = Field(..., alias="totalCount", description="전체 데이터 수")
    page: int = Field(..., description="현재 페이지")
    limit: int = Field(..., description="페이지당 항목 수")
    total_pages: int = Field(..., alias="totalPages", description="전체 페이지 수")
    data: List[DashboardItem] = Field(..., description="데이터 목록")


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(
    # ID 검색
    search_id: Optional[str] = Query(None, alias="id", description="ID 검색어 (이력번호/관리번호)"),
    
    # 상태 필터 (화면의 "전체" 드롭다운)
    # status: Optional[str] = Query("전체", description="상태 필터: 전체, 정상, 보류, 반려"),
    
    # 데이터 생성일 기준 조회기간 (화면의 기간 버튼들)
    period: Optional[str] = Query("전체", description="조회기간: 1주, 1개월, 1분기, 1년, 전체"),
    
    # 직접 날짜 입력 (데이터 생성일 기준)
    start_date: Optional[date] = Query(None, alias="startDate", description="시작날짜 (생성일 기준)"),
    end_date: Optional[date] = Query(None, alias="endDate", description="종료날짜 (생성일 기준)"),
    
    # 페이징
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    
    db: Session = Depends(get_db)
):
    """
    대시보드 데이터 조회 API
    
    - 필터링 기준: 데이터 생성일 (createdAt)
    - 화면 요소:
      * ID 검색 필드
      * 상태 드롭다운 (전체/정상/보류/반려)
      * 조회기간 버튼 (1주/1개월/1분기/1년/전체)
      * 시작날짜/종료날짜 직접 입력
      * 페이징 지원
    """
    try:
        from datetime import timedelta
        
        # 기본 쿼리
        query = db.query(Meat)
        conditions = []
        
        # ID 검색 (이력번호 또는 육류관리번호)
        if search_id and search_id.strip():
            conditions.append(
                or_(
                    Meat.id.ilike(f"%{search_id}%"),
                    Meat.traceNum.ilike(f"%{search_id}%")
                )
            )
        
        """
        # 상태 필터
        if status and status != "전체":
            if status == "정상":
                conditions.append(Meat.statusType == 2)
            elif status == "보류":
                conditions.append(Meat.statusType == 0)
            elif status == "반려":
                conditions.append(Meat.statusType == 1)
        """

        # 조회기간 처리 (데이터 생성일 기준)
        if period and period != "전체":
            today = date.today()
            
            if period == "1주":
                start_date = today - timedelta(weeks=1)
                end_date = today
            elif period == "1개월":
                start_date = today - timedelta(days=30)
                end_date = today
            elif period == "1분기":
                start_date = today - timedelta(days=90)
                end_date = today
            elif period == "1년":
                start_date = today - timedelta(days=365)
                end_date = today
        
        # 데이터 생성일 기준 날짜 범위 적용
        if start_date:
            conditions.append(Meat.createdAt >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            conditions.append(Meat.createdAt <= datetime.combine(end_date, datetime.max.time()))
        if start_date and end_date and start_date > end_date:
            raise HTTPException(status_code=422, detail="시작일이 종료일보다 늦을 수 없습니다.")

        # 조건들을 AND로 결합
        if conditions:
            query = query.filter(and_(*conditions))
        
        # 전체 개수 계산
        total_count = query.count()
        
        # 페이징 및 정렬 (생성일 최신순)
        offset = (page - 1) * limit
        results = query.order_by(Meat.createdAt.desc()).offset(offset).limit(limit).all()
        
        # 전체 페이지 수 계산
        total_pages = (total_count + limit - 1) // limit
        
        # 응답 데이터 변환
        data_items = []
        for meat in results:
            """
            # 상태명 변환
            status_name = "알 수 없음"
            if meat.statusType == 2:
                status_name = "정상"
            elif meat.statusType == 0:
                status_name = "보류"
            elif meat.statusType == 1:
                status_name = "반려"
            """

            """
            # test용 임시 코드
            # for meat in results: 바로 아래에 추가 (임시)
            dai = (db.query(DeepAgingInfo)
                    .filter(DeepAgingInfo.id == meat.id)
                    .order_by(DeepAgingInfo.seqno.desc())
                    .first())
            seqno = dai.seqno if dai else 0
            is_deep_aged = bool(dai.isCompleted) if dai else False
            process_date = dai.date.strftime("%Y-%m-%d %H:%M:%S") if dai and dai.date else None

            cat = db.query(CategoryInfo).filter(CategoryInfo.id == meat.categoryId).first() if meat.categoryId else None
            part_primal = cat.primalValue if cat else None
            part_secondary = cat.secondaryValue if cat else None

            se = (db.query(SensoryEval)
                    .filter(SensoryEval.id == meat.id, SensoryEval.seqno == seqno)
                    .order_by(SensoryEval.createdAt.desc())
                    .first())
            human_overall = se.overall if se else None
            rgb_url = se.imagePath if (se and se.imagePath) else None

            ai_se = (db.query(AI_SensoryEval)
                      .filter(AI_SensoryEval.id == meat.id, AI_SensoryEval.seqno == seqno)
                      .first())
            ai_overall = ai_se.overall if ai_se else None
            ai_grade = ai_se.xai_gradeNum if ai_se else None

            msi_count = (db.query(HSIImagesBands)
                          .filter(HSIImagesBands.id == meat.id, HSIImagesBands.seqno == seqno)
                          .count())
            hsi_url = None  # 대표 HSI 선택 규칙 정해지면 채우기

            uploaded_at = meat.createdAt.strftime("%Y-%m-%d %H:%M:%S") if meat.createdAt else None

            data_items.append(DashboardItem(
            id=meat.id,
            trace_num=meat.traceNum,
            sample_no=seqno,
            trace_key=f"{meat.traceNum}-{seqno}",
            part=Part(primal=part_primal, secondary=part_secondary),
            is_deep_aged=is_deep_aged,
            butchery_date=meat.butcheryYmd.strftime("%Y-%m-%d") if meat.butcheryYmd else None,
            process_date=process_date,
            uploaded_at=uploaded_at,
            images=ImageSummary(rgb=rgb_url, hsi=hsi_url, msiCount=msi_count),
            sensory=SensorySummary(humanOverall=human_overall, aiOverall=ai_overall, aiGradeNum=ai_grade),
            spectrum=None,  # 리스트에선 생략
        )) """
            data_items.append(DashboardItem(
                id=meat.id,
                trace_num=meat.traceNum,
                sample_no=meat.sampleNo,
                trace_key=meat.traceKey,
                part=Part(
                    primal=meat.partPrimal,
                    secondary=meat.partSecondary
                ),
                is_deep_aged=meat.isDeepAged,
                butchery_date=meat.butcheryYmd.strftime("%Y-%m-%d") if meat.butcheryYmd else None,
                process_date=meat.processDate.strftime("%Y-%m-%d") if meat.processDate else None,
                uploaded_at=meat.uploadedAt.strftime("%Y-%m-%d %H:%M:%S") if meat.uploadedAt else None,
                images=ImageSummary(
                    rgb=meat.imageRgb,
                    hsi=meat.imageHsi,
                    msiCount=meat.imageMsiCount
                ),
                sensory=SensorySummary(
                    humanOverall=meat.sensoryHumanOverall,
                    aiOverall=meat.sensoryAiOverall,
                    aiGradeNum=meat.sensoryAiGradeNum
                ),
                spectrum=[
                    SpectrumPoint(
                        wavelength_nm=point.wavelength_nm,
                        mean_absorption=point.mean_absorption
                    ) for point in meat.spectrumPoints
                ]
            ))
            
        return DashboardResponse(
            success=True,
            totalCount=total_count,
            page=page,
            limit=limit,
            totalPages=total_pages,
            data=data_items
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"대시보드 데이터 조회 중 오류가 발생했습니다: {str(e)}"
        )

"""
@router.get("/dashboard/filters")
async def get_dashboard_filters(db: Session = Depends(get_db)):
    # 대시보드 필터 옵션 조회
    try:
        # 상태 옵션
        status_options = [
            {"value": "전체", "label": "전체"},
            {"value": "정상", "label": "정상"},
            {"value": "보류", "label": "보류"},
            {"value": "반려", "label": "반려"}
        ]
        
        # 기간 옵션
        period_options = [
            {"value": "전체", "label": "전체"},
            {"value": "1주", "label": "1주"},
            {"value": "1개월", "label": "1개월"},
            {"value": "1분기", "label": "1분기"},
            {"value": "1년", "label": "1년"}
        ]
        
        return {
            "success": True,
            "data": {
                "statusOptions": status_options,
                "periodOptions": period_options
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"필터 옵션 조회 중 오류가 발생했습니다: {str(e)}"
        )
"""