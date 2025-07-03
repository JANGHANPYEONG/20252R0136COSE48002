import os
import timm
import torch
import torch.nn as nn
import numpy as np

class BaseModel(nn.Module):
    def __init__(self, model_name, pretrained, num_classes, in_chans):
        super(BaseModel, self).__init__()
        self.base_model = timm.create_model(model_name=model_name, pretrained=pretrained, num_classes=num_classes, in_chans=in_chans)

    def forward(self, x):
        x = self.base_model(x)
        return x

class MLP_layer(nn.Module):
    def __init__(self, base_model, out_dim, kde_path, custom_str):
        super().__init__()
        self.base_model = base_model
        self.out_dim = out_dim
        self.kde_path = kde_path
        self.custom_str = custom_str

        self.num_features = self.base_model.base_model.num_features  # 768

        # KDE 경로 및 레이어
        self.kde_transform = nn.Sequential(
            nn.Linear(128, 256),  # 128 → 256
            nn.ReLU()
        )

        # 최종 MLP 헤드: (768 + 256) → 1
        self.mlp_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.num_features + 256, 64),  # 768 + 256 → 64
                nn.ReLU(),
                nn.Linear(64, 1)  # 64 → 1
            ) for _ in range(out_dim)
        ])

    def load_kde_values(self, grade):
        """경로에서 KDE 값을 불러오는 함수"""
        grade = grade.replace('등심', '')
        kde_file = os.path.join(self.kde_path, f'kde_{self.custom_str}_{grade}_grade.npy')
        if not os.path.exists(kde_file):
            raise FileNotFoundError(f"KDE file not found for grade '{grade}': {kde_file}")
        kde_values = torch.tensor(np.load(kde_file), dtype=torch.float32)
        return kde_values

    def forward(self, x, grade):
        # Base 모델의 출력을 계산
        base_output = self.base_model(x)  # (batch_size, num_features) == (batch_size, 768)

        # KDE 값을 처리
        kde_features = []
        for g in grade:
            # 등급별 KDE 값 불러오기
            kde_values = self.load_kde_values(g).to(base_output.device)  # (128,)
            kde_features.append(kde_values)

        # KDE 값을 텐서로 변환 후 레이어 통과
        kde_features = torch.stack(kde_features)  # (batch_size, 128)
        kde_features = self.kde_transform(kde_features)  # (batch_size, 256)

        # 768차원과 256차원 결합
        combined_features = torch.cat([base_output, kde_features], dim=1)  # (batch_size, 768 + 256)

        # 각 MLP 헤드를 통해 계산
        outputs = [head(combined_features) for head in self.mlp_heads]  # list of (batch_size, 1)
        outputs = torch.cat(outputs, dim=1)  # (batch_size, out_dim)

        return outputs

def create_model(model_name, pretrained, num_classes, in_chans, out_dim, config):
    if out_dim <= 0:
        raise ValueError("오류: out_dim이 0 이하입니다.")

    kde_path = 'dataset/ku_kde_norm_1213'
    kde_label = 'Color'

    base_model = BaseModel(model_name, pretrained, num_classes, in_chans)
    model = MLP_layer(base_model, out_dim=out_dim, kde_path=kde_path, custom_str=kde_label)

    return model
