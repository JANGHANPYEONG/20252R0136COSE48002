import timm
import torch
import torch.nn as nn

# Shifted Patch Tokenization(SPT) 레이어 정의
class ShiftedPatchTokenization(nn.Module):
    def __init__(self, patch_size=16, shift_ratio=0.5):
        super(ShiftedPatchTokenization, self).__init__()
        self.patch_size = patch_size
        self.shift_ratio = shift_ratio

    def forward(self, x):
        B, C, H, W = x.size()  # 배치 크기, 채널, 높이, 너비
        shift = int(self.patch_size * self.shift_ratio)

        # 입력 이미지를 다양한 방향으로 이동
        shifted_images = [
            x,
            torch.roll(x, shifts=(shift, shift), dims=(2, 3)),     # 오른쪽-아래로 이동
            torch.roll(x, shifts=(-shift, shift), dims=(2, 3)),    # 왼쪽-아래로 이동
            torch.roll(x, shifts=(shift, -shift), dims=(2, 3)),    # 오른쪽-위로 이동
            torch.roll(x, shifts=(-shift, -shift), dims=(2, 3)),   # 왼쪽-위로 이동
        ]

        # 원본 이미지와 이동된 이미지들을 채널 차원에서 결합
        x = torch.cat(shifted_images, dim=1)
        return x

# BaseModel에 SPT 통합
class BaseModel(nn.Module):
    def __init__(self, model_name, pretrained, num_classes, in_chans, patch_size=16):
        super(BaseModel, self).__init__()
        self.spt = ShiftedPatchTokenization(patch_size=patch_size)
        self.base_model = timm.create_model(model_name=model_name, pretrained=pretrained, num_classes=num_classes, in_chans=in_chans * 5)  # 채널 크기 조정

    def forward(self, x):
        x = self.spt(x)  # Shifted Patch Tokenization 적용
        x = self.base_model(x)
        return x

# MLP_layer 클래스는 이전과 동일
class MLP_layer(nn.Module):
    def __init__(self, base_model, out_dim):
        super().__init__()
        self.base_model = base_model
        self.out_dim = out_dim

        self.num_features = self.base_model.base_model.num_features
        
        # out_dim 개수만큼 MLP 생성
        self.mlp_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.num_features, 64),
                nn.ReLU(),
                nn.Linear(64, 1)
            ) for _ in range(out_dim)
        ])

    def forward(self, x):
        base_output = self.base_model(x)
        features = base_output
        outputs = [head(features) for head in self.mlp_heads]
        return torch.cat(outputs, dim=1)

# 모델 생성 함수
def create_model(model_name, pretrained, num_classes, in_chans, out_dim, config):
    if out_dim <= 0:
        raise ValueError("오류: out_dim이 0 이하입니다.")

    base_model = BaseModel(model_name, pretrained, num_classes, in_chans, patch_size=16)
    model = MLP_layer(base_model, out_dim)
    return model
