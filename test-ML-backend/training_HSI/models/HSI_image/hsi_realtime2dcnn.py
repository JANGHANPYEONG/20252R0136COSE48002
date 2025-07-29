import torch
import torch.nn as nn
import torch.nn.functional as F

class Realtime2DCNNMultilabel(nn.Module):
    def __init__(self, input_channels, num_classes):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(input_channels, 16, kernel_size=3, padding=1),
            nn.GroupNorm(num_groups=4, num_channels=16),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.head = nn.Linear(16, num_classes)

        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, (nn.Conv2d, nn.Linear)):
            nn.init.kaiming_normal_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.backbone(x)
        x = torch.flatten(x, 1)
        x = self.head(x)
        return x


def create_model(config):
    k = config["model"]["num_classes"]
    n = config["model"]["hsi_channels"]

    return Realtime2DCNNMultilabel(input_channels=n, num_classes=k)
