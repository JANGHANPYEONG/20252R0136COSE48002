import torch
import torch.nn as nn
import math

class CNNBackbone(nn.Module):
    """
    2D CNN 블록: 공간 특징 추출
    입력: (batch, B, H, W) 형태의 하이퍼스펙트럴 이미지
    출력: (batch, C_last, H', W') 형태의 특징 맵
    """
    def __init__(self, in_channels, channels=[32, 64, 128], use_pool=True):
        super().__init__()
        layers = []
        prev_ch = in_channels   
        for ch in channels:
            layers.append(nn.Conv2d(prev_ch, ch, kernel_size=3, padding=1))
            layers.append(nn.BatchNorm2d(ch))
            layers.append(nn.ReLU(inplace=True))
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

    def forward(self, x):
        return self.cnn(x)


class MultiTaskHead(nn.Module):
    """
    멀티태스크 헤드: 분류 + 회귀
    """
    def __init__(self, feature_dim, num_classes, num_regression_targets=0, dropout=0.3):
        super().__init__()
        self.classification_head = nn.Sequential(
            nn.Linear(feature_dim, feature_dim // 2),
            nn.ReLU(inplace=True),
            nn.Identity(),
            nn.Linear(feature_dim // 2, num_classes)
        )
        if num_regression_targets > 0:
            self.regression_head = nn.Sequential(
                nn.Linear(feature_dim, feature_dim // 2),
                nn.ReLU(inplace=True),
                nn.Identity(),
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


class CNNTransformerMT(nn.Module):
    """
    수정된 모델: 2D CNN + Spectral Transformer + MultiTaskHead
    """
    def __init__(self,
                 in_bands,
                 cnn_channels=[32, 64, 128],
                 num_bands=None,
                 token_dim=64,
                 trans_layers=6,
                 trans_heads=4,
                 trans_ffn_dim=1024,
                 num_classes=13,
                 num_regression_targets=0,
                 shared_hidden=128,
                 use_pool=True,
                 dropout=0.1):
        super().__init__()
        num_bands = num_bands or in_bands

        # CNN Backbone
        self.backbone = CNNBackbone(in_bands, cnn_channels, use_pool)

        C = cnn_channels[-1]
        # 밴드별 토큰화: 1x1 Conv로 C -> (num_bands * token_dim)
        self.band_proj = nn.Conv2d(C, num_bands * token_dim, kernel_size=1)
        self.num_bands = num_bands

        # [cls] 토큰 정의 추가
        # (num_bands+1, d)
        self.cls_token = nn.Parameter(torch.randn(1, 1, token_dim))
        self.pos_emb = nn.Parameter(torch.randn(1, num_bands + 1, token_dim))

        # Transformer
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=token_dim,
            nhead=trans_heads,
            dim_feedforward=trans_ffn_dim,
            batch_first=True,
            dropout=dropout,
            activation='gelu'
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=trans_layers)

        # shared hidden layer
        self.shared_layer = nn.Sequential(
            nn.Linear(token_dim, shared_hidden),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )


        self.head = MultiTaskHead(shared_hidden, num_classes, num_regression_targets, dropout=dropout)

        self._init_weights()

    def _init_weights(self):
        nn.init.normal_(self.pos_emb, std=0.02)
        nn.init.xavier_uniform_(self.band_proj.weight)
        if self.band_proj.bias is not None:
            nn.init.zeros_(self.band_proj.bias)

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
        cnn_channels=mcfg.get('cnn_channels', [32, 64, 128]),
        num_bands=mcfg.get('num_bands', None),
        token_dim=mcfg.get('token_dim', 64),
        trans_layers=mcfg.get('trans_layers', 6),
        trans_heads=mcfg.get('trans_heads', 4),
        trans_ffn_dim=mcfg.get('trans_ffn_dim', 1024),
        num_classes=mcfg['num_classes'],
        num_regression_targets=mcfg.get('num_regression_targets', 0),
        use_pool=mcfg.get('use_pool', True),
        dropout=mcfg.get('dropout', 0.1)
    )


def get_model_info(model):
    total_params = sum(p.numel() for p in model.parameters())
    return {'total_parameters': total_params}
