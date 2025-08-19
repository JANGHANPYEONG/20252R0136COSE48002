import torch
import cv2
import numpy as np

def load_multiband_tensor(image_paths):
    # image_path의 image개수만큼 차원 생성
    bands = []

    for path in image_paths:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)  # shape: (H, W)
        if img is None:
            raise FileNotFoundError(f"Cannot read image: {path}")
        img = img.astype(np.float32) / 255.0  # 정규화 (선택사항)
        bands.append(img)

    stacked = np.stack(bands, axis=0)  # shape: (5, H, W)
    tensor = torch.tensor(stacked, dtype=torch.float32)

    # 예시: 5개 밴드 이미지 경로 리스트
    image_paths = [
        "band1.png",
        "band2.png",
        "band3.png",
        "band4.png",
        "band5.png"
    ]

    # 하나의 개체에 대한 다분광 텐서 생성
    multiband_tensor = tensor

    # 필요하면 배치 차원 추가
    multiband_tensor = multiband_tensor.unsqueeze(0)  # shape: (1, 5, H, W)

    # Padding 차원 추가
    multiband_tensor = multiband_tensor.unsqueeze(0)  # shape: (1, 1, 5, H, W)
    return multiband_tensor