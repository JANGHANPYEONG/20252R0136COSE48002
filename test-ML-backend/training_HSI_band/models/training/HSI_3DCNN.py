import torch
import torch.nn as nn
import timm
import cv2
import numpy as np
import pywt
from sklearn.cluster import AgglomerativeClustering
from scipy import ndimage
import spectral

class BaseModel(nn.Module):
    def __init__(self, model_name, pretrained, num_classes, in_chans):
        super(BaseModel, self).__init__()
        self.base_model = timm.create_model(model_name=model_name, pretrained=pretrained, num_classes=num_classes, in_chans=in_chans)

    def forward(self, x):
        return self.base_model(x)

class ProcessingData(nn.Module):
    def __init__(self):
        super(ProcessingData, self).__init__()

    def dual_partition(self, section_path):
        img = spectral.open_image(section_path).load()  # (h, w, d)
        h, w, d = img.shape
        H_2d = img.reshape(-1, d)

        corr = np.corrcoef(H_2d.T)
        n_clusters = 10
        clusterer = AgglomerativeClustering(n_clusters=n_clusters, affinity='precomputed', linkage='average')
        labels = clusterer.fit_predict(1 - np.abs(corr))

        selected_bands = []
        for cl in range(n_clusters):
            idx = np.where(labels == cl)[0]
            energies = []
            for b in idx:
                coeffs = pywt.wavedec(H_2d[:, b], wavelet='db1', level=2)
                energy = sum((c**2).sum() for c in coeffs)
                energies.append((b, energy))
            energies.sort(key=lambda x: x[1], reverse=True)
            top_k = [b for b, _ in energies[:5]]
            selected_bands.extend(top_k)

        return selected_bands

    def extract_selected_band_image(self, hsi_path, selected_bands):
        img = spectral.open_image(hsi_path).load()  # (h, w, d)
        selected_img = img[:, :, selected_bands]  # (h, w, k)
        selected_img = (selected_img - selected_img.min()) / (selected_img.max() - selected_img.min() + 1e-6)
        return torch.tensor(selected_img.transpose(2, 0, 1), dtype=torch.float32)

    def hemi_reflectance_filter(self, patch):
        kernel = np.ones((3,3)) / 9.0
        return ndimage.convolve(patch, kernel, mode='reflect')


class MLP_layer(nn.Module):
    def __init__(self, base_model, out_dim):
        super().__init__()
        self.base_model = base_model
        self.processing = ProcessingData()
        self.num_features = self.base_model.base_model.num_features
        self.out_dim = out_dim

        self.marbling_head = nn.Sequential(
            nn.Linear(self.num_features + 256, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )
        self.texture_preference = nn.Sequential(
            nn.Linear(self.num_features, 256),
            nn.ReLU(),
            nn.Linear(256, 2)
        )
        self.moisture_head = nn.Sequential(
            nn.Linear(self.num_features, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        self.color_head = nn.Sequential(
            nn.Linear(self.num_features + 256, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )

    def forward(self, section_paths):
        # 하나의 section_path만 사용하는 예시
        section_path = section_paths[0]

        # 1. 밴드 선택
        selected_bands = self.processing.dual_partition(section_path)

        # 2. 선택된 밴드로 이미지 생성
        input_tensor = self.processing.extract_selected_band_image(section_path, selected_bands)
        input_tensor = input_tensor.unsqueeze(0).to(next(self.parameters()).device)  # (1, C, H, W)

        # 3. 특징 추출
        features = self.base_model(input_tensor)

        # 4. 더미 벡터 예시 (HSV/행열 벡터 대신)
        dummy_vector = torch.randn((1, 256)).to(features.device)

        # 5. 예측 결과
        marbling = self.marbling_head(torch.cat([features, dummy_vector], dim=1))
        texture_pref = self.texture_preference(features)
        moisture = self.moisture_head(features)
        color = self.color_head(torch.cat([features, dummy_vector], dim=1))

        return torch.cat([
            marbling,
            color,
            texture_pref[:, 0:1],
            moisture,
            texture_pref[:, 1:2]
        ], dim=1)

def create_model(model_name, pretrained, num_classes, in_chans, out_dim):
    if out_dim <= 0:
        raise ValueError("오류: out_dim이 0 이하입니다.")
    base_model = BaseModel(model_name, pretrained, num_classes, in_chans)
    model = MLP_layer(base_model, out_dim)
    return model
