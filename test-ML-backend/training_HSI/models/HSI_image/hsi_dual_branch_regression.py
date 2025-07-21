import torch
import torch.nn as nn

def conv_block(in_channels, out_channels, kernel_size=3, stride=1, padding=1, dropout=0.0):
    """기본 Conv-BN-ReLU 블록"""
    return nn.Sequential(
        nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, bias=False),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True),
        nn.Dropout2d(dropout)
    )

class DualBranchHSICNN(nn.Module):
    def __init__(self, in_channels, num_classes, num_regression_targets, base_channels=32, depth=3, dropout=0.2):
        """
        2D CNN 기반 Dual Branch HSI 모델
        Args:
            in_channels (int): HSI 이미지의 채널 수 (= 선택된 밴드 수)
            num_classes (int): 분류 클래스 수 (0이면 비활성화됨)
            num_regression_targets (int): 회귀 타겟 수
            base_channels (int): 첫 번째 conv 채널 수
            depth (int): CNN 깊이
            dropout (float): Dropout 비율
        """
        super().__init__()

        # 공유 이미지 feature extractor (Shared encoder)
        layers = [conv_block(in_channels, base_channels, dropout=dropout)]
        channels = base_channels
        for _ in range(1, depth):
            layers.append(conv_block(channels, channels * 2, dropout=dropout))
            channels *= 2
        self.encoder = nn.Sequential(*layers)

        self.pool = nn.AdaptiveAvgPool2d((1, 1))  # 출력: (B, C, 1, 1)
        feature_dim = channels

        # 회귀 헤드 (항상 사용)
        self.regressor = nn.Sequential(
            nn.Linear(feature_dim, feature_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(feature_dim // 2, num_regression_targets)
        )

        # 분류 헤드 (클래스 수 > 0일 때만)
        self.classifier = None
        if num_classes > 0:
            self.classifier = nn.Sequential(
                nn.Linear(feature_dim, feature_dim // 2),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(feature_dim // 2, num_classes)
            )

    def forward(self, x):
        """
        Args:
            x (Tensor): 입력 이미지 텐서 (B, C, H, W)
        Returns:
            dict: {"classification": ..., "regression": ...}
        """
        feat = self.encoder(x)         # (B, C, H, W)
        feat = self.pool(feat)         # (B, C, 1, 1)
        feat = feat.view(feat.size(0), -1)  # (B, C)

        reg_out = self.regressor(feat)
        cls_out = self.classifier(feat) if self.classifier else torch.empty(x.size(0), 0, device=x.device)

        return {
            "classification": cls_out,
            "regression": reg_out
        }

def create_model(config):
    """
    파이프라인 연동용 모델 생성 함수
    Args:
        config (dict): 전체 설정 딕셔너리
    Returns:
        nn.Module: 학습 가능한 모델
    """
    model_cfg = config["model"]
    in_channels = model_cfg.get("in_channels", 6)
    num_classes = model_cfg.get("num_classes", 0)
    num_regression_targets = model_cfg.get("num_regression_targets", 6)
    base_channels = model_cfg.get("base_channels", 32)
    depth = model_cfg.get("depth", 3)
    dropout = model_cfg.get("dropout", 0.2)

    return DualBranchHSICNN(
        in_channels=in_channels,
        num_classes=num_classes,
        num_regression_targets=num_regression_targets,
        base_channels=base_channels,
        depth=depth,
        dropout=dropout
    )
