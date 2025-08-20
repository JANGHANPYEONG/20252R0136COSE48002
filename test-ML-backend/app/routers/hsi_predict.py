from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import json
import mlflow
import boto3
from botocore.exceptions import ClientError
import tempfile
import subprocess
import asyncio
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.db_model import HSIImagesBands, SpectralInfo, HSISensoryEval
from app.connection.s3_connect import get_s3_client

router = APIRouter()


# Request/Response 모델
class HSIPredictRequest(BaseModel):
    id: str
    seqno: int
    isRefrigerated: bool


class HSIPredictResponse(BaseModel):
    message: str
    predictions: List[float]
    xai_image_urls: List[str]
    created_at: datetime


class HSIPredictor:
    """HSI 예측을 위한 클래스"""
    
    def __init__(self):
        # MLflow 설정 로드
        self.mlflow_config = self._load_mlflow_config()
        self.s3_client = get_s3_client()
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
        # 캐싱 폴더 설정
        self.image_cache_dir = self.mlflow_config['cache_dirs']['image_cache']
        self.xai_cache_dir = self.mlflow_config['cache_dirs']['xai_cache']
        
        # MLflow 설정
        mlflow.set_tracking_uri(self.mlflow_config['backend-store-uri'])
        
    def _load_mlflow_config(self):
        """MLflow 설정 파일을 로드합니다."""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "training_HSI", "configs", "mlflow_config.json"
        )
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"MLflow config not found: {config_path}")
            
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def get_latest_run_id(self) -> str:
        """특정 experiment에서 최신 run_id를 가져옵니다."""
        try:
            experiment_name = self.mlflow_config['experiment_name']
            experiment = mlflow.get_experiment_by_name(experiment_name)
            
            if experiment is None:
                raise ValueError(f"Experiment '{experiment_name}' not found")
            
            # 최신 run 조회
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["start_time DESC"],
                max_results=1
            )
            
            if runs.empty:
                raise ValueError(f"No runs found in experiment '{experiment_name}'")
            
            latest_run = runs.iloc[0]
            run_id = latest_run['run_id']
            
            print(f"Latest run_id: {run_id} from experiment: {experiment_name}")
            return run_id
            
        except Exception as e:
            print(f"Error getting latest run_id: {e}")
            raise
    
    def get_hsi_images_from_db(self, db: Session, id: str, seqno: int, isRefrigerated: bool) -> List[dict]:
        """DB에서 HSI 이미지 정보를 조회합니다."""
        try:
            # hsi_images_bands 테이블에서 이미지 정보 조회
            hsi_images = db.query(HSIImagesBands).filter(
                HSIImagesBands.id == id,
                HSIImagesBands.seqno == seqno,
                HSIImagesBands.isRefrigerated == isRefrigerated
            ).all()
            
            if not hsi_images:
                raise ValueError(f"No HSI images found for id={id}, seqno={seqno}, isRefrigerated={isRefrigerated}")
            
            # spectral_info와 조인하여 파장 정보 포함
            image_info_list = []
            for hsi_image in hsi_images:
                spectral_info = db.query(SpectralInfo).filter(
                    SpectralInfo.spectral_index == hsi_image.spectral_index
                ).first()
                
                if spectral_info:
                    image_info_list.append({
                        'filename': hsi_image.filename,
                        'wavelength_nm': spectral_info.wavelength_nm,
                        'spectral_index': hsi_image.spectral_index
                    })
            
            # 파장 순으로 정렬
            image_info_list.sort(key=lambda x: x['wavelength_nm'])
            
            print(f"Found {len(image_info_list)} HSI images")
            return image_info_list
            
        except Exception as e:
            print(f"Error getting HSI images from DB: {e}")
            raise
    
    def download_images_from_s3(self, image_info_list: List[dict]) -> List[str]:
        """S3에서 HSI 이미지들을 다운로드합니다."""
        try:
            downloaded_paths = []
            
            for image_info in image_info_list:
                # S3 키 생성
                s3_key = f"train_dataset/HSI/{image_info['filename']}"
                
                # 로컬 캐시 경로
                local_path = os.path.join(self.image_cache_dir, image_info['filename'])
                
                # 이미 캐시된 경우 스킵
                if os.path.exists(local_path):
                    print(f"Image already cached: {local_path}")
                    downloaded_paths.append(local_path)
                    continue
                
                # S3에서 다운로드
                print(f"Downloading from S3: {s3_key}")
                self.s3_client.download_file(
                    self.bucket_name,
                    s3_key,
                    local_path
                )
                
                downloaded_paths.append(local_path)
                print(f"Downloaded to: {local_path}")
            
            return downloaded_paths
            
        except Exception as e:
            print(f"Error downloading images from S3: {e}")
            raise
    
    def run_prediction(self, run_id: str, image_paths: List[str]) -> dict:
        """predict_xai_hsi.py를 실행하여 예측을 수행합니다."""
        try:
            # predict_xai_hsi.py 스크립트 경로
            script_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "training_HSI", "predict_xai_hsi.py"
            )
            
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Prediction script not found: {script_path}")
            
            # 임시 결과 파일 생성
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_result_path = temp_file.name
            
            try:
                # 명령어 구성
                cmd = [
                    "python", script_path,
                    "--run_id", run_id,
                    "--image_paths"
                ] + image_paths + [
                    "--output", temp_result_path,
                    "--xai",
                    "--xai-mode", "gradcam",
                    "--xai-return", "url",
                    "--xai-save-dir", self.xai_cache_dir
                ]
                
                print(f"Executing command: {' '.join(cmd)}")
                
                # 스크립트 실행
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(script_path)
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else "Unknown error"
                    print(f"Script execution failed: {error_msg}")
                    raise RuntimeError(f"Prediction script failed: {error_msg}")
                
                # 결과 파일 읽기
                if not os.path.exists(temp_result_path):
                    raise FileNotFoundError(f"Result file was not created: {temp_result_path}")
                
                with open(temp_result_path, 'r') as f:
                    prediction_result = json.load(f)
                
                print(f"Prediction completed successfully")
                return prediction_result
                
            finally:
                # 임시 파일 정리
                if os.path.exists(temp_result_path):
                    os.unlink(temp_result_path)
                    print(f"Cleaned up temporary result file: {temp_result_path}")
                    
        except Exception as e:
            print(f"Error during prediction: {e}")
            raise
    
    def upload_xai_images_to_s3(self, id: str, seqno: int, isRefrigerated: bool) -> List[str]:
        """캐시된 XAI 이미지들을 S3에 업로드합니다."""
        try:
            uploaded_urls = []
            
            # XAI 이미지 파일들 찾기
            xai_files = [f for f in os.listdir(self.xai_cache_dir) if f.endswith('.png')]
            
            for xai_file in xai_files:
                local_path = os.path.join(self.xai_cache_dir, xai_file)
                
                # S3 키 생성
                s3_key = f"hsi_xai_images/{id}/{seqno}/{isRefrigerated}/{xai_file}"
                
                # S3에 업로드
                print(f"Uploading XAI image to S3: {s3_key}")
                self.s3_client.upload_file(
                    local_path,
                    self.bucket_name,
                    s3_key
                )
                
                # S3 URL 생성
                s3_url = f"s3://{self.bucket_name}/{s3_key}"
                uploaded_urls.append(s3_url)
                
                print(f"Uploaded XAI image: {s3_url}")
            
            return uploaded_urls
            
        except Exception as e:
            print(f"Error uploading XAI images to S3: {e}")
            raise
    
    def save_results_to_db(self, db: Session, id: str, seqno: int, isRefrigerated: bool, 
                          predictions: List[float], xai_image_path: str):
        """예측 결과를 DB에 저장합니다."""
        try:
            # 기존 레코드 확인
            existing_record = db.query(HSISensoryEval).filter(
                HSISensoryEval.id == id,
                HSISensoryEval.seqno == seqno,
                HSISensoryEval.isRefrigerated == isRefrigerated
            ).first()
            
            if existing_record:
                # 기존 레코드 업데이트
                existing_record.marbling = predictions[0] if len(predictions) > 0 else None
                existing_record.color = predictions[1] if len(predictions) > 1 else None
                existing_record.texture = predictions[2] if len(predictions) > 2 else None
                existing_record.surfaceMoisture = predictions[3] if len(predictions) > 3 else None
                existing_record.overall = predictions[4] if len(predictions) > 4 else None
                existing_record.xai_imagePath = xai_image_path
                existing_record.createdAt = datetime.now()
            else:
                # 새 레코드 생성
                new_record = HSISensoryEval(
                    id=id,
                    seqno=seqno,
                    isRefrigerated=isRefrigerated,
                    marbling=predictions[0] if len(predictions) > 0 else None,
                    color=predictions[1] if len(predictions) > 1 else None,
                    texture=predictions[2] if len(predictions) > 2 else None,
                    surfaceMoisture=predictions[3] if len(predictions) > 3 else None,
                    overall=predictions[4] if len(predictions) > 4 else None,
                    xai_imagePath=xai_image_path,
                    createdAt=datetime.now()
                )
                db.add(new_record)
            
            db.commit()
            print(f"Results saved to DB for id={id}, seqno={seqno}, isRefrigerated={isRefrigerated}")
            
        except Exception as e:
            db.rollback()
            print(f"Error saving results to DB: {e}")
            raise


