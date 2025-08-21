# [0821] TODO 리스트
"""
# [0821] TODO 리스트
# 냉장 1일차만 있으면 이거만 뜬다. 1일차 7일차 둘 다 있는 경우 id로 달라는 요청을 보내면, 1일차 7일차 둘 다 FE에 보내야한다.
# 일단 이미지는 일반 rgb이미지, hsi이미지, xai이미지 db에 저장되어 있는 경로를 모두 반환한다.
# DATA를 두개를 보내던지 구현이 편한대로 해서 보내야한다. 

DB 관련해서 500 에러 나는거 해결
"""

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict
# from pydantic import UrlConstraints
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.database import get_db
from app.db.db_model import (
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
    xai: Optional[str] = Field(None, description="XAI 설명 이미지 URL")  # 추가
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

    # 냉장 여부 1일 혹은 7일 (1일차 false, 7일차 true), 기본값은 false
    refrigerated: Optional[bool] = Field(False, alias="refrigerated", description="냉장 여부")

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
def get_dashboard_data(
    search_id: Optional[str] = Query(None, alias="id", description="ID 검색어 (이력번호/관리번호)"),
    period: Optional[str] = Query("전체", description="조회기간: 1주, 1개월, 1분기, 1년, 전체"),
    start_date: Optional[date] = Query(None, alias="startDate", description="시작날짜 (생성일 기준)"),
    end_date: Optional[date] = Query(None, alias="endDate", description="종료날짜 (생성일 기준)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db)
):
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
            # DeepAgingInfo에서 모든 냉장 데이터 가져오기 (1일차, 7일차 등)
            deep_aging_infos = (db.query(DeepAgingInfo)
                            .filter(DeepAgingInfo.id == meat.id)
                            .order_by(DeepAgingInfo.seqno.asc())  # 1일차부터 정렬
                            .all())
            
            # 냉장 데이터가 없으면 기본 데이터 하나만 생성
            if not deep_aging_infos:
                deep_aging_infos = [None]  # 기본 처리를 위해
            
            # 각 냉장 단계별로 데이터 생성
            for deep_aging_info in deep_aging_infos:
                sample_no = deep_aging_info.seqno if deep_aging_info else 0
                is_deep_aged = bool(deep_aging_info.isCompleted) if deep_aging_info else False
                process_date = deep_aging_info.date.strftime("%Y-%m-%d") if (deep_aging_info and deep_aging_info.date) else None

                # CategoryInfo에서 부위 정보 가져오기
                category = (db.query(CategoryInfo)
                        .filter(CategoryInfo.id == meat.categoryId)
                        .first()) if meat.categoryId else None
                
                part_primal = category.primalValue if category else None
                part_secondary = category.secondaryValue if category else None

                # 해당 냉장 단계의 관능평가 데이터 가져오기
                sensory_eval = (db.query(SensoryEval)
                            .filter(SensoryEval.id == meat.id, SensoryEval.seqno == sample_no)
                            .order_by(SensoryEval.createdAt.desc())
                            .first())
                
                human_overall = sensory_eval.overall if sensory_eval else None
                rgb_image_url = sensory_eval.imagePath if (sensory_eval and sensory_eval.imagePath) else None

                # 해당 냉장 단계의 AI 예측 데이터 가져오기 (냉장 여부 확인)
                ai_sensory = (db.query(AI_SensoryEval)
                            .filter(AI_SensoryEval.id == meat.id, AI_SensoryEval.seqno == sample_no)
                            .first())
                
                ai_overall = ai_sensory.overall if ai_sensory else None
                ai_grade_num = ai_sensory.xai_gradeNum if ai_sensory else None
                xai_image_url = ai_sensory.xai_imagePath if ai_sensory else None

                # 냉장 여부 판단 (AI_SensoryEval의 isRefrigerated 사용)
                refrigerated = bool(ai_sensory.isRefrigerated) if ai_sensory else False

                # HSI 이미지 데이터 (냉장 여부 고려)
                msi_count = (db.query(HSIImagesBands)
                            .filter(
                                HSIImagesBands.id == meat.id, 
                                HSIImagesBands.seqno == sample_no,
                                HSIImagesBands.isRefrigerated == refrigerated
                            )
                            .count())

                hsi_image = (db.query(HSIImagesBands)
                            .filter(
                                HSIImagesBands.id == meat.id, 
                                HSIImagesBands.seqno == sample_no,
                                HSIImagesBands.isRefrigerated == refrigerated
                            )
                            .first())
                hsi_image_url = hsi_image.filename if hsi_image else None

                # 스펙트럼 데이터 (성능 최적화)
                spectrum_data = []
                if sample_no > 0 and limit <= 10:
                    try:
                        spectrum_records = (db.query(HSISensoryEval)
                                        .filter(
                                            HSISensoryEval.id == meat.id, 
                                            HSISensoryEval.seqno == sample_no,
                                            HSISensoryEval.isRefrigerated == refrigerated
                                        )
                                        .limit(50)
                                        .all())
                        
                        for record in spectrum_records:
                            try:
                                absorption_value = 0.0
                                for attr_name in ['Total', 'total', 'L', 'Marbling', 'marbling', 'overall']:
                                    if hasattr(record, attr_name):
                                        attr_value = getattr(record, attr_name)
                                        if attr_value is not None:
                                            absorption_value = float(attr_value)
                                            break
                                
                                spectrum_data.append(SpectrumPoint(
                                    wavelength_nm=430.0 + len(spectrum_data) * 10,
                                    mean_absorption=absorption_value
                                ))
                                
                            except Exception:
                                continue
                                
                    except Exception:
                        spectrum_data = []

                # 업로드 일시
                uploaded_at = meat.createdAt.strftime("%Y-%m-%d %H:%M:%S") if meat.createdAt else None

                # trace_key 생성
                trace_key = f"{meat.traceNum}-{sample_no:02d}{'R' if refrigerated else 'F'}" if meat.traceNum else f"{meat.id}-{sample_no:02d}{'R' if refrigerated else 'F'}"

                data_items.append(DashboardItem(
                    id=meat.id,
                    traceNum=meat.traceNum,
                    sampleNo=sample_no,
                    traceKey=trace_key,
                    refrigerated=refrigerated,
                    part=Part(
                        primal=part_primal,
                        secondary=part_secondary
                    ),
                    isDeepAged=is_deep_aged,
                    butcheryDate=meat.butcheryYmd.strftime("%Y-%m-%d") if meat.butcheryYmd else None,
                    processDate=process_date,
                    uploadedAt=uploaded_at,
                    images=ImageSummary(
                        rgb=rgb_image_url,
                        hsi=hsi_image_url,
                        xai=xai_image_url,
                        msiCount=msi_count
                    ),
                    sensory=SensorySummary(
                        humanOverall=human_overall,
                        aiOverall=ai_overall,
                        aiGradeNum=ai_grade_num
                    ),
                    spectrum=spectrum_data if spectrum_data else None
                ))
        
        # return을 올바른 위치로 이동
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
