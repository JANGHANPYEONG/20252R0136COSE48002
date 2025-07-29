import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN_2D(nn.Module):
    def __init__(self, input_channels, num_classes):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(),

            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),

            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.AdaptiveAvgPool2d((1, 1))  # Output shape: (B, 128, 1, 1)
        )

        self.head = nn.Sequential(
            nn.Flatten(),                # (B, 128, 1, 1) → (B, 128)
            nn.Linear(128, 512),
            nn.ReLU(),
            nn.Linear(512, num_classes)
        )

        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, (nn.Conv2d, nn.Linear)):
            nn.init.kaiming_normal_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.backbone(x)  # shape: (B, 128, 1, 1)
        x = self.head(x)      # shape: (B, num_classes)
        return x


def create_model(config):
    k = config["model"]["num_classes"]
    n = config["model"]["hsi_channels"]

    return CNN_2D(input_channels=n, num_classes=k)
