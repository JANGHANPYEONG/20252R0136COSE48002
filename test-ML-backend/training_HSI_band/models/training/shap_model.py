import numpy as np
import pandas as pd
import mlflow
from typing import Dict, Any, Tuple, List
import shap
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class SHAPBandSelector:
    """SHAP (SHapley Additive exPlanations) 밴드 선택기"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        SHAP 밴드 선택기 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.mlflow_info = config.get('mlflow_info', {})
        self.parameters = config.get('training', {}).get('parameters', {})
        
        # SHAP 파라미터
        self.background_samples = self.parameters.get('background_samples', 100)
        self.nsamples = self.parameters.get('nsamples', 100)
        self.random_state = self.parameters.get('random_state', 42)
        self.explainer_type = self.parameters.get('explainer_type', 'TreeExplainer')  # TreeExplainer, KernelExplainer
        self.model_type = self.parameters.get('model_type', 'RandomForest')  # RandomForest, XGBoost, etc.
        self.label_type = self.parameters.get('label_type', 'classification')  # classification, regression
        
        # 결과 저장
        self.selected_bands = None
        self.band_scores = None
        self.feature_names = None
        self.explainer = None
        self.model = None
        
        print(f"SHAP Band Selector initialized with {self.explainer_type}, {self.model_type}, {self.label_type}")
    
    def select_bands_with_scores(self, spectral_data: np.ndarray, labels: np.ndarray, 
                                pre_selected_bands: List[int], target_bands: int) -> Tuple[List[int], List[float]]:
        """
        SHAP를 사용하여 밴드 선택 수행
        
        Args:
            spectral_data: 스펙트럼 데이터 (n_samples, n_features)
            labels: 라벨 데이터 (n_samples,)
            pre_selected_bands: 전처리된 밴드 인덱스
            target_bands: 선택할 밴드 수
            
        Returns:
            selected_bands: 선택된 밴드 인덱스
            selected_scores: 선택된 밴드의 SHAP 점수
        """
        # MLflow 중첩 실행 시작
        if self.mlflow_info:
            with mlflow.start_run(nested=True):
                return self._select_bands_internal(spectral_data, labels, pre_selected_bands, target_bands)
        else:
            return self._select_bands_internal(spectral_data, labels, pre_selected_bands, target_bands)
    
    def _select_bands_internal(self, spectral_data: np.ndarray, labels: np.ndarray, 
                             pre_selected_bands: List[int], target_bands: int) -> Tuple[List[int], List[float]]:
        """내부 밴드 선택 로직"""
        
        print(f"Starting SHAP band selection with {target_bands} target bands...")
        
        # 전처리된 데이터 사용
        if pre_selected_bands is not None and len(pre_selected_bands) > 0:
            X = spectral_data[:, pre_selected_bands]
            print(f"Using {len(pre_selected_bands)} pre-selected bands")
        else:
            X = spectral_data
            pre_selected_bands = list(range(X.shape[1]))
            print(f"Using all {X.shape[1]} original bands")
        
        # 특성 이름 생성
        feature_names = [f'band_{i}' for i in pre_selected_bands]
        
        # 데이터 분할 (SHAP 계산을 위해) - label_type에 따라 stratify 결정
        stratify = labels if self.label_type == "classification" else None
        
        # stratify 에러 대비 예외 처리 (한 클래스뿐인 경우)
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, labels, test_size=0.2, random_state=self.random_state, stratify=stratify
            )
        except ValueError as e:
            print(f"Warning: Stratify failed ({e}), using random split instead")
            X_train, X_test, y_train, y_test = train_test_split(
                X, labels, test_size=0.2, random_state=self.random_state, stratify=None
            )
        
        # 모델 학습 (이미 정규화된 데이터 사용)
        self.model = self._create_model()
        self.model.fit(X_train, y_train)
        
        # SHAP Explainer 생성 (이미 정규화된 데이터 사용)
        self.explainer = self._create_explainer(X_train)
        
        # SHAP 값 계산 (이미 정규화된 데이터 사용)
        shap_values = self._calculate_shap_values(X_test)
        
        # 분류 모델의 경우 SHAP 값이 클래스별로 반환되므로 올바르게 처리
        if self.label_type == "classification" and isinstance(shap_values, list):
            # 클래스별 SHAP 값을 하나로 통합 (절댓값 평균)
            shap_values_combined = np.mean(np.abs(shap_values), axis=0)
            feature_importance = np.mean(shap_values_combined, axis=0)
        else:
            # 회귀 모델이거나 이미 올바른 형태인 경우
            feature_importance = np.mean(np.abs(shap_values), axis=0)
        
        # 상위 target_bands 선택
        top_indices = np.argsort(feature_importance)[-target_bands:][::-1]  # 내림차순
        
        # 원본 인덱스로 변환 (안전한 방법)
        selected_bands = []
        for idx in top_indices.flatten():
            selected_bands.append(pre_selected_bands[idx])
        selected_scores = feature_importance[top_indices].tolist()
        
        # 결과 저장
        self.selected_bands = selected_bands
        self.band_scores = selected_scores
        self.feature_names = feature_names
        
        # MLflow 로깅
        if self.mlflow_info:
            # 라벨 정보가 있으면 고유 키 생성
            label_name = self.mlflow_info.get('current_label', 'unknown')
            label_idx = self.mlflow_info.get('current_label_idx', 0)
            
            mlflow.log_param("shap_explainer_type", self.explainer_type)
            mlflow.log_param("shap_model_type", self.model_type)
            mlflow.log_param("shap_label_type", self.label_type)
            mlflow.log_param("shap_background_samples", self.background_samples)
            mlflow.log_param("shap_nsamples", self.nsamples)
            mlflow.log_param("shap_target_bands", target_bands)
            mlflow.log_param(f"shap_selected_bands_{label_name}", len(selected_bands))
            mlflow.log_param(f"shap_selected_indices_{label_name}", selected_bands)
            
            # SHAP 결과 정보 로깅
            shap_info = {
                'selected_bands': selected_bands,
                'selected_scores': selected_scores,
                'original_features': len(pre_selected_bands),
                'reduction_ratio': len(selected_bands) / len(pre_selected_bands),
                'method': 'shap',
                'explainer_type': self.explainer_type,
                'model_type': self.model_type
            }
            mlflow.log_dict(shap_info, "shap_selection_info.json")
            
            # SHAP 값 통계 로깅
            shap_stats = {
                'mean_shap_values': np.mean(shap_values, axis=0).tolist(),
                'std_shap_values': np.std(shap_values, axis=0).tolist(),
                'max_shap_values': np.max(shap_values, axis=0).tolist(),
                'min_shap_values': np.min(shap_values, axis=0).tolist()
            }
            mlflow.log_dict(shap_stats, "shap_values_stats.json")
            
            # 모델 성능 로깅 (이미 정규화된 데이터 사용)
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            mlflow.log_metric("train_r2_score", train_score)
            mlflow.log_metric("test_r2_score", test_score)
        
        print(f"SHAP band selection completed. Selected {len(selected_bands)} bands from {len(pre_selected_bands)} pre-selected bands.")
        
        return selected_bands, selected_scores
    
    def _create_model(self):
        """모델 생성 - label_type에 따라 분류/회귀 모델 선택"""
        if self.model_type == 'RandomForest':
            if self.label_type == 'classification':
                return RandomForestClassifier(
                    n_estimators=100,
                    random_state=self.random_state,
                    n_jobs=-1
                )
            else:  # regression
                return RandomForestRegressor(
                    n_estimators=100,
                    random_state=self.random_state,
                    n_jobs=-1
                )
        else:
            # 기본값으로 RandomForest 사용 (label_type에 따라)
            if self.label_type == 'classification':
                return RandomForestClassifier(
                    n_estimators=100,
                    random_state=self.random_state,
                    n_jobs=-1
                )
            else:  # regression
                return RandomForestRegressor(
                    n_estimators=100,
                    random_state=self.random_state,
                    n_jobs=-1
                )
    
    def _create_explainer(self, X_train: np.ndarray):
        """SHAP Explainer 생성"""
        if self.explainer_type == 'TreeExplainer':
            return shap.TreeExplainer(self.model)
        elif self.explainer_type == 'KernelExplainer':
            # 배경 데이터 샘플링
            background_data = X_train[:self.background_samples]
            return shap.KernelExplainer(self.model.predict, background_data)
        else:
            # 기본값으로 TreeExplainer 사용
            return shap.TreeExplainer(self.model)
    
    def _calculate_shap_values(self, X_test: np.ndarray) -> np.ndarray:
        """SHAP 값 계산"""
        try:
            if self.explainer_type == 'KernelExplainer':
                # KernelExplainer는 nsamples 파라미터 사용
                shap_values = self.explainer.shap_values(
                    X_test, 
                    nsamples=self.nsamples
                )
            else:
                # TreeExplainer는 nsamples 파라미터 불필요
                shap_values = self.explainer.shap_values(X_test)
            
            return shap_values
            
        except Exception as e:
            print(f"Error calculating SHAP values: {e}")
            # 대체 방법: 모델의 feature_importances_ 사용
            print("Using fallback method: model feature importance")
            return self._fallback_importance(X_test)
    
    def _fallback_importance(self, X_test: np.ndarray) -> np.ndarray:
        """SHAP 실패 시 대체 방법 (모델의 feature_importances_ 사용)"""
        if hasattr(self.model, 'feature_importances_'):
            # feature_importances_를 SHAP 값 형태로 변환
            importance = self.model.feature_importances_
            # 각 샘플에 대해 동일한 중요도 적용
            shap_values = np.tile(importance, (X_test.shape[0], 1))
            return shap_values
        else:
            # 랜덤 중요도 (최후의 수단)
            print("Warning: Using random importance as fallback")
            return np.random.rand(X_test.shape[0], X_test.shape[1])
    
    def get_selected_bands(self) -> List[int]:
        """선택된 밴드 인덱스 반환"""
        return self.selected_bands if self.selected_bands is not None else []
    
    def get_band_scores(self) -> List[float]:
        """선택된 밴드 점수 반환"""
        return self.band_scores if self.band_scores is not None else []
    
    def get_feature_names(self) -> List[str]:
        """특성 이름 리스트 반환"""
        return self.feature_names if self.feature_names is not None else []

def create_model(model_name: str, config: Dict[str, Any]) -> SHAPBandSelector:
    """
    SHAP 모델 생성 함수
    
    Args:
        model_name: 모델 이름
        config: 설정 딕셔너리
        
    Returns:
        SHAPBandSelector 인스턴스
    """
    return SHAPBandSelector(config) 