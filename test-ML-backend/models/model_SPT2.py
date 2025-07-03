import timm
import torch
import torch.nn as nn
from einops import rearrange
from einops.layers.torch import Rearrange
import math

class SPT(nn.Module):
    def __init__(self, in_chans, patch_size=16, embed_dim=64):
        super(SPT, self).__init__()
        self.patch_size = patch_size
        self.embed_dim = embed_dim
        self.num_patches = (224 // patch_size) ** 2  # Assuming input size of 224x224
        
        # 패치 임베딩 레이어 설정
        self.patch_embedding = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)
        
        # 각 패치의 위치 인코딩
        self.position_embedding = nn.Parameter(torch.randn(1, self.num_patches, embed_dim))

    def forward(self, x):
        # 입력을 패치별로 분할하고 임베딩
        x = self.patch_embedding(x)  # (B, embed_dim, H/P, W/P)
        B, E, H, W = x.shape
        x = x.flatten(2).transpose(1, 2)  # (B, num_patches, embed_dim)
        
        # 위치 인코딩 추가
        x += self.position_embedding
        return x



class PatchShifting(nn.Module):
    def __init__(self, patch_size):
        super().__init__()
        self.shift = int(patch_size * (1/2))

    def forward(self, x):
        x_pad = torch.nn.functional.pad(x, (self.shift, self.shift, self.shift, self.shift))
        
        # 4 diagonal directions
        x_lu = x_pad[:, :, :-self.shift*2, :-self.shift*2]
        x_ru = x_pad[:, :, :-self.shift*2, self.shift*2:]
        x_lb = x_pad[:, :, self.shift*2:, :-self.shift*2]
        x_rb = x_pad[:, :, self.shift*2:, self.shift*2:]
        x_cat = torch.cat([x, x_lu, x_ru, x_lb, x_rb], dim=1)
        
        return x_cat


class BaseModel(nn.Module):
    def __init__(self, model_name, pretrained, num_classes, in_chans, spt_embed_dim=64):
        super(BaseModel, self).__init__()
        self.spt = SPT(in_chans=in_chans, embed_dim=spt_embed_dim)
        
        # SPT의 출력 차원을 기반으로 base_model 설정
        self.base_model = timm.create_model(
            model_name=model_name, pretrained=pretrained, num_classes=num_classes, in_chans=spt_embed_dim
        )
        
    def forward(self, x):
        x = self.spt(x)  # SPT 적용으로 패치 기반 출력 획득
        x = self.base_model(x)  # base_model에 SPT 출력 전달
        return x


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
        outputs = [head(base_output) for head in self.mlp_heads]
        return torch.cat(outputs, dim=1)


def create_model(model_name, pretrained, num_classes, in_chans, out_dim, config):
    if out_dim <= 0:
        raise ValueError("오류: out_dim이 0 이하입니다.")

    base_model = BaseModel(model_name, pretrained, num_classes, in_chans, spt_embed_dim=64)
    model = MLP_layer(base_model, out_dim)

    return model
