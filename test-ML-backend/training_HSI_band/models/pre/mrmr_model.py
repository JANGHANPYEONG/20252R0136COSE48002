import numpy as np
import mlflow
from typing import Dict, Any, Tuple, List
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.metrics import mutual_info_score
import warnings
warnings.filterwarnings('ignore')

class MRMRBandSelector:
    """MRMR (Minimum Redundancy Maximum Relevance) 밴드 선택기"""
    
    def __init__(self, config: Dict[str, Any], label_type: str = 'classification'):
        """
        MRMR 밴드 선택기 초기화
        
        Args:
            config: 설정 딕셔너리
            label_type: 분류/회귀 타입 ('classification' 또는 'regression')
        """
        self.config = config
        self.mlflow_info = config.get('mlflow_info', {})
        self.parameters = config.get('preprocessing', {}).get('parameters', {})
        
        # MRMR 파라미터
        self.criterion = self.parameters.get('criterion', 'MID')  # MID, MIQ, MIC
        self.k = self.parameters.get('k', 50)
        self.random_state = self.parameters.get('random_state', 42)
        self.label_type = label_type  # 외부에서 전달받은 label_type 사용
        
        # 결과 저장
        self.selected_bands = None
        self.band_scores = None
        self.feature_names = None
        
        print(f"MRMR Band Selector initialized with criterion: {self.criterion}, k: {self.k}, label_type: {self.label_type}")
    
    def select_bands(self, spectral_data: np.ndarray, labels: np.ndarray, 
                    target_bands: int, feature_names: List[str] = None) -> List[int]:
        """
        MRMR를 사용하여 밴드 선택 수행
        
        Args:
            spectral_data: 스펙트럼 데이터 (n_samples, n_features)
            labels: 라벨 데이터 (n_samples,)
            target_bands: 선택할 밴드 수
            feature_names: 특성 이름 리스트 (옵션)
            
        Returns:
            selected_bands: 선택된 밴드 인덱스 리스트
        """
        # MLflow 중첩 실행 시작
        if self.mlflow_info:
            with mlflow.start_run(nested=True):
                return self._select_bands_internal(spectral_data, labels, target_bands, feature_names)
        else:
            return self._select_bands_internal(spectral_data, labels, target_bands, feature_names)
    
    def _select_bands_internal(self, spectral_data: np.ndarray, labels: np.ndarray, 
                             target_bands: int, feature_names: List[str] = None) -> List[int]:
        """내부 밴드 선택 로직"""
        
        print(f"Starting MRMR band selection with {target_bands} target bands...")
        
        # 특성 이름 생성 (이미 정규화된 데이터 사용)
        if feature_names is None:
            feature_names = [f'band_{i}' for i in range(spectral_data.shape[1])]
        
        # label_type에 따라 연속형/이산형 판단
        is_continuous = self.label_type == "regression"
        
        # MRMR 알고리즘 실행 (이미 정규화된 데이터 사용)
        try:
            selected_indices = self._mrmr_selection(spectral_data, labels, target_bands, is_continuous)
            print(f"MRMR selected {len(selected_indices)} bands")
            
        except Exception as e:
            print(f"Error in MRMR selection: {e}")
            # 대체 방법: 상관관계 기반 선택
            selected_indices = self._fallback_selection(spectral_data, labels, target_bands)
        
        # 결과 저장
        self.selected_bands = selected_indices
        self.feature_names = feature_names
        
        # MLflow 로깅
        if self.mlflow_info:
            # 라벨 정보가 있으면 고유 키 생성
            label_name = self.mlflow_info.get('current_label', 'unknown')
            label_idx = self.mlflow_info.get('current_label_idx', 0)
            
            mlflow.log_param("mrmr_criterion", self.criterion)
            mlflow.log_param("mrmr_label_type", self.label_type)
            mlflow.log_param("mrmr_target_bands", target_bands)
            mlflow.log_param(f"mrmr_selected_bands_{label_name}", len(selected_indices))
            mlflow.log_param(f"mrmr_selected_indices_{label_name}", selected_indices)
            
            # 밴드 선택 정보 로깅
            band_info = {
                'selected_bands': selected_indices,
                'original_features': len(feature_names),
                'reduction_ratio': len(selected_indices) / len(feature_names)
            }
            mlflow.log_dict(band_info, "band_selection_info.json")
            
            # 선택된 밴드의 통계 정보
            selected_data = spectral_data[:, selected_indices]
            band_stats = {
                'mean_values': np.mean(selected_data, axis=0).tolist(),
                'std_values': np.std(selected_data, axis=0).tolist(),
                'min_values': np.min(selected_data, axis=0).tolist(),
                'max_values': np.max(selected_data, axis=0).tolist()
            }
            mlflow.log_dict(band_stats, "selected_bands_stats.json")
        
        print(f"MRMR band selection completed. Selected {len(selected_indices)} bands from {len(feature_names)} original bands.")
        
        return selected_indices
    
    def _mrmr_selection(self, X: np.ndarray, y: np.ndarray, k: int, is_continuous: bool) -> List[int]:
        """MRMR 알고리즘 구현"""
        n_features = X.shape[1]
        
        # Relevance 계산 (Mutual Information)
        if is_continuous:
            relevance = mutual_info_regression(X, y, random_state=self.random_state)
        else:
            relevance = mutual_info_classif(X, y, random_state=self.random_state)
        
        # 첫 번째 특성 선택 (가장 높은 relevance)
        selected = [np.argmax(relevance)]
        remaining = list(range(n_features))
        remaining.remove(selected[0])
        
        # 나머지 k-1개 특성 선택
        for _ in range(min(k-1, len(remaining))):
            best_score = -np.inf
            best_feature = None
            
            for feature in remaining:
                # Relevance
                rel = relevance[feature]
                
                # Redundancy 계산
                redundancy = 0
                for selected_feature in selected:
                    # 특성 간 상관관계로 redundancy 근사
                    corr = np.abs(np.corrcoef(X[:, feature], X[:, selected_feature])[0, 1])
                    redundancy += corr
                
                if len(selected) > 0:
                    redundancy /= len(selected)
                
                # MRMR 점수 계산
                if self.criterion == 'MID':
                    score = rel - redundancy
                elif self.criterion == 'MIQ':
                    score = rel / (redundancy + 1e-8)
                else:  # MIC
                    score = rel / (redundancy + 1e-8)
                
                if score > best_score:
                    best_score = score
                    best_feature = feature
            
            if best_feature is not None:
                selected.append(best_feature)
                remaining.remove(best_feature)
        
        return selected
    
    def _fallback_selection(self, spectral_data: np.ndarray, labels: np.ndarray, 
                          target_bands: int) -> List[int]:
        """MRMR 실패 시 대체 선택 방법 (상관관계 기반)"""
        
        print("Using fallback selection method (correlation-based)...")
        
        # 라벨과의 상관관계 계산
        correlations = []
        for i in range(spectral_data.shape[1]):
            corr = np.corrcoef(spectral_data[:, i], labels)[0, 1]
            correlations.append(abs(corr))
        
        # 상관관계가 높은 순으로 정렬
        sorted_indices = np.argsort(correlations)[::-1]
        selected_indices = sorted_indices[:target_bands]
        
        return selected_indices.tolist()
    
    def get_selected_bands(self) -> List[int]:
        """선택된 밴드 인덱스 반환"""
        return self.selected_bands if self.selected_bands is not None else []
    
    def get_feature_names(self) -> List[str]:
        """특성 이름 리스트 반환"""
        return self.feature_names if self.feature_names is not None else []

def create_model(model_name: str, config: Dict[str, Any], label_type: str = 'classification') -> MRMRBandSelector:
    """
    MRMR 모델 생성 함수
    
    Args:
        model_name: 모델 이름
        config: 설정 딕셔너리
        label_type: 분류/회귀 타입 ('classification' 또는 'regression')
        
    Returns:
        MRMRBandSelector 인스턴스
    """
    return MRMRBandSelector(config, label_type) 