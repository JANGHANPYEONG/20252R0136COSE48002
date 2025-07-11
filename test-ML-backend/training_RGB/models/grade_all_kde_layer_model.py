"""
separate -> share
"""

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
    def __init__(self, base_model, out_dim, kde_path, kde_labels):
        super().__init__()
        self.base_model = base_model
        self.out_dim = out_dim
        self.kde_path = kde_path
        self.kde_labels = kde_labels

        self.num_features = self.base_model.base_model.num_features  # 768

        # KDE 레이어: 각 라벨별로 128 → 256 -> 64 변환
        self.kde_transforms = nn.ModuleList([
            nn.Sequential(
                nn.Linear(128, 256),  # 128 → 256
                nn.ReLU(),
                nn.Dropout(p=0.3),
                nn.Linear(256, 64),
                nn.ReLU(),
                nn.Dropout(p=0.3)
            ) for _ in range(out_dim)
        ])

        # 최종 결합 레이어: 64 * out_dim → 256
        self.kde_combination_layer = nn.Sequential(
            nn.Linear(64 * out_dim, 256),  # 64 * out_dim → 256
            nn.ReLU(),
            nn.Dropout(p=0.3)
        )

        # 최종 MLP 헤드: (768 + 256) → 1
        self.mlp_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.num_features + 256, 64),  # 768 + 256 → 64
                nn.ReLU(),
                nn.Linear(64, 1)  # 64 → 1
            ) for _ in range(out_dim)
        ])

    def load_kde_values(self, grade, label):
        """경로에서 KDE 값을 불러오는 함수"""
        # '등심'을 제외한 grade 값 추출
        grade = grade.replace('등심', '')
        kde_file = os.path.join(self.kde_path, f'kde_{label}_{grade}_grade.npy')
        if not os.path.exists(kde_file):
            raise FileNotFoundError(f"KDE file not found for grade '{grade}' and label '{label}': {kde_file}")
        kde_values = torch.tensor(np.load(kde_file), dtype=torch.float32)
        return kde_values

    def forward(self, x, grade):
        # Base 모델의 출력을 계산
        base_output = self.base_model(x)  # (batch_size, num_features) == (batch_size, 768)

        # 각 라벨별로 KDE 변환 수행
        kde_outputs = []
        for idx, label in enumerate(self.kde_labels):
            kde_features = []
            for g in grade:
                # 등급별 KDE 값 불러오기
                kde_values = self.load_kde_values(g, label).to(base_output.device)  # (128,)
                kde_features.append(kde_values)

            # KDE 값을 텐서로 변환 후 레이어 통과
            kde_features = torch.stack(kde_features)  # (batch_size, 128)
            kde_features = self.kde_transforms[idx](kde_features)  # (batch_size, 64)
            kde_outputs.append(kde_features)

        # KDE 결과 합치기
        kde_combined = torch.cat(kde_outputs, dim=1)  # (batch_size, 64 * out_dim)
        kde_combined = self.kde_combination_layer(kde_combined)  # (batch_size, 256)

        # 768차원과 256차원 결합
        combined_features = torch.cat([base_output, kde_combined], dim=1)  # (batch_size, 768 + 256)

        # 각 MLP 헤드를 통해 계산
        outputs = [mlp_head(combined_features) for mlp_head in self.mlp_heads]  # list of (batch_size, 1)
        outputs = torch.cat(outputs, dim=1)  # (batch_size, out_dim)
        return outputs

def create_model(model_name, pretrained, num_classes, in_chans, out_dim, config):
    if out_dim <= 0:
        raise ValueError("오류: out_dim이 0 이하입니다.")

    kde_path = 'dataset/ku_kde2_grade_norm'
    kde_labels = ['Marbling', 'Color', 'Texture', 'Surface_Moisture', 'Total']

    if len(kde_labels) != out_dim:
        raise ValueError("The length of kde_labels must match out_dim.")

    base_model = BaseModel(model_name, pretrained, num_classes, in_chans)
    model = MLP_layer(base_model, out_dim=out_dim, kde_path=kde_path, kde_labels=kde_labels)

    return model
