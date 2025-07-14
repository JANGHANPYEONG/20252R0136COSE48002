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
        models = config["3DCNN"]
        in_channels = params.get("in_channels")
        num_classes = params.get("num_classes")
        init_channels = params.get("init_channels")

        
        conv_layers_cfg = models["conv_layers"]
        adaptive_pool_output = tuple(models["adaptive_pool_output"])
        activation_fn = getattr(nn, models.get("activation", "ReLU"))

        layers = []
        cur_in = in_channels
        for layer_cfg in conv_layers_cfg:
            out_ch = eval(
                str(layer_cfg["out_channels"]), {}, {"init_channels": init_channels}
            )
            layers.append(
                nn.Conv3d(
                    cur_in, # size of input data
                    out_ch, # size of output data
                    kernel_size=tuple(layer_cfg["kernel_size"]), # size of kernel
                    padding=layer_cfg["padding"] # padding
                )
            )

            layers.append(nn.BatchNorm3d(out_ch)) # 3D conv 사용하였으므로 3d Norm
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
    

def create_model(model_name, config):
    if model_name == "BS_3DCNN":
        return Simple3DCNN(config)
    else:
        raise ValueError(f"Unknown model: {model_name}")
