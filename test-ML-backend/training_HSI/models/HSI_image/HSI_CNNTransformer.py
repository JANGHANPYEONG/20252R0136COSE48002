import torch
import torch.nn as nn
import torch.nn.functional as F
import math

# 개선된 SEBlock (Squeeze-and-Excitation)
class SEBlock(nn.Module):
    def __init__(self, ch, reduction=16):  # reduction을 8에서 16으로 변경하여 더 효율적
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(ch, ch // reduction),
            nn.ReLU(inplace=True),
            nn.Dropout(0.1),  # 드롭아웃 추가
            nn.Linear(ch // reduction, ch),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y

# CBAM (Convolutional Block Attention Module) 추가
class CBAM(nn.Module):
    def __init__(self, ch, reduction=16, kernel_size=7):
        super().__init__()
        self.channel_attention = ChannelAttention(ch, reduction)
        self.spatial_attention = SpatialAttention(kernel_size)
    
    def forward(self, x):
        x = self.channel_attention(x) * x
        x = self.spatial_attention(x) * x
        return x

class ChannelAttention(nn.Module):
    def __init__(self, ch, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(ch, ch // reduction),
            nn.ReLU(inplace=True),
            nn.Linear(ch // reduction, ch)
        )
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        b, c, _, _ = x.size()
        avg_out = self.fc(self.avg_pool(x).view(b, c))
        max_out = self.fc(self.max_pool(x).view(b, c))
        out = avg_out + max_out
        return self.sigmoid(out).view(b, c, 1, 1)

class SpatialAttention(nn.Module):
    def __init__(self, kernel_size=7):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=kernel_size//2)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        out = torch.cat([avg_out, max_out], dim=1)
        out = self.conv(out)
        return self.sigmoid(out)

# 개선된 CNN Backbone
class CNNBackbone(nn.Module):
    """
    2D CNN 블록: 공간 특징 추출 + 개선된 Attention
    입력: (batch, B, H, W) 형태의 하이퍼스펙트럴 이미지
    출력: (batch, C_last, H', W') 형태의 특징 맵
    """
    def __init__(self, in_channels, channels=[32, 64, 128], use_pool=True, attention_type='se'):
        super().__init__()
        layers = []
        prev_ch = in_channels   
        
        for i, ch in enumerate(channels):
            # ResNet 스타일의 residual connection 추가
            if i > 0 and prev_ch == ch:
                layers.append(ResidualBlock(prev_ch, ch, attention_type))
            else:
                layers.append(nn.Conv2d(prev_ch, ch, kernel_size=3, padding=1))
                layers.append(nn.BatchNorm2d(ch))
                layers.append(nn.ReLU(inplace=True))
                
                # Attention 메커니즘 선택
                if attention_type == 'se':
                    layers.append(SEBlock(ch, reduction=16))
                elif attention_type == 'cbam':
                    layers.append(CBAM(ch, reduction=16))
                elif attention_type == 'both':
                    layers.append(SEBlock(ch, reduction=16))
                    layers.append(CBAM(ch, reduction=16))
                
                if use_pool:
                    layers.append(nn.MaxPool2d(2, 2))
            
            prev_ch = ch
        
        self.cnn = nn.Sequential(*layers)
        self._init_weights()

    def _init_weights(self):
        for m in self.cnn:
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        return self.cnn(x)

# Residual Block 추가
class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, attention_type='se'):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # Attention 메커니즘
        if attention_type == 'se':
            self.attention = SEBlock(out_channels, reduction=16)
        elif attention_type == 'cbam':
            self.attention = CBAM(out_channels, reduction=16)
        else:
            self.attention = nn.Identity()
        
        self.relu = nn.ReLU(inplace=True)
        
        # Skip connection
        if in_channels != out_channels:
            self.shortcut = nn.Conv2d(in_channels, out_channels, kernel_size=1)
        else:
            self.shortcut = nn.Identity()
    
    def forward(self, x):
        residual = self.shortcut(x)
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.attention(out)
        
        out += residual
        out = self.relu(out)
        
        return out

# 개선된 MultiTaskHead
class MultiTaskHead(nn.Module):
    """
    멀티태스크 헤드: 분류 + 회귀 (개선된 버전)
    """
    def __init__(self, feature_dim, num_classes, num_regression_targets=0, dropout=0.3):
        super().__init__()
        
        # 분류 헤드 개선
        self.classification_head = nn.Sequential(
            nn.Linear(feature_dim, feature_dim),
            nn.LayerNorm(feature_dim),  # LayerNorm 추가
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(feature_dim, feature_dim // 2),
            nn.LayerNorm(feature_dim // 2),  # LayerNorm 추가
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(feature_dim // 2, num_classes)
        )
        
        if num_regression_targets > 0:
            self.regression_head = nn.Sequential(
                nn.Linear(feature_dim, feature_dim),
                nn.LayerNorm(feature_dim),  # LayerNorm 추가
                nn.ReLU(inplace=True),
                nn.Dropout(dropout),
                nn.Linear(feature_dim, feature_dim // 2),
                nn.LayerNorm(feature_dim // 2),  # LayerNorm 추가
                nn.ReLU(inplace=True),
                nn.Dropout(dropout),
                nn.Linear(feature_dim // 2, num_regression_targets)
            )
        else:
            self.regression_head = None
            
        self._init_weights()

    def _init_weights(self):
        for m in self.classification_head:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)
        if self.regression_head:
            for m in self.regression_head:
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight)
                    nn.init.zeros_(m.bias)

    def forward(self, x):
        clf = self.classification_head(x)
        if self.regression_head:
            reg = self.regression_head(x)
            return clf, reg
        return clf

# 개선된 Transformer Encoder Layer
class ImprovedTransformerEncoderLayer(nn.TransformerEncoderLayer):
    def __init__(self, d_model, nhead, dim_feedforward=2048, dropout=0.1, activation='gelu'):
        super().__init__(d_model, nhead, dim_feedforward, dropout, activation)
        
        # Pre-norm 구조로 변경
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        # 추가적인 정규화
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
    
    def forward(self, src, src_mask=None, src_key_padding_mask=None):
        # Pre-norm 구조
        src2 = self.norm1(src)
        src2 = self.self_attn(src2, src2, src2, attn_mask=src_mask,
                              key_padding_mask=src_key_padding_mask)[0]
        src = src + self.dropout1(src2)
        
        src2 = self.norm2(src)
        src2 = self.linear2(self.dropout(self.activation(self.linear1(src2))))
        src = src + self.dropout2(src2)
        
        return src

# 개선된 CNNTransformerMT 모델
class CNNTransformerMT(nn.Module):
    """
    개선된 모델: 2D CNN + Spectral Transformer + MultiTaskHead
    (성능 최적화 버전: 다양한 attention 메커니즘, residual connection, pre-norm 등)
    """
    def __init__(self,
                 in_bands,
                 cnn_channels=[32, 64, 128],  # 채널 수 증가
                 num_bands=None,
                 token_dim=64,  # 토큰 차원 증가
                 trans_layers=3,  # 레이어 수 증가
                 trans_heads=4,  # 헤드 수 증가
                 trans_ffn_dim=512,  # FFN 차원 증가
                 num_classes=13,
                 num_regression_targets=0,
                 shared_hidden=128,  # 공유 히든 차원 증가
                 use_pool=True,
                 dropout=0.2,  # 드롭아웃 감소
                 attention_type='se',  # attention 타입 선택
                 use_pre_norm=True):  # pre-norm 사용 여부
        super().__init__()
        num_bands = num_bands or in_bands

        # CNN Backbone (개선된 attention 적용)
        self.backbone = CNNBackbone(in_bands, cnn_channels, use_pool, attention_type)

        C = cnn_channels[-1]
        # 밴드별 토큰화: 1x1 Conv로 C -> (num_bands * token_dim)
        self.band_proj = nn.Conv2d(C, num_bands * token_dim, kernel_size=1)
        self.num_bands = num_bands

        # [cls] 토큰 정의 추가
        self.cls_token = nn.Parameter(torch.randn(1, 1, token_dim))
        self.pos_emb = nn.Parameter(torch.randn(1, num_bands + 1, token_dim))

        # 개선된 Transformer
        if use_pre_norm:
            encoder_layer = ImprovedTransformerEncoderLayer(
                d_model=token_dim,
                nhead=trans_heads,
                dim_feedforward=trans_ffn_dim,
                batch_first=True,
                dropout=dropout,
                activation='gelu'
            )
        else:
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=token_dim,
                nhead=trans_heads,
                dim_feedforward=trans_ffn_dim,
                batch_first=True,
                dropout=dropout,
                activation='gelu'
            )
        
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=trans_layers)

        # 개선된 shared hidden layer
        self.shared_layer = nn.Sequential(
            nn.Linear(token_dim, shared_hidden),
            nn.LayerNorm(shared_hidden),  # LayerNorm 추가
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(shared_hidden, shared_hidden),
            nn.LayerNorm(shared_hidden),  # LayerNorm 추가
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )

        self.head = MultiTaskHead(shared_hidden, num_classes, num_regression_targets, dropout=dropout)

        self._init_weights()

    def _init_weights(self):
        # 가중치 초기화 개선
        nn.init.normal_(self.pos_emb, std=0.02)
        nn.init.xavier_uniform_(self.band_proj.weight)
        if self.band_proj.bias is not None:
            nn.init.zeros_(self.band_proj.bias)
        
        # CLS 토큰 초기화
        nn.init.normal_(self.cls_token, std=0.02)

    def forward(self, x):
        # x: (batch, B, H, W)
        feat = self.backbone(x)
        bp = self.band_proj(feat).mean(dim=[2, 3])  # (B, B*token_dim)
        b = bp.size(0)
        tokens = bp.view(b, self.num_bands, -1)    # (B, num_bands, token_dim)

        # Prepend CLS token
        cls = self.cls_token.expand(b, -1, -1)     # (B,1,token_dim)
        tokens = torch.cat([cls, tokens], dim=1)   # (B,num_bands+1,token_dim)
        tokens = tokens + self.pos_emb             # Add positional embedding

        # Transformer
        trans = self.transformer(tokens)           # (B,num_bands+1,token_dim)

        # Extract CLS representation and pass through shared layer
        cls_rep = trans[:, 0, :]                   # (B, token_dim)
        shared = self.shared_layer(cls_rep)        # (B, shared_hidden)

        # Head
        return self.head(shared)


def create_model(config: dict) -> nn.Module:
    mcfg = config['model']
    return CNNTransformerMT(
        in_bands=mcfg['in_bands'],
        cnn_channels=mcfg.get('cnn_channels', [32, 64, 128]),  # 기본값 개선
        num_bands=mcfg.get('num_bands', None),
        token_dim=mcfg.get('token_dim', 64),  # 기본값 증가
        trans_layers=mcfg.get('trans_layers', 3),  # 기본값 증가
        trans_heads=mcfg.get('trans_heads', 4),  # 기본값 증가
        trans_ffn_dim=mcfg.get('trans_ffn_dim', 512),  # 기본값 증가
        num_classes=mcfg['num_classes'],
        num_regression_targets=mcfg.get('num_regression_targets', 0),
        shared_hidden=mcfg.get('shared_hidden', 128),  # 기본값 증가
        use_pool=mcfg.get('use_pool', True),
        dropout=mcfg.get('dropout', 0.2),  # 기본값 감소
        attention_type=mcfg.get('attention_type', 'se'),  # 새로운 옵션
        use_pre_norm=mcfg.get('use_pre_norm', True)  # 새로운 옵션
    )


def get_model_info(model):
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return {
        'total_parameters': total_params,
        'trainable_parameters': trainable_params
    }
