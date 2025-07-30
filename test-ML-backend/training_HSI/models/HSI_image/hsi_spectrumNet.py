import torch
import torch.nn as nn
import torch.nn.functional as F

class SpectralModule(nn.Module):
    def __init__(self, in_channels, squeeze_channels, expand1x1_channels, expand3x3_channels, dropout=0.0):
        super(SpectralModule, self).__init__()
        self.squeeze = nn.Sequential(
            nn.Conv2d(in_channels, squeeze_channels, kernel_size=1),
            nn.BatchNorm2d(squeeze_channels),
            nn.ReLU(inplace=True)
        )

        self.expand1x1 = nn.Sequential(
            nn.Conv2d(squeeze_channels, expand1x1_channels, kernel_size=1),
            nn.BatchNorm2d(expand1x1_channels),
            nn.ReLU(inplace=True)
        )

        self.expand3x3 = nn.Sequential(
            nn.Conv2d(squeeze_channels, expand3x3_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(expand3x3_channels),
            nn.ReLU(inplace=True)
        )

        self.dropout = nn.Dropout2d(p=dropout) if dropout > 0 else nn.Identity()
    
    def forward(self, x):
        x = self.squeeze(x)
        out1 = self.expand1x1(x)
        out3 = self.expand3x3(x)
        out = torch.cat([out1, out3], dim=1)
        return self.dropout(out)

class SpectrumNet(nn.Module):
    def __init__(self, in_channels, num_classes, dropout=0.0):
        super(SpectrumNet, self).__init__()

        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels, 96, kernel_size=2, stride=1),
            nn.BatchNorm2d(96),
            nn.ReLU(inplace=True)
        )

        # (squeeze, expand1x1, expand3x3)
        module_settings = [
            (16, 96, 32),   # spectral2
            (16, 96, 32),   # spectral3
            (32, 192, 64),  # spectral4
            (32, 192, 64),  # spectral5
            (48, 288, 96),  # spectral6
            (48, 288, 96),  # spectral7
            (64, 385, 128), # spectral8
            (64, 385, 128), # spectral9
        ]

        self.layers = nn.ModuleList()
        current_channels = 96

        for idx, (squeeze, exp1, exp3) in enumerate(module_settings):
            self.layers.append(SpectralModule(current_channels, squeeze, exp1, exp3, dropout=dropout))
            current_channels = exp1 + exp3

            if idx in [2, 6]:
                self.layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
        
        self.dropout_final = nn.Dropout2d(p=dropout) if dropout > 0 else nn.Identity()
        self.conv_final = nn.Conv2d(current_channels, num_classes, kernel_size=1)
        self.global_pool = nn.AdaptiveAvgPool2d(1)
    
    def forward(self, x):
        x = self.conv1(x)
        
        for layer in self.layers:
            x = layer(x)
        
        x = self.dropout_final(x)
        x = self.conv_final(x)
        x = self.global_pool(x)
        x = torch.flatten(x, 1)
        return x

def create_model(config):
    num_classes = config['model']['num_classes']
    params = config['model']['parameters']
    in_channels = params.get('in_channels', 5)
    dropout = params.get('dropout', 0.0)

    return SpectrumNet(
        in_channels = in_channels,
        num_classes = num_classes, 
        dropout = dropout
    )