import torch
import torch.nn as nn
import torch.nn.functional as F

class AttentionModel(nn.Module):
    """
    Band Attention Module for Hyperspectral Image Processing
    
    논문 설명에 따른 Band Attention 모듈:
    1. 원본 HSI 큐브에서 H_avg (평균 풀링)과 H_max (최대 풀링)을 계산
    2. 공유된 MLP를 통해 각각의 스펙트럼 특징을 추출
    3. 두 특징을 더한 후 Sigmoid를 적용하여 band attention map 생성
    4. Attention map과 원본 데이터를 element-wise multiplication
    """
    def __init__(self, config: dict):
        super(AttentionModel, self).__init__()
        input_dim = config.get("input_dim")  # 입력 차원, 밴드 수 (예: 140)
        # 논문에서는 더 큰 hidden dimension 사용 (보통 input_dim//4 ~ input_dim//8)
        hidden_dim = config.get("hidden_dim", max(1, input_dim // 8))  

        # 공유된 MLP: W0 -> ReLU -> W1 (논문의 수식과 일치)
        self.shared_mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim, bias=False),  # W0
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim, bias=False)   # W1
        )

    # 논문 수식: Attention(H) = σ(MLP(H_avg) + MLP(H_max))
    # MLP 출력 벡터를 더한 후 SIGMOID 활성화 함수를 적용하여 attention map을 계산
    @staticmethod
    def compute_attention_map(mlp_data: torch.Tensor) -> torch.Tensor:
        """
        Args:
            mlp_data: MLP(H_avg) + MLP(H_max)의 결과
        Returns:
            band attention map: 각 밴드의 중요도를 나타내는 0~1 사이의 값
        """
        return torch.sigmoid(mlp_data)  # (D,) or (B, D)

    # 논문 수식: H' = H ⊙ Attention(H)
    # 생성된 attention map과 원본 HSI 데이터를 element-wise로 곱함
    @staticmethod
    def elementwise_multiplication(data: torch.Tensor, attention_map: torch.Tensor) -> torch.Tensor:
        """
        밴드 attention 값이 공간 차원 전반에 걸쳐 전파되어
        각 밴드별로 모든 공간(Height × Width) 위치에 동일한 가중치를 적용
        """
        return data * attention_map
    
    def forward(self, data: torch.Tensor) -> torch.Tensor:
        """
        논문의 방법론에 따른 Band Attention 수행
        
        Args:
            data: HSI 데이터 
                - (B, H, W, D): 배치 처리 (표준)
                - (H, W, D): 단일 이미지
        Returns:
            output: Band attention이 적용된 HSI 데이터
        """
        original_shape = data.shape
        
        # 배치 차원이 없는 경우 추가
        if data.dim() == 3:
            data = data.unsqueeze(0)  # (H, W, D) -> (1, H, W, D)
            single_sample = True
        else:
            single_sample = False
            
        B, H, W, D = data.shape
        
        # 논문의 Global Pooling 방식: H_avg와 H_max 계산
        # H_avg: Global Average Pooling over spatial dimensions (H, W)
        data_avg = torch.mean(data, dim=(1, 2))  # (B, D)
        
        # H_max: Global Max Pooling over spatial dimensions (H, W)  
        data_max = torch.max(data.view(B, -1, D), dim=1)[0]  # (B, D)
        
        # 공유된 MLP를 통해 각각의 스펙트럼 특징을 추출
        attn_map_avg = self.shared_mlp(data_avg)     # (B, D)
        attn_map_max = self.shared_mlp(data_max)     # (B, D)

        # 논문 수식: Attention(H) = σ(MLP(H_avg) + MLP(H_max))
        attn_map = self.compute_attention_map(attn_map_avg + attn_map_max)  # (B, D)

        # Attention map을 공간 차원으로 확장: (B, D) -> (B, H, W, D)
        # 각 밴드별로 모든 공간 위치에 동일한 가중치 적용
        attn_map_expanded = attn_map.unsqueeze(1).unsqueeze(2).expand(-1, H, W, -1)  # (B, H, W, D)

        # 논문 수식: H' = H ⊙ Attention(H) (element-wise multiplication)
        output = self.elementwise_multiplication(data, attn_map_expanded)

        # 원본이 단일 샘플이었다면 배치 차원 제거
        if single_sample:
            output = output.squeeze(0)  # (1, H, W, D) -> (H, W, D)

        return output
    
    def get_attention_weights(self, data: torch.Tensor) -> torch.Tensor:
        """
        주어진 입력에 대한 band attention weights만 반환
        
        Args:
            data: HSI 데이터 (H, W, D) or (B, H, W, D)
        Returns:
            attention_weights: 각 밴드의 중요도 (B, D) or (D,)
        """
        original_shape = data.shape
        
        # 배치 차원이 없는 경우 추가
        if data.dim() == 3:
            data = data.unsqueeze(0)  # (H, W, D) -> (1, H, W, D)
            single_sample = True
        else:
            single_sample = False
            
        B, H, W, D = data.shape
        
        # 논문의 Global Pooling 방식
        data_avg = torch.mean(data, dim=(1, 2))  # (B, D)
        data_max = torch.max(data.view(B, -1, D), dim=1)[0]  # (B, D)
        
        # MLP를 통해 attention map 생성
        attn_map_avg = self.shared_mlp(data_avg)
        attn_map_max = self.shared_mlp(data_max)
        attention_weights = self.compute_attention_map(attn_map_avg + attn_map_max)
        
        # 원본이 단일 샘플이었다면 배치 차원 제거
        if single_sample:
            attention_weights = attention_weights.squeeze(0)  # (1, D) -> (D,)
        
        return attention_weights
    
    def select_bands(self, data: torch.Tensor, num_bands: int = None, threshold: float = None) -> tuple:
        """
        논문의 방법론에 따른 밴드 선택
        
        Args:
            data: HSI 데이터 (H, W, D) or (B, H, W, D)
            num_bands: 선택할 밴드 개수 (논문에서는 140개 중 상위 20개 선택)
            threshold: attention weight 임계값 (이상인 밴드만 선택)
        Returns:
            selected_data: 선택된 밴드들만 포함한 데이터
            selected_indices: 선택된 밴드의 인덱스
            attention_weights: 각 밴드의 중요도
        """
        # Attention weights 계산
        attention_weights = self.get_attention_weights(data)
        
        if data.dim() == 3:
            single_sample = True
            weights_for_selection = attention_weights  # (D,)
        else:
            single_sample = False
            # 배치의 경우 평균 attention weights 사용
            weights_for_selection = attention_weights.mean(dim=0)  # (B, D) -> (D,)
        
        # 밴드 선택 방식 결정
        if num_bands is not None:
            # Top-K 방식: 상위 num_bands개 선택
            _, selected_indices = torch.topk(weights_for_selection, num_bands)
            selected_indices = selected_indices.sort()[0]  # 인덱스 정렬
        elif threshold is not None:
            # 임계값 방식: threshold 이상인 밴드들 선택
            selected_indices = torch.where(weights_for_selection >= threshold)[0]
        else:
            # 기본값: 상위 50% 밴드 선택
            num_bands = len(weights_for_selection) // 2
            _, selected_indices = torch.topk(weights_for_selection, num_bands)
            selected_indices = selected_indices.sort()[0]
        
        # 선택된 밴드들로 데이터 필터링
        if single_sample:
            selected_data = data[:, :, selected_indices]  # (H, W, selected_bands)
        else:
            selected_data = data[:, :, :, selected_indices]  # (B, H, W, selected_bands)
        
        return selected_data, selected_indices, attention_weights
    
    def get_band_importance_ranking(self, data: torch.Tensor) -> dict:
        """
        밴드 중요도 순위 정보 반환 (논문의 분석 방식)
        
        Args:
            data: HSI 데이터
        Returns:
            dict: 밴드 순위 정보
        """
        attention_weights = self.get_attention_weights(data)
        
        if data.dim() == 4:
            # 배치의 경우 평균 사용
            weights_for_ranking = attention_weights.mean(dim=0)
        else:
            weights_for_ranking = attention_weights
        
        # 중요도 순으로 정렬
        sorted_weights, sorted_indices = torch.sort(weights_for_ranking, descending=True)
        
        ranking_info = {
            'band_indices': sorted_indices.tolist(),
            'attention_weights': sorted_weights.tolist(),
            'total_bands': len(weights_for_ranking),
            'top_10_bands': sorted_indices[:10].tolist(),
            'top_20_bands': sorted_indices[:20].tolist(),
            'mean_attention': float(weights_for_ranking.mean()),
            'std_attention': float(weights_for_ranking.std())
        }
        
        return ranking_info

def create_model(model_name, config):
    if model_name == "attention_model":
        return AttentionModel(config)
    else:
        raise ValueError(f"Model {model_name} is not recognized.")