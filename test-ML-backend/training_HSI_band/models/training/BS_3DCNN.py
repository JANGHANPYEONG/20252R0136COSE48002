import numpy as np
import pywt
from sklearn.cluster import AgglomerativeClustering
from typing import List, Dict
import torch
import torch.nn as nn

# 선택된 밴드 이미지 (h, w, p)를 입력으로 받는 3D CNN 모델
class Simple3DCNN(nn.Module):
    def __init__(self, config: Dict):
        super(Simple3DCNN, self).__init__()
        params = config["training"]["parameters"]
        in_channels = params.get("in_channels")
        num_classes = params.get("num_classes")
        init_channels = params.get("init_channels")

        self.features = nn.Sequential(
            nn.Conv3d(1, init_channels, kernel_size=(3, 3, 3), padding=1),
            nn.BatchNorm3d(init_channels),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=(1, 2, 2)),

            nn.Conv3d(init_channels, init_channels * 2, kernel_size=(3, 3, 3), padding=1),
            nn.BatchNorm3d(init_channels * 2),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=(1, 2, 2)),

            nn.Conv3d(init_channels * 2, init_channels * 4, kernel_size=(3, 3, 3), padding=1),
            nn.BatchNorm3d(init_channels * 4),
            nn.ReLU(),
            nn.AdaptiveAvgPool3d(output_size=(1, 1, 1))
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(init_channels * 4, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: torch.Tensor (batch_size, 1, channels, height, width)
        Returns:
            torch.Tensor (batch_size, num_classes)
        """
        x = self.features(x)
        x = self.classifier(x)
        return x