import numpy as np
import pywt
import torch
import torch.nn as nn
from typing import List, Dict, Tuple

# 3D CNN 기반 밴드 중요도 계산 및 최종 밴드 선택
class Simple3DCNN(nn.Module):
    def __init__(self, config: Dict):
        super(Simple3DCNN, self).__init__() 
        params = config["training"]["parameters"]
        cnn_cfg = config.get("cnn", {})
        in_channels = params.get("in_channels", 1)
        num_classes = params.get("num_classes")
        init_channels = params.get("init_channels", 16)

        conv_layers_cfg = cnn["conv_layers"]
        adaptive_pool_output = tuple(cnn["adaptive_pool_output"])
        activation_fn = getattr(nn, cnn.get("activation", "ReLU"))

        layers = []
        cur_in = in_channels
        for layer_cfg in conv_layers_cfg:
            out_ch = eval(str(layer_cfg["out_channels"]), {}, {"init_channels": init_channels})
            layers.append(
                nn.Conv3d(
                    cur_in,
                    out_ch,
                    kernel_size=tuple(layer_cfg.get("kernel_size", [3, 3, 3])),
                    padding=tuple(layer_cfg.get("padding", [0, 0, 0]))
                )
            )
            layers.append(nn.BatchNorm3d(out_ch))
            layers.append(activation_fn())

            if "pooling" in layer_cfg:
                pool = layer_cfg["pooling"]
                layers.append(
                    getattr(nn, pool.get("type", "MaxPool3d"))(kernel_size=tuple(pool.get("kernel_size", [2, 2, 2])))
                )
            cur_in = out_ch

        layers.append(nn.AdaptiveAvgPool3d(output_size=adaptive_pool_output))
        self.features = nn.Sequential(*layers)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(
                cur_in * adaptive_pool_output[0] * adaptive_pool_output[1] * adaptive_pool_output[2],
                num_classes
            )
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: torch.Tensor of shape (batch_size, 1, depth, height, width)
        Returns:
            logits: torch.Tensor of shape (batch_size, num_classes)
        """
        x = self.features(x)
        x = self.classifier(x)
        return x
    
    # 250715 추가
    @staticmethod
    def add_coord_channels(x: torch.Tensor) -> torch.Tensor:
        # 좌표 채널은 H·W≥2일 때만 의미가 있음
        if x.dim() != 5:
            return x                  # 2‑D, 4‑D 입력엔 좌표 채널 안 붙임
        B, _, C, H, W = x.shape
        if H == 1 or W == 1:
            return x                  # 1×1 패치는 좌표 채널 무시

        yy = torch.linspace(-1, 1, H, device=x.device)\
                .view(1,1,1,H,1).expand(B,1,1,H,W)
        xx = torch.linspace(-1, 1, W, device=x.device)\
                .view(1,1,1,1,W).expand(B,1,1,H,W)
        return torch.cat([x, yy, xx], dim=2)   # (B,1,C+2,H,W)

    def select_bands_with_scores(
        self,
        spectral_data: np.ndarray or torch.Tensor,
        labels: np.ndarray,
        pre_selected_bands: List[int],
        target_bands: int,
    ) -> Tuple[List[int], List[float]]:
        """
        Gradient-based band importance using 3D CNN.

        Args:
            spectral_data: HSI volume
                - numpy: shape (B, H, W, B_full)
                - tensor: shape (B, 1, B_full, H, W) or (B, B_full, H, W)
            labels: unused labels, shape (B, ...)
            pre_selected_bands: list of band indices to evaluate
            target_bands: number of bands to select
        Returns:
            selected: List[int], indices of selected bands
            scores: List[float], importance scores
        """
        self.eval()

        # spectral_data가 Numpy 배열이라면 torch.Tensor로 변환
        if isinstance(spectral_data, np.ndarray):
            # numpy: (B, H, W, B_full) -> slice -> (B, H, W, K)
            vol = spectral_data[..., pre_selected_bands]
            x = torch.from_numpy(vol).float()               # (B,H,W,K)
            x = x.permute(0, 3, 1, 2).unsqueeze(1)          # (B,1,K,H,W)
        elif torch.is_tensor(spectral_data):
            t = spectral_data
            if t.dim() == 4:
                t = t.unsqueeze(1)                          # (B,1,B_full,H,W)
            x = t[:, :, pre_selected_bands, :, :]         # (B,1,K,H,W)
        else:
            raise TypeError(f"Unsupported data type: {type(spectral_data)}")

        # spectral_data 차원 검사 및 재구성
        if x.dim() == 2: # x가 (batch, channels) 모양이라면, 
            batch, channels = x.shape
            # 모델이 기대하는 5D 텐서 (batch, 1, channels, 1, 1) 형태로 뷰(view)를 변경
            # 차원 맞춤: 2D 입력 → 5D (B, 1, C, H=1, W=1) 
            x = x.view(batch, 1, channels, 1, 1) 

        device = next(self.parameters()).device
        x = x.to(device).requires_grad_(True)

        # 위치 정보 추가를 위한 처리
        # spectral_data → tensor x  (B,1,C,H,W)
        x = self.add_coord_channels(x)       # (B,1,C+2,H,W)

        # 1) Forward pass
        logits = self.forward(x)                  # (batch, num_classes)
        score = logits[:, logits.argmax(dim=1)]   # 가장 높은 클래스에 대한 score

        # 3) 역전파
        self.zero_grad()
        scores_tensor.mean().backward()

        # 4) gradient 평균 -> band importance
        grads = x.grad.abs().mean(dim=[0, 2, 3, 4])        # (K,)
        band_scores = grads.tolist()

        # 5) 상위 bands 선택
        ranked = sorted(range(len(band_scores)), key=lambda i: band_scores[i], reverse=True)
        selected = [pre_selected_bands[i] for i in ranked[:target_bands]]
        scores = [band_scores[i] for i in ranked[:target_bands]]

        return selected, scores

def create_model(model_name, config):
    if model_name == "3DCNN":
        return Simple3DCNN(config)
    raise ValueError(f"Unknown model: {model_name}")