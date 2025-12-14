"""
Transfer Learning ViT Model for HSI Regression
ImageNet Pretrained 모델을 HSI 6채널로 적응
"""

import torch
import torch.nn as nn
import timm


class ViTTransferRegression(nn.Module):
    """Transfer Learning을 위한 ViT 모델"""

    def __init__(self, model_name='vit_tiny_patch16_224', in_channels=6, num_classes=5,
                 pretrained=True, freeze_backbone=False, dropout=0.3):
        """
        Args:
            model_name: timm 모델 이름
            in_channels: 입력 채널 수 (HSI + RGB)
            num_classes: 출력 클래스 수 (회귀 출력)
            pretrained: ImageNet pretrained 가중치 사용
            freeze_backbone: Backbone 동결 여부
            dropout: Dropout 비율
        """
        super().__init__()

        self.in_channels = in_channels
        self.num_classes = num_classes

        # Timm 모델 로드 (3채널 기본)
        self.model = timm.create_model(
            model_name,
            pretrained=pretrained,
            num_classes=0  # Head 제거 (직접 구현)
        )

        # 첫 Conv/Projection layer를 6채널로 확장
        self._adapt_first_layer()

        # Backbone 동결 옵션
        if freeze_backbone:
            self._freeze_backbone()

        # Feature dimension 추출
        self.feature_dim = self.model.num_features

        # Custom regression head
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(self.feature_dim, self.feature_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout / 2),
            nn.Linear(self.feature_dim // 2, num_classes)
        )

        print(f"Transfer Learning Model: {model_name}")
        print(f"  Pretrained: {pretrained}")
        print(f"  Input channels: {in_channels}")
        print(f"  Feature dim: {self.feature_dim}")
        print(f"  Output classes: {num_classes}")
        print(f"  Freeze backbone: {freeze_backbone}")

    def _adapt_first_layer(self):
        """첫 번째 레이어를 6채널로 확장"""
        # ViT의 patch embedding 확장
        if hasattr(self.model, 'patch_embed'):
            old_proj = self.model.patch_embed.proj

            # 새로운 Conv2d (6채널 입력)
            new_proj = nn.Conv2d(
                self.in_channels,
                old_proj.out_channels,
                kernel_size=old_proj.kernel_size,
                stride=old_proj.stride,
                padding=old_proj.padding,
                bias=old_proj.bias is not None
            )

            # Pretrained 가중치 재사용 (3채널 → 6채널)
            with torch.no_grad():
                # 기존 3채널 가중치를 2번 반복하여 6채널로
                old_weight = old_proj.weight  # (out, 3, k, k)
                # 각 채널 가중치를 절반으로 스케일링하여 합이 동일하게 유지
                new_weight = old_weight.repeat(1, 2, 1, 1) * 0.5
                new_proj.weight.copy_(new_weight)

                if old_proj.bias is not None:
                    new_proj.bias.copy_(old_proj.bias)

            # 교체
            self.model.patch_embed.proj = new_proj
            print("  ✓ Adapted first layer: 3 → 6 channels")
        else:
            raise ValueError("Model structure not supported for channel adaptation")

    def _freeze_backbone(self):
        """Backbone 파라미터 동결"""
        for param in self.model.parameters():
            param.requires_grad = False
        print("  ✓ Backbone frozen")

    def forward(self, x, channel_mask=None):
        """
        Args:
            x: (B, 6, 224, 224)
            channel_mask: (B, 6) - 선택적, 현재 미사용

        Returns:
            (B, num_classes)
        """
        # Feature extraction
        features = self.model(x)  # (B, feature_dim)

        # Regression head
        output = self.head(features)  # (B, num_classes)

        return output


def create_model(config: dict) -> nn.Module:
    """Config에서 Transfer Learning 모델 생성"""
    mcfg = config['model']

    model_name = mcfg.get('timm_model_name', 'vit_tiny_patch16_224')
    in_channels = mcfg.get('in_channels', 6)
    num_classes = mcfg.get('num_classes', 5)
    pretrained = mcfg.get('pretrained', True)
    freeze_backbone = mcfg.get('freeze_backbone', False)
    dropout = mcfg.get('dropout', 0.3)

    return ViTTransferRegression(
        model_name=model_name,
        in_channels=in_channels,
        num_classes=num_classes,
        pretrained=pretrained,
        freeze_backbone=freeze_backbone,
        dropout=dropout
    )


if __name__ == "__main__":
    # 테스트
    config = {
        'model': {
            'timm_model_name': 'vit_tiny_patch16_224',
            'in_channels': 6,
            'num_classes': 5,
            'pretrained': True,
            'freeze_backbone': False,
            'dropout': 0.3
        }
    }

    model = create_model(config)

    # 파라미터 수 확인
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print(f"\nModel Parameters:")
    print(f"  Total: {total_params:,}")
    print(f"  Trainable: {trainable_params:,}")

    # Forward test
    x = torch.randn(4, 6, 224, 224)
    y = model(x)
    print(f"\nForward test:")
    print(f"  Input: {x.shape}")
    print(f"  Output: {y.shape}")
