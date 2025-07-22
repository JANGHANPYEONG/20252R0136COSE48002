import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any
import json

# Spatial and Spectral Attention Modules

# SeAM: Spectral Attention Module
# 분류에 유용한 밴드(파장)를 선택하는 모듈
# 다만, 우리의 입력 데이터는 이미 밴드가 선별되어 오기 때문에, on/off 하며 실험 필요
class SeAM(nn.Module):
    def __init__(self, channels, reduction=8):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1) # 출력의 크기를 1x1로 조정
        self.max_pool = nn.AdaptiveMaxPool2d(1) # 출력의 크기를 1x1로 조정

        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False), # 첫 번째 FC 레이어
            nn.ReLU(), # 활성화 함수
            nn.Linear(channels // reduction, channels, bias=False) # 두 번째 FC 레이어
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        b, c, _, _ = x.size()  # 입력 텐서 x: (B, C, H, W), 여기서 C는 spectral band 수
        avg_out = self.fc(self.avg_pool(x).view(b, c))  # Pavg_se
        max_out = self.fc(self.max_pool(x).view(b, c))  # Pmax_se
        out = avg_out + max_out  # 두 결과를 더해 밴드별 중요도 벡터 생성, Pse 전 Sigmoid
        scale = self.sigmoid(out).view(b, c, 1, 1) # sigmoid를 통해 0~1 정규화된 중요도 벡터 Pse 생성
        return x * scale # 입력에 밴드별 중요도 적용: y'' = x * Pse

# SaAM: Spatial Attention Module
# 공간적 중요도를 강조하는 모듈
class SaAM(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size=7, padding=3)
        self.sigmoid = nn.Sigmoid()

    # SeAM에서는 전체 공간 영역 (H, W)을 평균/최대해서 채널별 정보만을 남기는 것이 목적이지만, 
    # SaAM에서는 각 공간 위치 (H, W)에서의 중요도를 계산하여 강조하는 것이 목적이므로,
    # mean, max method을 사용하여 공간적 중요도를 계산합니다.
    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True) # dim=1은 채널 차원(C)을 평균/최대로 줄이는 것
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        combined = torch.cat([avg_out, max_out], dim=1)
        attention = self.sigmoid(self.conv(combined))
        return x * attention

# Spectral-Spatial Attention Network (SSANet)
# This combines SeAM and SaAM for HSI data
# 최종 결과로는 (n, h, h, k) 형태의 텐서를 반환, k는 attention 및 1x1 conv 이후 유지되는 밴드 수
class SpectralSpatialAttention(nn.Module):
    """
    This combines SeAM and SaAM for HSI data

    최종 결과로는 (n, h, h, k) 형태의 텐서를 반환, 
    k는 attention 및 1x1 conv 이후 유지되는 밴드 수
    """

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.se = SeAM(in_channels)
        self.sa = SaAM()
        self.reduce = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        x = self.se(x)
        x = self.sa(x)
        x = self.reduce(x)
        return x

# [270722] 코드 수정중
# Patchify and Position Embedding
class PatchifyPositionEmbedding(nn.Module):
    """
    (h, h, k) 형태의 입력을 (p, p) 크기의 patch로 분할
    
    전체 데이터의 형태: (N, D)
    N: 패치의 수 == h x h / p x p, D: 각 시퀀스 벡터의 차원의 수 = p x p x k
    
    각 patch (p, p, k)를 1차원 벡터로 flatten하고, 
    위치 임베딩 및 분류를 위한 class token을 추가 정리하면,
    ViT 방식을 차용하여 패치 분할 -> 벡터 평탄화 -> 클래스 토큰 추가 -> 위치 임베딩 추가
    
    최종적으로 transformer에 입력되는 텐서는 (batchsize, N + 1, D) 형태
    """
    def __init__(self, patch_size: int, in_channels: int, embed_dim: int, image_size: int):
        super().__init__()
        self.patch_size = patch_size
        self.embed_dim = embed_dim
        self.num_patches = (image_size // patch_size) ** 2

        self.proj = nn.Conv2d(in_channels, embed_dim, kernel_size=patch_size, stride=patch_size)
        self.cls_token = nn.Parameter(torch.randn(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.randn(1, self.num_patches + 1, embed_dim))

    def forward(self, x):
        # x: (B, C, H, W)
        B = x.size(0)
        x = self.proj(x)  # (B, embed_dim, H//p, W//p)
        x = x.flatten(2).transpose(1, 2)  # (B, N, D)

        cls_tokens = self.cls_token.expand(B, -1, -1)  # (B, 1, D)
        x = torch.cat((cls_tokens, x), dim=1)  # (B, N+1, D)
        x = x + self.pos_embed  # 위치 임베딩 추가
        return x

# [270722] 코드 수정중
# input -> Norm -> Multi-Head Attention -> Norm -> Feed Forward -> Output
# FFC(input) = FC(activation_function(FC(input)))
class TransformerEncoderBlock(nn.Module):
    def __init__(self, dim: int, num_heads: int, mlp_ratio=4.0, dropout=0.1):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(embed_dim=dim, num_heads=num_heads, batch_first=True)

        self.norm2 = nn.LayerNorm(dim)
        self.ffn = nn.Sequential(
            nn.Linear(dim, int(dim * mlp_ratio)),
            nn.GELU(),  # σ: GeLU 함수
            nn.Linear(int(dim * mlp_ratio), dim)
        )

        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # Multi-head Self-Attention with Residual Connection
        x_res = x
        x = self.norm1(x)
        x, _ = self.attn(x, x, x)
        x = x_res + self.dropout(x)

        # Feed Forward Network with Residual Connection
        x_res = x
        x = self.norm2(x)
        x = x_res + self.dropout(self.ffn(x))
        return x

# [270722] 코드 수정중
# HSI SSANet Model
# main model class that uses the SpectralSpatialAttention module
class HSI_SSANet(nn.Module):
    def __init__(self, in_channels, num_classes):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes

        self.ssa = SpectralSpatialAttention(in_channels, out_channels=30)
        self.flatten = nn.Flatten(start_dim=2)
        self.classifier = nn.Sequential(
            nn.Linear(30 * 15 * 15, 256),  # assuming input patch is 15x15
            nn.ReLU(),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        # x: (B, C, H, W) 형태라고 가정
        x = self.ssa(x)
        x = self.flatten(x)
        x = self.classifier(x)
        return x

# [270722] 코드 수정중
def create_model(config: Dict[str, Any]) -> HSI_SSANet:
    column_config_path = config['data']['column_config']
    with open(column_config_path, 'r') as f:
        column_config = json.load(f)

    in_channels = len(column_config['wavelengths'])
    num_classes = config['model']['num_classes']

    print(f"Creating HSI SSANet model:")
    print(f"  Input channels (wavelengths): {in_channels}")
    print(f"  Number of classes: {num_classes}")

    model = HSI_SSANet(in_channels=in_channels, num_classes=num_classes)
    return model

# [270722] 코드 수정중
def get_model_info(model: HSI_SSANet) -> Dict[str, Any]:
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    return {
        'total_parameters': total_params,
        'trainable_parameters': trainable_params,
        'input_channels': model.in_channels,
        'num_classes': model.num_classes
    }
