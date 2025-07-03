import timm
import torch
import torch.nn as nn

class LSAAttention(nn.Module):
    def __init__(self, dim):
        super(LSAAttention, self).__init__()
        self.temperature = nn.Parameter(torch.ones(1) * (dim ** 0.5))  # √dim으로 초기화

    def forward(self, Q, K, V):
        # Query와 Key로 유사도 행렬 계산
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.temperature
        
        # 대각선 마스킹 적용 (자기 자신에 대한 주의 제거)
        mask = torch.eye(scores.size(-1), device=scores.device).bool()
        scores = scores.masked_fill(mask, float('-inf'))
        
        # Softmax로 주의 가중치 계산
        attention_weights = torch.softmax(scores, dim=-1)
        
        # Attention 가중치를 사용해 값 계산
        output = torch.matmul(attention_weights, V)
        return output

class BaseModelWithLSA(nn.Module):
    def __init__(self, model_name, pretrained, num_classes, in_chans):
        super(BaseModelWithLSA, self).__init__()
        # timm을 이용해 기본 모델 생성
        self.base_model = timm.create_model(model_name=model_name, pretrained=pretrained, num_classes=num_classes, in_chans=in_chans)
        
        # LSA 적용 (기본 모델의 마지막 attention layer에서 사용)
        self.lsa_attention = LSAAttention(self.base_model.num_features)

    def forward(self, x):
        # Base Model의 출력
        base_output = self.base_model.forward_features(x)  # timm 모델의 특징 추출
        
        # Attention을 위해 Query, Key, Value 생성 (기본 모델의 출력을 사용)
        Q = base_output
        K = base_output
        V = base_output

        # LSA 적용
        lsa_output = self.lsa_attention(Q, K, V)
        
        # 출력층 통과 (클래스 예측을 위한 단계)
        final_output = self.base_model.head(lsa_output)
        
        return final_output


class MLP_layer(nn.Module):
    def __init__(self, base_model, out_dim):
        super().__init__()
        self.base_model = base_model
        self.out_dim = out_dim

        self.num_features = self.base_model.base_model.num_features

        # Global Average Pooling Layer 추가
        self.global_avg_pool = nn.AdaptiveAvgPool1d(1)

        # MLP head
        self.mlp_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.num_features, 64),  # 차원을 줄인 후에 입력 크기를 맞춥니다
                nn.ReLU(),
                nn.Linear(64, 1)  # 타겟 차원 5로 설정
            ) for _ in range(out_dim)
        ])

    def forward(self, x):
        base_output = self.base_model(x)
        features = base_output  # (32, 985, 11)

        # Global Average Pooling을 적용하여 985 차원을 제거합니다.
        features = features.permute(0, 2, 1)  # (32, 11, 985)
        features = self.global_avg_pool(features)  # (32, 11, 1)
        features = features.squeeze(-1)  # (32, 11)

        outputs = [head(features) for head in self.mlp_heads]

        return torch.cat(outputs, dim=1)  # (32, 5)






# class MLP_layer(nn.Module):
#     def __init__(self, base_model, out_dim):
#         super().__init__()
#         self.base_model = base_model
#         self.out_dim = out_dim

#         self.num_features = self.base_model.base_model.num_features

#         # MLP head
#         self.mlp_heads = nn.ModuleList([
#             nn.Sequential(
#                 nn.Linear(self.num_features, 64),
#                 nn.ReLU(),
#                 nn.Linear(64, 5)  # 타깃 차원이 5이므로 여기를 5로 설정
#             ) for _ in range(out_dim)
#         ])

#         # Global Average Pooling Layer 추가
#         self.global_avg_pool = nn.AdaptiveAvgPool1d(1)

#     def forward(self, x):
#         base_output = self.base_model(x)
#         features = base_output  # (32, 985, 11)

#         # Global Average Pooling 적용하여 985 차원을 제거
#         features = features.permute(0, 2, 1)  # (32, 11, 985)
#         features = self.global_avg_pool(features)  # (32, 11, 1)
#         features = features.squeeze(-1)  # (32, 11)

#         outputs = [head(features) for head in self.mlp_heads]

#         return torch.cat(outputs, dim=1)  # (32, 5)





def create_model(model_name, pretrained, num_classes, in_chans, out_dim, config):
    if out_dim <= 0:
        raise ValueError("오류: out_dim이 0 이하입니다.")

    # LSA가 적용된 BaseModel 생성
    base_model = BaseModelWithLSA(model_name, pretrained, num_classes, in_chans)
    
    # MLP Layer와 통합
    model = MLP_layer(base_model, out_dim)

    return model
