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
        cnn = config["cnn"]
        in_channels = params.get("in_channels")
        num_classes = params.get("num_classes")
        init_channels = params.get("init_channels")

        
        conv_layers_cfg = cnn["conv_layers"]
        adaptive_pool_output = tuple(cnn["adaptive_pool_output"])
        activation_fn = getattr(nn, cnn.get("activation", "ReLU"))

        layers = []
        cur_in = in_channels
        for layer_cfg in conv_layers_cfg:
            out_ch = eval(
                str(layer_cfg["out_channels"]), {}, {"init_channels": init_channels}
            )
            layers.append(
                nn.Conv3d(
                    cur_in,
                    out_ch,
                    kernel_size=tuple(layer_cfg["kernel_size"]),
                    padding=layer_cfg["padding"]
                )
            )

            layers.append(nn.BatchNorm3d(out_ch))
            layers.append(activation_fn())

            if "pooling" in layer_cfg:
                pool = layer_cfg["pooling"]
                layers.append(
                    getattr(nn, pool["type"])(kernel_size=tuple(pool["kernel_size"]))
                )
            cur_in = out_ch

        layers.append(
            nn.AdaptiveAvgPool3d(output_size=adaptive_pool_output)
        )

        self.features = nn.Sequential(*layers)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(cur_in, num_classes)
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
    
    def select_bands_with_scores(
        self,
        spectral_data,
        labels: np.ndarray,
        pre_selected_bands: List[int],
        target_bands: int,
    ) -> tuple[List[int], List[float]]:
        """
        Args:
            spectral_data: 모델에 입력할 HSI 패치 텐서
            labels: 각 샘플의 레이블 (현재 예시에서는 사용되지 않음)
            pre_selected_bands: 전처리(select_bands)에서 1차로 뽑힌 밴드 인덱스
            target_bands: 최종으로 리턴할 밴드 개수
         Returns:
             final_bands: List[int] – 선택된 밴드 인덱스
             band_scores: List[float] – 각 밴드의 중요도 점수
        """
        self.eval()

        if isinstance(spectral_data, np.ndarray):
            # spectral_data shape 예: (batch, 1, channels, H, W)
            x = torch.from_numpy(spectral_data).float()
        elif torch.is_tensor(spectral_data):
            x = spectral_data
        else:
            raise TypeError(f"Unsupported data type: {type(spectral_data)}")

        if x.dim() == 2:
            batch, channels = x.shape
            x = x.view(batch, 1, channels, 1, 1)
        
        device = next(self.parameters()).device
        x = x.to(device).requires_grad_(True)

        # 1) Forward pass
        logits = self.forward(x)                  # (batch, num_classes)
        score = logits[:, logits.argmax(dim=1)]   # 가장 높은 클래스에 대한 score

        # 2) Backward to get gradients wrt input channels
        self.zero_grad()
        score.mean().backward()

        # 3) x.grad 형태: same shape as x
        grads = x.grad.abs().mean(dim=[0, 2, 3, 4])  # (channels,) 평균 절댓값
        
        # 4) 중요도 기준으로 정렬
        band_scores = grads.tolist()
        final_bands = sorted(range(len(band_scores)),
                             key=lambda i: band_scores[i],
                             reverse=True)
        
        return final_bands[:target_bands], band_scores[:target_bands]



def create_model(model_name, config):
    if model_name == "3DCNN":
        return Simple3DCNN(config)
    else:
        raise ValueError(f"Unknown model: {model_name}")
