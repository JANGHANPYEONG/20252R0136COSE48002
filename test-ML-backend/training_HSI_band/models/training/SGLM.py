import numpy as np
import mlflow
from typing import Dict, Any, Tuple, List
from skimage.segmentation import slic
from skimage.future import graph
import warnings
warnings.filterwarnings('ignore')  # 경고 무시 설정

class SGLMBandSelector:
    """SGLM 기반 밴드 선택기 (원본 3D 하이퍼스펙트럴 이미지 입력)"""
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 설정 딕셔너리
                - n_segments: Superpixel 개수
                - compactness: Superpixel 균질성 제어 파라미터
                - lambda_spa: 공간 구조 정규화 강도
                - lambda_spe: 스펙트럼 구조 정규화 강도
                - max_iter: 그래프 자기표현 최적화 반복 횟수
                - mlflow_info: MLflow 로깅 정보
        """
        # Superpixel 분할 파라미터
        self.n_segments = config.get('n_segments', 100)
        self.compactness = config.get('compactness', 10.0)
        # 그래프 최적화 정규화 상수
        self.lambda_spa = config.get('lambda_spa', 0.1)
        self.lambda_spe = config.get('lambda_spe', 0.1)
        # 최적화 반복 횟수
        self.max_iter   = config.get('max_iter', 100)
        # MLflow 로깅 사용 정보
        self.mlflow_info = config.get('mlflow_info', {})
        # 선택된 밴드 인덱스 및 중요도 점수 저장 변수
        self.selected_bands: List[int] = []
        self.band_scores: List[float] = []
        print(f"Initialized SGLM with segments={self.n_segments}, compactness={self.compactness}, λ_spa={self.lambda_spa}, λ_spe={self.lambda_spe}")

    def select_bands_with_scores(
        self,
        hypercube: np.ndarray,
        target_bands: int
    ) -> Tuple[List[int], List[float]]:
        """
        원본 3D 하이퍼스펙트럴 이미지로부터 밴드 선택 수행

        Args:
            hypercube: np.ndarray, shape (H, W, B)
                H: 높이, W: 너비, B: 채널(밴드) 수
            target_bands: int
                선택할 상위 밴드 개수
        Returns:
            selected_bands: List[int]
                선택된 밴드의 원본 인덱스
            band_scores: List[float]
                각 선택된 밴드의 중요도 점수
        """
        # 1) Superpixel 분할: 입력 3D 이미지를 SLIC로 분할하여 레이블 맵 생성
        #    multichannel=False로 각 밴드를 독립 처리
        labels = slic(
            hypercube,
            n_segments=self.n_segments,
            compactness=self.compactness,
            multichannel=False
        )
        # 2) RAG 그래프 생성: 영역 간 평균 색상(스펙트럼 거리)을 가중치로 하는 인접 그래프
        rag = graph.rag_mean_color(hypercube, labels, mode='distance')

        # 3) 노드별 스펙트럼 벡터 계산
        regions = np.unique(labels)  # Superpixel 레이블 리스트
        B = hypercube.shape[2]       # 밴드 수
        # 각 영역별 평균 스펙트럼을 저장할 행렬 초기화
        X = np.zeros((len(regions), B))
        for i, r in enumerate(regions):
            mask = (labels == r)  # 해당 레이블 영역 마스크
            # 영역 내 모든 픽셀에 대해 각 밴드 평균 계산
            X[i, :] = hypercube[mask].mean(axis=0)

        # 4) A_spa: 공간 유사도 행렬 생성
        n = len(regions)
        A_spa = np.zeros((n, n))
        for u, v, d in rag.edges(data=True):
            # RAG의 weight: 두 영역 간 평균 스펙트럼 거리
            # 거리가 작을수록 유사도가 높으므로 역수 취함
            A_spa[u, v] = A_spa[v, u] = 1.0 / (1.0 + d['weight'])

        # 5) A_spe: 채널(밴드) 간 스펙트럼 유사도
        # X.T: shape (B, regions)
        corr = np.corrcoef(X.T)            # 밴드 간 상관계수
        A_spe = np.nan_to_num(corr)        # NaN을 0으로 대체

        # 6) 전처리된 밴드 인덱스, 여기서는 0..B-1 전체 밴드 사용
        pre_selected = list(range(B))

        # 7) 내부 최적화 및 Top-K 밴드 선택
        return self._select_bands_internal(
            X, A_spa, A_spe, pre_selected, target_bands
        )

    def _select_bands_internal(
        self,
        X: np.ndarray,
        A_spa: np.ndarray,
        A_spe: np.ndarray,
        pre_selected: List[int],
        K: int
    ) -> Tuple[List[int], List[float]]:
        """
        그래프 자기표현(Grap self-representation) 최적화 및 밴드 중요도 계산

        Args:
            X: (n_regions, B) 영역별 대표 스펙트럼 벡터
            A_spa: (n_regions, n_regions) 공간 유사도 행렬
            A_spe: (n_regions, n_regions) 스펙트럼 유사도 행렬
            pre_selected: List[int] 원본 밴드 인덱스
            K: int 선택할 밴드 수
        Returns:
            selected_bands, band_scores
        """
        # Laplacian 행렬 계산: L = D - A
        D_spa = np.diag(A_spa.sum(axis=1))
        L_spa = D_spa - A_spa
        D_spe = np.diag(A_spe.sum(axis=1))
        L_spe = D_spe - A_spe

        # Z 초기화: 대각행렬 형태, 자기표현 계수 행렬
        n_bands = X.shape[1]
        Z = np.eye(n_bands)

        # 반복 최적화: 목표 함수의 gradient descent (예시)
        for _ in range(self.max_iter):
            # 데이터 재구성 항 gradient
            grad = -2 * X.T.dot(X - X.dot(Z))
            # 스펙트럼 정규화 항 gradient
            grad += 2 * self.lambda_spe * (L_spe.dot(Z) + L_spe.T.dot(Z))
            # 공간 정규화 항 gradient
            grad += 2 * self.lambda_spa * (Z.dot(L_spa) + Z.dot(L_spa.T))
            # 고정 학습률로 업데이트
            Z -= 0.01 * grad

        # 각 밴드 i의 중요도: Z의 절대값 합 (행 기준)
        scores = np.sum(np.abs(Z), axis=1)
        # 상위 K 인덱스 선택
        top_idx = np.argsort(scores)[-K:][::-1]
        self.selected_bands = [pre_selected[i] for i in top_idx]
        self.band_scores    = scores[top_idx].tolist()

        # MLflow 매개변수 및 결과 로깅
        if self.mlflow_info:
            mlflow.log_param("sglm_segments", self.n_segments)
            mlflow.log_param("sglm_compactness", self.compactness)
            mlflow.log_param("sglm_lambda_spa", self.lambda_spa)
            mlflow.log_param("sglm_lambda_spe", self.lambda_spe)
            mlflow.log_param("sglm_max_iter", self.max_iter)
            mlflow.log_param("sglm_target_bands", K)
            mlflow.log_param("sglm_selected_bands", self.selected_bands)

        print(f"Selected bands: {self.selected_bands}")
        return self.selected_bands, self.band_scores

    def get_selected_bands(self) -> List[int]:
        """선택된 밴드 인덱스 반환"""
        return self.selected_bands

    def get_band_scores(self) -> List[float]:
        """선택된 밴드 중요도 점수 반환"""
        return self.band_scores

# 팩토리 함수: 외부에서 모델 인스턴스를 쉽게 생성

def create_model(model_name: str, config: Dict[str, Any]) -> SGLMBandSelector:
    """SGLM 모델 생성 함수"""
    return SGLMBandSelector(config)
