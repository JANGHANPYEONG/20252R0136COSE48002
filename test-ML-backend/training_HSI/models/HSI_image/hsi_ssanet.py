import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any
import json

# Spatial and Spectral Attention Modules

# SeAM: Spectral Attention Module
# 분류에 유용한 밴드(파장)를 선택하는 모듈
# 다만, 우리의 입력 데이터는 이미 밴드가 선별되어 오기 때문에, on/off 하며 실험 필요
# Input : (B, C, H, W)
# Output: (B, C, H, W)
class SeAM(nn.Module):
    def __init__(self, channels, reduction):
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
# Input : (B, C, H, W)
# Output: (B, C, H, W)

class SaAM(nn.Module):
    def __init__(self, kernel_size: int, padding: int):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size=kernel_size, padding=padding)
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
        self.patch_size = patch_size # 패치 크기
        self.embed_dim = embed_dim # 각 patch를 flatten한 후 transformer에 입력되는 벡터의 차원
        self.num_patches = (image_size // patch_size) ** 2 # image_size는 입력 이미지 한 변의 길이, patch_size는 각 패치의 크기

        self.proj = nn.Conv2d(in_channels, embed_dim, kernel_size=patch_size, stride=patch_size)
        self.cls_token = nn.Parameter(torch.randn(1, 1, embed_dim)) # class token
        self.pos_embed = nn.Parameter(torch.randn(1, self.num_patches + 1, embed_dim)) # 위치 임베딩

    def forward(self, x):
        # x: (B, C, H, W)
        B = x.size(0)
        x = self.proj(x)  # (B, embed_dim, H//p, W//p)
        x = x.flatten(2).transpose(1, 2)  # (B, N, D)

        cls_tokens = self.cls_token.expand(B, -1, -1)  # (B, 1, D)
        x = torch.cat((cls_tokens, x), dim=1)  # (B, N+1, D)
        x = x + self.pos_embed  # 위치 임베딩 추가
        return x

# input -> Norm -> Multi-Head Attention -> Norm -> Feed Forward -> Output
# FFC(input) = FC(activation_function(FC(input)))
class TransformerEncoderBlock(nn.Module):
    def __init__(self, dim: int, num_heads: int, mlp_ratio: float, dropout: float):
        super().__init__()
        # dim: 각 토큰 벡터가 가지는 차원, 입력 차원의 크기
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(embed_dim=dim, num_heads=num_heads, batch_first=True)

        self.norm2 = nn.LayerNorm(dim)
        self.ffn = nn.Sequential(
            nn.Linear(dim, int(dim * mlp_ratio)),
            nn.GELU(),  # activation: GeLU 함수
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

class DenseTransformer(nn.Module):
    def __init__(self, block_cls, num_layers, dim, heads, mlp_ratio, dropout):
        super().__init__()
        self.blocks = nn.ModuleList([
            block_cls(dim, heads, mlp_ratio, dropout) for _ in range(num_layers)
        ])
        # concat으로 차원이 늘어나므로 다시 dim으로 줄이는 프로젝션 레이어
        self.projs = nn.ModuleList([
            nn.Linear(dim * (i + 1), dim) for i in range(num_layers)
        ])

    def forward(self, x):
        feats = [x]           # x: (B, N+1, D)
        out = x
        for i, blk in enumerate(self.blocks):
            out = blk(out)    # (B, N+1, D)
            feats.append(out) # 누적
            cat = torch.cat(feats[1:], dim=-1)  # 첫 입력 제외하고 concat (B, N+1, D * (i+1))
            out = self.projs[i](cat)            # (B, N+1, D)로 압축
        return out

# [250731] branch attention
# 병렬 처리니까 따로 처리 후 마지막에 concat 하면 될거 같음.
class Branch_Attention(nn.Module):
    def __init__(self, channels: int, reduction: int, kernel_size: int, padding: int):
        super().__init__()
        # SeAM
        self.avg_pool = nn.AdaptiveAvgPool2d(1) # 출력의 크기를 1x1로 조정
        self.max_pool = nn.AdaptiveMaxPool2d(1) # 출력의 크기를 1x1로 조정

        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False), # 첫 번째 FC 레이어
            nn.ReLU(), # 활성화 함수
            nn.Linear(channels // reduction, channels, bias=False) # 두 번째 FC 레이어
        )
        self.sigmoid = nn.Sigmoid()

        # SaAM
        self.conv = nn.Conv2d(2, 1, kernel_size=kernel_size, padding=padding)
        self.sigmoid = nn.Sigmoid()

        # 1x1 conv로 다시 (B, C, H, W)로 축소
        self.reduce = nn.Conv2d(channels * 2, channels, kernel_size=1)

        # MLP based fusion
        self.fusion_mlp = nn.Sequential(
            nn.Conv2d(channels * 2, channels, kernel_size=1),
            nn.ReLU(),
            nn.Conv2d(channels * 2, channels, kernel_size=1)
        )

    def forward(self, x):
        # SeAM
        SeAM_x = x
        b, c, _, _ = x.size()  # 입력 텐서 x: (B, C, H, W), 여기서 C는 spectral band 수
        avg_out = self.fc(self.avg_pool(SeAM_x).view(b, c))
        max_out = self.fc(self.max_pool(SeAM_x).view(b, c))
        out = avg_out + max_out  # 두 결과를 더해 밴드별 중요도 벡터 생성
        scale = self.sigmoid(out).view(b, c, 1, 1)
        res_SeAM = SeAM_x * scale  # 입력에 밴드별 중요도 적용: y'' = x * Pse

        # SaAM
        SaAM_x = x
        avg_out = torch.mean(SaAM_x, dim=1, keepdim=True) # dim=1은 채널 차원(C)을 평균/최대로 줄이는 것
        max_out, _ = torch.max(SaAM_x, dim=1, keepdim=True)
        combined = torch.cat([avg_out, max_out], dim=1)
        attention = self.sigmoid(self.conv(combined))
        res_SaAM = SaAM_x * attention  # 공간적 중요도 적용

        # [250805] branch attention comment
        # concat 및 축소 method를 유의미한 방법으로 변경할 필요가 있어보임
        # 현재의 단순한 concat은 채널 차원을 단순히 늘리는 것에 불과함
        # 또한, 현재의 reduce는 단순히 1x1 conv로 채널 차원을 줄이는 것

        # 채널 차원 concat: (B, 2C, H, W)
        res = torch.cat([res_SeAM, res_SaAM], dim=1)

        # 1x1 conv로 다시 (B, C, H, W)로 축소
        # res = self.reduce(res)

        # [250806] MLP based fusion
        res = self.fusion_mlp(res)  # MLP based fusion

        return res  # (B, C, H, W)
        

# Spectral-Spatial Attention Network (SSANet)
# This combines SeAM and SaAM for HSI data
# 최종 결과로는 (n, h, h, k) 형태의 텐서를 반환, k는 attention 및 1x1 conv 이후 유지되는 밴드 수
# SeAM_use와 SaAM_use는 각각 SeAM과 SaAM을 사용할지 여부를 결정하는 파라미터
class SpectralSpatialAttention(nn.Module):
    """
    This combines SeAM and SaAM for HSI data

    최종 결과로는 (n, h, h, k) 형태의 텐서를 반환, 
    k는 attention 및 1x1 conv 이후 유지되는 밴드 수
    """

    def __init__(self, in_channels, out_channels, kernel_size, 
                 SeAM_reduction, SaAM_kernel_size, SaAM_padding,
                 SeAM_use, SaAM_use, branch_mode):
        super().__init__()
        self.se = SeAM(in_channels, SeAM_reduction)
        self.sa = SaAM(kernel_size=SaAM_kernel_size, padding=SaAM_padding)
        self.reduce = nn.Conv2d(in_channels, out_channels, kernel_size=1)
        self.SeAM_use = SeAM_use
        self.SaAM_use = SaAM_use
        # branch attention
        self.branch_mode = branch_mode
        self.branch_attention = Branch_Attention(in_channels, SeAM_reduction, kernel_size=SaAM_kernel_size, padding=SaAM_padding)

    def forward(self, x):
        if not self.branch_mode:  # branch 사용하지 않을 경우
            if self.SeAM_use:
                x = self.se(x)
            if self.SaAM_use:
                x = self.sa(x)
            # x = self.reduce(x)
        else:  # branch 사용할 경우
            x = self.branch_attention(x)
        
        # PatchifyPositionEmbedding 입력 크기에 맞게 조정
        x = self.reduce(x) # (SeAM + SaAM) 결과를 1x1 conv로 축소

        return x

# HSI SSANet Model
# main model class that uses the SpectralSpatialAttention module
# HSI_SSANet
class HSI_SSANet(nn.Module):
    def __init__(self, in_channels, num_classes, ssa_out_channels,
                 image_size, patch_size, embed_dim,
                 num_TransformerEncoder_heads, num_TransformerEncoder_layers,
                 transformer_mlp_ratio, transformer_dropout,
                 seam_reduction, saam_kernel_size, saam_padding, ssa_kernel_size,
                 UsingSeAM, UsingSaAM, branch_mode):
        super().__init__()

        self.in_channels = in_channels
        self.num_classes = num_classes

        # 1. SSA module
        self.ssa = SpectralSpatialAttention(
            in_channels=in_channels,
            out_channels=ssa_out_channels,
            kernel_size=ssa_kernel_size,
            SeAM_reduction=seam_reduction,
            SaAM_kernel_size=saam_kernel_size,
            SaAM_padding=saam_padding,
            SeAM_use=UsingSeAM,
            SaAM_use=UsingSaAM,
            branch_mode=branch_mode
        )

        # 2. Patchify + Position Embedding
        self.patch_embed = PatchifyPositionEmbedding(
            patch_size=patch_size,
            in_channels=ssa_out_channels,
            embed_dim=embed_dim,
            image_size=image_size
        )

        # 3. Transformer Encoder Stack
        self.transformer = DenseTransformer(
            block_cls=TransformerEncoderBlock,
            num_layers=num_TransformerEncoder_layers,
            dim=embed_dim,
            heads=num_TransformerEncoder_heads,
            mlp_ratio=transformer_mlp_ratio,
            dropout=transformer_dropout
            )

        # 4. Classification head
        self.classifier = nn.Linear(embed_dim, num_classes)

    def forward(self, x):
        x = self.ssa(x)               # (B, ssa_out_channels, H, W)
        x = self.patch_embed(x)      # (B, N+1, D)
        x = self.transformer(x)      # (B, N+1, D)
        cls_token = x[:, 0]          # (B, D)
        out = self.classifier(cls_token)  # (B, num_classes)
        return out

def create_model(config: Dict[str, Any]) -> HSI_SSANet:
    column_config_path = config['data']['column_config']
    with open(column_config_path, 'r') as f:
        column_config = json.load(f)

    in_channels = len(column_config['wavelengths'])
    model_cfg = config['model']

    # 구성 파라미터 추출
    num_classes = model_cfg['num_classes']
    ssa_out_channels = model_cfg['SeAM']['out_channels']
    ssa_kernel_size = model_cfg['SpectralSpatialAttention']['kernel_size']

    # SSA 세부 파라미터
    seam_reduction = model_cfg['SeAM']['reduction']
    saam_kernel_size = model_cfg['SaAM']['conv_kernel_size']
    saam_padding = model_cfg['SaAM']['conv_padding']

    # Patch + Positional Embedding
    patch_size = model_cfg['PatchPositionEmbedding']['patch_size']
    image_size = model_cfg['PatchPositionEmbedding']['image_size']
    embed_dim = model_cfg['PatchPositionEmbedding']['embed_dim']

    # Transformer
    num_heads = model_cfg['TransformerEncoderBlock']['num_heads']
    mlp_ratio = model_cfg['TransformerEncoderBlock']['mlp_ratio']
    dropout = model_cfg['TransformerEncoderBlock']['dropout']
    num_layers = model_cfg.get('TransformerEncoderBlock').get('num_layers', 1)

    # SeAM, SaAM 사용 여부
    UsingSeAM = model_cfg.get('UsingSeAM', {}).get('use', True)
    UsingSaAM = model_cfg.get('UsingSaAM', {}).get('use', True)

    # Branch mode
    branch_mode = model_cfg.get('BranchAttention', {}).get('use', False)

    model = HSI_SSANet(
        in_channels=in_channels,
        num_classes=num_classes,
        ssa_out_channels=ssa_out_channels,
        image_size=image_size,
        patch_size=patch_size,
        embed_dim=embed_dim,
        num_TransformerEncoder_heads=num_heads,
        num_TransformerEncoder_layers=num_layers,
        transformer_mlp_ratio=mlp_ratio,
        transformer_dropout=dropout,
        seam_reduction=seam_reduction,
        saam_kernel_size=saam_kernel_size,
        saam_padding=saam_padding,
        ssa_kernel_size=ssa_kernel_size,
        UsingSeAM=UsingSeAM,
        UsingSaAM=UsingSaAM,
        branch_mode=branch_mode
    )

    return model

def get_model_info(model: HSI_SSANet) -> Dict[str, Any]:
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    return {
        'total_parameters': total_params,
        'trainable_parameters': trainable_params,
        'input_channels': model.in_channels,
        'num_classes': model.num_classes
    }
