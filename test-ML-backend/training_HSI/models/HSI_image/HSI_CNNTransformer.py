import torch
import torch.nn as nn

class CNNBackbone(nn.Module):
    '''
    2D CNN 블록: 공간 특징 추출
    입력: (batch, B, H, W) 형태의 하이퍼스펙트럴 이미지
    출력: (batch, C_last, H', W') 형태의 특징 맵
    '''
    def __init__(self, in_channels, channels=[32, 64, 128], use_pool=True):
        super().__init__()
        layers = []
        prev_ch = in_channels
        for ch in channels:
            layers.append(nn.Conv2d(prev_ch, ch, kernel_size=3, padding=1))
            layers.append(nn.ReLU(inplace=True))
            if use_pool:
                layers.append(nn.MaxPool2d(2, 2))
            prev_ch = ch
        self.cnn = nn.Sequential(*layers)

    def forward(self, x):
        return self.cnn(x)


class MultiTaskHead(nn.Module):
    '''
    멀티태스크 헤드: 분류 + 회귀
    '''
    def __init__(self, feature_dim, num_classes, num_regression_targets=0):
        super().__init__()
        # 분류 헤드
        self.classification_head = nn.Sequential(
            nn.Linear(feature_dim, feature_dim//2),
            nn.ReLU(inplace=True),
            nn.Linear(feature_dim//2, num_classes)
        )
        # 회귀 헤드
        if num_regression_targets > 0:
            self.regression_head = nn.Sequential(
                nn.Linear(feature_dim, feature_dim//2),
                nn.ReLU(inplace=True),
                nn.Linear(feature_dim//2, num_regression_targets)
            )
        else:
            self.regression_head = None

    def forward(self, x):
        clf = torch.sigmoid(self.classification_head(x))
        if self.regression_head:
            reg = self.regression_head(x)
            return {'classification': clf, 'regression': reg}
        else:
            return clf   # dict 대신 (batch, num_classes) Tensor만 반환


class CNNTransformerMT(nn.Module):
    '''
    수정된 모델: 2D CNN + Spectral Transformer + MultiTaskHead
    '''
    def __init__(self,
                 in_bands,
                 cnn_channels=[32, 64, 128],
                 num_bands=10,
                 token_dim=64,
                 trans_layers=6,
                 trans_heads=4,
                 trans_ffn_dim=1024,
                 num_classes=13,
                 num_regression_targets=0,
                 shared_hidden=128,
                 use_pool=True):
        super().__init__()
        # CNN Backbone
        self.backbone = CNNBackbone(in_bands, cnn_channels, use_pool)
        # 채널 차원
        C = cnn_channels[-1]
        # 글로벌 풀링 -> 토큰화
        self.global_pool = nn.AdaptiveAvgPool2d((1,1))
        self.project = nn.Linear(C, token_dim)
        self.pos_emb = nn.Parameter(torch.randn(1, num_bands, token_dim))
        self.num_bands = num_bands
        # Transformer
        encoder = nn.TransformerEncoderLayer(d_model=token_dim, nhead=trans_heads,
                                            dim_feedforward=trans_ffn_dim, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder, num_layers=trans_layers)
        # 최종 pooling 후 MultiTaskHead
        self.pool1d = nn.AdaptiveAvgPool1d(1)
        self.head = MultiTaskHead(token_dim, num_classes, num_regression_targets)

    def forward(self, x):
        # x: (batch, B, H, W)
        feat = self.backbone(x)  # (batch, C, H', W')
        b, c, h, w = feat.shape
        pooled = self.global_pool(feat).view(b, c)  # (batch, C)
        tok = self.project(pooled)  # (batch, d)
        tokens = tok.unsqueeze(1).expand(-1, self.num_bands, -1) + self.pos_emb
        trans = self.transformer(tokens)  # (batch, B, d)
        combined = self.pool1d(trans.transpose(1,2)).squeeze(-1)  # (batch, d)
        return self.head(combined)



def create_model(config: dict) -> nn.Module:
    '''
    학습 스크립트에서 호출하는 팩토리 함수
    Args:
        config (dict): 전체 설정 딕셔너리
    Returns:
        nn.Module: 모델 인스턴스
    '''
    mcfg = config['model']
    return CNNTransformerMT(
        in_bands=mcfg['in_bands'],
        cnn_channels=mcfg.get('cnn_channels', [32, 64, 128]),
        num_bands=mcfg.get('num_bands', mcfg['in_bands']),
        token_dim=mcfg.get('token_dim', 64),
        trans_layers=mcfg.get('trans_layers', 6),
        trans_heads=mcfg.get('trans_heads', 4),
        trans_ffn_dim=mcfg.get('trans_ffn_dim', 1024),
        num_classes=mcfg['num_classes'],
        num_regression_targets=mcfg.get('num_regression_targets', 0),
        use_pool=mcfg.get('use_pool', True)
    )


def get_model_info(model):
    '''
    모델 정보 요약 반환
    '''
    total_params = sum(p.numel() for p in model.parameters())
    return {'total_parameters': total_params}