@router.post("/", response_model=HSIPredictResponse)
async def hsi_predict(request: HSIPredictRequest, db: Session = Depends(get_db)):
    """HSI 이미지 예측을 수행하는 엔드포인트"""
    try:
        print(f"HSI prediction request received: id={request.id}, seqno={request.seqno}, isRefrigerated={request.isRefrigerated}")
        
        # HSI Predictor 초기화
        predictor = HSIPredictor()
        
        # 1. DB에서 HSI 이미지 정보 조회
        image_info_list = predictor.get_hsi_images_from_db(
            db, request.id, request.seqno, request.isRefrigerated
        )
        
        # 2. S3에서 이미지 다운로드
        image_paths = predictor.download_images_from_s3(image_info_list)
        
        # 3. MLflow에서 최신 run_id 조회
        run_id = predictor.get_latest_run_id()
        
        # 4. 예측 실행
        prediction_result = predictor.run_prediction(run_id, image_paths)
        
        # 5. 예측값 추출 (regression 값들)
        predictions = []
        for sample_key, sample_result in prediction_result.items():
            if 'regression' in sample_result:
                reg_values = sample_result['regression']
                # column_config.json의 순서에 맞춰 정렬
                label_order = ['Marbling', 'Meat Color', 'Texture', 'Surface Moisture', 'Total']
                for label in label_order:
                    if label in reg_values:
                        predictions.append(reg_values[label])
                break  # 첫 번째 샘플만 처리
        
        # 6. XAI 이미지들을 S3에 업로드
        xai_image_urls = predictor.upload_xai_images_to_s3(
            request.id, request.seqno, request.isRefrigerated
        )
        
        # 7. 결과를 DB에 저장
        xai_image_path = f"hsi_xai_images/{request.id}/{request.seqno}/{request.isRefrigerated}"
        predictor.save_results_to_db(
            db, request.id, request.seqno, request.isRefrigerated, 
            predictions, xai_image_path
        )
        
        print(f"HSI prediction completed successfully")
        
        return HSIPredictResponse(
            message="HSI prediction completed successfully",
            predictions=predictions,
            xai_image_urls=xai_image_urls,
            created_at=datetime.now()
        )
        
    except Exception as e:
        print(f"Error in HSI prediction: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"HSI prediction failed: {str(e)}")
