import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict

class Simple1DCNN(nn.Module):
    def __init__(self, config: Dict):
        super().__init__()
        params      = config["training"]["parameters"]
        in_ch       = params["in_channels"]
        num_classes = params["num_classes"]
        init_ch     = params["init_channels"]

        layers = []
        cur = in_ch
        for lcfg in config["cnn"]["conv_layers"]:
            # kernel_size, padding을 int 또는 list로 지정 가능하도록 처리
            k = lcfg["kernel_size"]
            p = lcfg["padding"]
            kernel = k[0] if isinstance(k, (list, tuple)) else k
            pad    = p[0] if isinstance(p, (list, tuple)) else p

            out = eval(str(lcfg["out_channels"]), {}, {"init_channels": init_ch})
            layers += [
                nn.Conv1d(cur, out, kernel_size=kernel, padding=pad),
                nn.BatchNorm1d(out),
                getattr(nn, config["cnn"].get("activation", "ReLU"))()
            ]
            cur = out

        self.features   = nn.Sequential(*layers)
        self.classifier = nn.Linear(cur, num_classes)

    def forward(self, x):
        # x: (batch, channels, length)
        x = self.features(x)    # → (batch, cur, L')
        x = x.mean(dim=-1)      # global average pooling over length
        return self.classifier(x)

    def select_bands_with_scores(
        self,
        spectral_data,
        labels: np.ndarray,
        pre_selected_bands: List[int],
        target_bands: int,
    ) -> tuple[List[int], List[float]]:
        self.eval()
        # numpy array → tensor
        if isinstance(spectral_data, np.ndarray):
            x = torch.from_numpy(spectral_data).float()
        elif torch.is_tensor(spectral_data):
            x = spectral_data
        else:
            raise TypeError(f"Unsupported data type: {type(spectral_data)}")

        # (batch, channels) → (batch, channels, 1) if needed
        if x.dim() == 2:
            batch, ch = x.shape               # (2731, 5)
            x = x.view(batch, 1, ch)          # → (2731, 1, 5)

        device = next(self.parameters()).device
        x = x.to(device).requires_grad_(True)

        # forward / backward
        logits = self.forward(x)                
        score  = logits[:, logits.argmax(dim=1)]
        self.zero_grad()
        score.mean().backward()

        # gradient shape = (batch, channels, length)
        # 평균 절댓값을 채널 축만 남기고 계산
        grads = x.grad.abs().mean(dim=[0,2])  # (channels,)

        band_scores = grads.tolist()
        final_bands = sorted(
            range(len(band_scores)),
            key=lambda i: band_scores[i],
            reverse=True
        )
        return final_bands[:target_bands], band_scores[:target_bands]

def create_model(model_name, config):
    if model_name == "1DCNN":
        return Simple1DCNN(config)
    else:
        raise ValueError(f"Unknown model: {model_name}")
