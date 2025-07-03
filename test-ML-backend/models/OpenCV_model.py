import timm
import torch
import torch.nn as nn
import cv2
import numpy as np

class BaseModel(nn.Module):
    def __init__(self, model_name, pretrained, num_classes, in_chans):
        super(BaseModel, self).__init__()
        self.base_model = timm.create_model(model_name=model_name, pretrained=pretrained, num_classes=num_classes, in_chans=in_chans)

    def forward(self, x):
        x = self.base_model(x)
        return x

class MLP_layer(nn.Module):
    def __init__(self, base_model, out_dim):
        super().__init__()
        self.base_model = base_model
        self.out_dim = out_dim
        self.num_features = self.base_model.base_model.num_features
        
        # 마블링을 위한 MLP (행과 열 벡터 추가)
        self.marbling_head = nn.Sequential(
            nn.Linear(self.num_features + 256, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )
        
        # 조직감과 기호도를 위한 MLP
        self.texture_preference = nn.Sequential(
            nn.Linear(self.num_features, 256),
            nn.ReLU(),
            nn.Linear(256, 2)
        )
        
        # 표면육즙을 위한 MLP
        self.moisture_head = nn.Sequential(
            nn.Linear(self.num_features, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
        # 색깔을 위한 MLP (HSV 벡터 포함)
        self.color_head = nn.Sequential(
            nn.Linear(self.num_features + 256, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )

    def forward(self, x, section_paths):
        features = self.base_model(x)
        
        # HSV 벡터 추출 (단면 이미지 사용)
        hsv_vector = self.get_hsv_vector(section_paths)
        
        # 행과 열 벡터 추출 (단면 이미지 사용)
        combined_vectors = self.extract_row_col_vectors(section_paths)

        # 마블링 예측 (행과 열 벡터 결합)
        marbling_features = torch.cat([features, combined_vectors], dim=1)
        marbling = self.marbling_head(marbling_features)

        # 조직감과 기호도 예측
        texture_preference = self.texture_preference(features)

        # 표면육즙 예측
        moisture = self.moisture_head(features)

        # 색깔 예측 (HSV 벡터 포함)
        color_features = torch.cat([features, hsv_vector], dim=1)
        color = self.color_head(color_features)
        
        # 원래의 라벨 순서대로 출력을 결합
        return torch.cat([
            marbling,
            color,
            texture_preference[:, 0:1],
            moisture,
            texture_preference[:, 1:2]
        ], dim=1)

    def get_hsv_vector(self, section_paths, epsilon=1e-6, target_min=-2.2, target_max=2.0, target_mean=-0.105):
        hsv_vectors = []

        for path in section_paths:
            img = cv2.imread(path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # RGB에서 HSV로 변환
            hsv_image = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            
            # 히스토그램 계산
            hist = cv2.calcHist([hsv_image], [0, 1, 2], None, [8, 4, 8], [0, 180, 0, 256, 0, 256])
            hist_vector = hist.flatten()
            
            # 모든 빈(bin)에 작은 값을 추가하여 0을 방지
            hist_vector += epsilon
            
            # 정규화
            hist_vector = hist_vector / np.sum(hist_vector)
            
            # 벡터를 ViT 출력 범위로 조정
            current_min = hist_vector.min()
            current_max = hist_vector.max()
            hist_scaled = (hist_vector - current_min) / (current_max - current_min)
            hist_scaled = hist_scaled * (target_max - target_min) + target_min
            
            # 평균 조정
            mean_diff = target_mean - hist_scaled.mean()
            hist_adjusted = hist_scaled + mean_diff
            
            hsv_vectors.append(hist_adjusted)
        
        hsv_vectors = np.array(hsv_vectors)

        return torch.from_numpy(hsv_vectors).to(next(self.parameters()).device)

    def extract_row_col_vectors(self, section_paths):
        row_vectors_list = []
        col_vectors_list = []
        
        for path in section_paths:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            non_black_mask = img > 0

            rows = [img[j, non_black_mask[j, :]] for j in range(img.shape[0]) if np.any(non_black_mask[j, :])]
            cols = [img[non_black_mask[:, j], j] for j in range(img.shape[1]) if np.any(non_black_mask[:, j])]

            def normalize_and_resize(vector, length):
                if len(vector) == 0:
                    return np.zeros(length)
                vector = (vector - vector.min()) / (vector.max() - vector.min() + 1e-8)
                return np.interp(np.linspace(0, len(vector) - 1, length), np.arange(len(vector)), vector)

            # 64로 크기 변경
            row_vectors_batch = [normalize_and_resize(row, 64) for row in rows]
            col_vectors_batch = [normalize_and_resize(col, 64) for col in cols]

            # 32개로 맞추기
            if len(row_vectors_batch) > 32:
                row_indices = np.linspace(0, len(row_vectors_batch) - 1, 32, dtype=int)
                row_vectors_batch = [row_vectors_batch[j] for j in row_indices]
            elif len(row_vectors_batch) < 32:
                row_vectors_batch.extend([np.zeros(64)] * (32 - len(row_vectors_batch)))

            if len(col_vectors_batch) > 32:
                col_indices = np.linspace(0, len(col_vectors_batch) - 1, 32, dtype=int)
                col_vectors_batch = [col_vectors_batch[j] for j in col_indices]
            elif len(col_vectors_batch) < 32:
                col_vectors_batch.extend([np.zeros(64)] * (32 - len(col_vectors_batch)))

            row_vectors_list.append(np.array(row_vectors_batch))
            col_vectors_list.append(np.array(col_vectors_batch))

        # NumPy 배열로 변환 후 PyTorch 텐서로 변환
        row_vectors = torch.from_numpy(np.array(row_vectors_list)).to(next(self.parameters()).device).float()
        col_vectors = torch.from_numpy(np.array(col_vectors_list)).to(next(self.parameters()).device).float()

        # 형태 변경 및 결합
        batch_size = len(section_paths)
        row_vectors_flat = row_vectors.view(batch_size, -1)  # (batch_size, 32*64)
        col_vectors_flat = col_vectors.view(batch_size, -1)  # (batch_size, 32*64)

        combined_vectors = torch.cat([row_vectors_flat, col_vectors_flat], dim=1)  # (batch_size, 32*64*2)

        return combined_vectors

def create_model(model_name, pretrained, num_classes, in_chans, out_dim, config):
    if out_dim <= 0:
        raise ValueError("오류: out_dim이 0 이하입니다.")

    base_model = BaseModel(model_name, pretrained, num_classes, in_chans)
    model = MLP_layer(base_model, out_dim)

    return model
