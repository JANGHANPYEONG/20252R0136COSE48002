import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN_2D(nn.Module):
    def __init__(self, input_channels, num_classes, dropout=0.0):
        super().__init__()
        def conv_block(in_c, out_c):
            return nn.Sequential(
                nn.Conv2d(in_c, out_c, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_c),
                nn.ReLU(),
                nn.Conv2d(out_c, out_c, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_c),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2, stride=2)
            )

        self.backbone = nn.Sequential(
            conv_block(input_channels, 32),
            conv_block(32, 64),
            conv_block(64, 128),
        )

        self.head = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),  # (B, 128, 1, 1)
            nn.Flatten(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes)
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
    d = config["model"].get("dropout", 0.0)

    return CNN_2D(input_channels=n, num_classes=k, dropout=d)
