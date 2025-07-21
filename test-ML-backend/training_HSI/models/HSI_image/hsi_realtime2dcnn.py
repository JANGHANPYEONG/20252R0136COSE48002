import torch
import torch.nn as nn
import torch.nn.functional as F

class Realtime2DCNNMultilabel(nn.Module):
    def __init__(self, input_channels=5, num_classes=13, num_regression_targets=0):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(input_channels, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1))
        )

        self.classification_head = nn.Linear(16, num_classes)

        self.regression_head = (
            nn.Linear(16, num_regression_targets)
            if num_regression_targets > 0 else None
        )

        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, (nn.Conv2d, nn.Linear)):
            nn.init.kaiming_normal_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        features = self.backbone(x)
        features = torch.flatten(features, 1)

        classification_output = torch.sigmoid(self.classification_head(features))

        if self.regression_head is not None:
            regression_output = self.regression_head(features)
        else:
            regression_output = torch.empty(classification_output.shape[0], 0, device=x.device)

        return {
            'classification': classification_output,
            'regression': regression_output
        }


def create_model(num_classes, num_regression_targets=0, hsi_channels=5, **kwargs):
    return Realtime2DCNNMultilabel(
        input_channels=hsi_channels,
        num_classes=num_classes,
        num_regression_targets=num_regression_targets
    )  
