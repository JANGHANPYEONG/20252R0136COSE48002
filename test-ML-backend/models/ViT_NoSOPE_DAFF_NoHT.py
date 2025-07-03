# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: PyTorch 2.2 (NGC 23.11/Python 3.10) on Backend.AI
#     language: python
#     name: python3
# ---

import timm
import torch
import torch.nn as nn
import math

def conv3x3(in_dim, out_dim):
    return torch.nn.Sequential(
        nn.Conv2d(in_dim, out_dim, kernel_size=3, stride=2, padding=1),
        nn.BatchNorm2d(out_dim)
    )

class Affine(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.alpha = nn.Parameter(torch.ones([1, dim, 1, 1]))
        self.beta = nn.Parameter(torch.zeros([1, dim, 1, 1]))

    def forward(self, x):
        return x * self.alpha + self.beta

class SOPE(nn.Module):
    def __init__(self, patch_size, embed_dim):
        super().__init__()
        self.pre_affine = Affine(3)
        self.post_affine = Affine(embed_dim)

        if patch_size[0] == 16:
            self.proj = torch.nn.Sequential(
                conv3x3(3, embed_dim // 8),
                nn.GELU(),
                conv3x3(embed_dim // 8, embed_dim // 4),
                nn.GELU(),
                conv3x3(embed_dim // 4, embed_dim // 2),
                nn.GELU(),
                conv3x3(embed_dim // 2, embed_dim),
            )
        elif patch_size[0] == 4:
            self.proj = torch.nn.Sequential(
                conv3x3(3, embed_dim // 2),
                nn.GELU(),
                conv3x3(embed_dim // 2, embed_dim),
            )
        elif patch_size[0] == 2:
            self.proj = torch.nn.Sequential(
                conv3x3(3, embed_dim),
                nn.GELU(),
            )

    def forward(self, x):
        B, C, H, W = x.shape
        x = self.pre_affine(x)
        x = self.proj(x)
        x = self.post_affine(x)
        Hp, Wp = x.shape[2], x.shape[3]
        x = x.flatten(2).transpose(1, 2)
        return x


class DAFF(nn.Module):
    def __init__(self, in_dim, hid_dim, out_dim, kernel_size=3):
        super().__init__()
        self.conv1 = nn.Conv2d(in_dim, hid_dim, kernel_size=1, stride=1, padding=0)
        self.conv2 = nn.Conv2d(hid_dim, hid_dim, kernel_size=3, stride=1, padding=(kernel_size-1)//2, groups=hid_dim)
        self.conv3 = nn.Conv2d(hid_dim, out_dim, kernel_size=1, stride=1, padding=0)
        self.act = nn.GELU()
        self.squeeze = nn.AdaptiveAvgPool2d((1, 1))
        self.compress = nn.Linear(in_dim, in_dim // 4)
        self.excitation = nn.Linear(in_dim // 4, in_dim)
        self.bn1 = nn.BatchNorm2d(hid_dim)
        self.bn2 = nn.BatchNorm2d(hid_dim)
        self.bn3 = nn.BatchNorm2d(out_dim)

    def forward(self, x):
        B, N, C = x.size()
        cls_token, tokens = torch.split(x, [1, N-1], dim=1)
        x = tokens.reshape(B, int(math.sqrt(N-1)), int(math.sqrt(N-1)), C).permute(0, 3, 1, 2)
        x = self.act(self.bn1(self.conv1(x)))
        x = x + self.act(self.bn2(self.conv2(x)))
        x = self.bn3(self.conv3(x))
        weight = self.squeeze(x).flatten(1).reshape(B, 1, C)
        weight = self.excitation(self.act(self.compress(weight)))
        cls_token = cls_token * weight
        tokens = x.flatten(2).permute(0, 2, 1)
        out = torch.cat((cls_token, tokens), dim=1)
        return out

class BaseModel(nn.Module):
    def __init__(self, model_name, pretrained, num_classes, in_chans, embed_layer=SOPE):
        super(BaseModel, self).__init__()
        self.base_model = timm.create_model(model_name=model_name, pretrained=pretrained, num_classes=num_classes, in_chans=in_chans)

        # self.base_model.patch_embed = SOPE(patch_size=(16, 16), embed_dim=768)
        for i in range(len(self.base_model.blocks)):
            block = self.base_model.blocks[i]
            in_features = block.mlp.fc1.in_features
            hidden_features = block.mlp.fc1.out_features
            out_features = block.mlp.fc2.out_features

            # DAFF 모듈로 교체
            block.mlp = DAFF(in_features, hidden_features, out_features)
        
    def forward(self, x):
        # 패치 임베딩
        x = self.base_model.patch_embed(x)
        # print(f"After patch embedding: {x.shape}")  # (batch_size, num_patches, embed_dim)

        # 클래스 토큰 추가
        batch_size = x.shape[0]
        # print("before:", self.base_model.cls_token.shape)
        cls_token = self.base_model.cls_token.expand(batch_size, -1, -1)  # (batch_size, 1, embed_dim)
        # print("after:", cls_token.shape)
        x = torch.cat((cls_token, x), dim=1)  # (batch_size, num_patches + 1, embed_dim)
        # print(f"After adding class token: {x.shape}")
        
        # 포지셔널 임베딩 추가
        x = x + self.base_model.pos_embed  # (batch_size, num_patches + 1, embed_dim)
        x = self.base_model.pos_drop(x)
        # print(f"After positional embedding: {x.shape}")
        
        # 트랜스포머 블록 통과
        x = self.base_model.blocks(x)
        # print(f"After transformer blocks: {x.shape}")
        
        # LayerNorm 적용
        x = self.base_model.norm(x)
        # print(f"After norm: {x.shape}")
        
        # Class token 선택
        cls_token_final = x[:, 0]
        # print(f"After selecting class token: {cls_token_final.shape}")
        
        # Classifier head 적용
        x = self.base_model.head(cls_token_final)
        # print(f"Final output shape: {x.shape}")

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
        
        # print("mlp input:", base_output.shape)
        
        features = base_output

        outputs = [head(features) for head in self.mlp_heads]

        return torch.cat(outputs, dim=1)


def create_model(model_name, pretrained, num_classes, in_chans, out_dim, config):

    if out_dim <= 0:
        raise ValueError("오류: out_dim이 0 이하입니다.")

    base_model = BaseModel(model_name, pretrained, num_classes, in_chans)
    model = MLP_layer(base_model, out_dim)

    return model

# 모델을 생성
model_name = 'vit_base_r50_s16_224'
pretrained = True
num_classes = 0
in_chans = 3
out_dim = 5

# +
# 모델 생성
# model = create_model(model_name, pretrained, num_classes, in_chans, out_dim)

# +
# 랜덤 입력 생성 (배치 크기 1, 채널 수 3, 이미지 크기 224x224)
# random_input = torch.randn(1, in_chans, 224, 224)

# +
# 모델에 랜덤 입력을 넣어 출력 확인
# output = model(random_input)
# -

# print("Output shape:", output.shape)  # 출력의 크기 확인
