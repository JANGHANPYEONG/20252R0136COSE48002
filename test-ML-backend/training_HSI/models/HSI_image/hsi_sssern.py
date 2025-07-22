import torch
import torch.nn as nn
import torch.nn.functional as F

class SpectralSEBlock(nn.Module):
    def __init__(self, channel, reduction=2):
        super(SpectralSEBlock, self).__init__()
        reduced = max(1, channel // reduction)
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channel, reduced, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(reduced, channel, bias=False),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        b, c, h, w = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y.expand_as(x)
    
class SpatialSEBlock(nn.Module):
    def __init__(self, channel):
        super(SpatialSEBlock, self).__init__()
        self.conv = nn.Conv2d(channel, 1, kernel_size=1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        y = self.conv(x)
        y = self.sigmoid(y)
        return x * y
    
class SSSEBlock(nn.Module):
    def __init__(self, channel, reduction=2):
        super(SSSEBlock, self).__init__()
        self.spectral = SpectralSEBlock(channel, reduction)
        self.spatial = SpatialSEBlock(channel)
        self.alpha = nn.Parameter(torch.tensor(0.5))
    
    def forward(self, x):
        spec_out = self.spectral(x)
        spat_out = self.spatial(x)
        return self.alpha * spec_out + (1 - self.alpha) * spat_out
    
class SSSEBasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels, reduction=2):
        super(SSSEBasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.conv3 = nn.Conv2d(out_channels, in_channels, kernel_size=1)
        self.bn3 = nn.BatchNorm2d(in_channels)
        self.ssse = SSSEBlock(in_channels, reduction)
        
    def forward(self, x):
        residual = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))
        out = self.ssse(out)
        out += residual
        out = self.relu(out)
        return out

class SSSERN(nn.Module):
    def __init__(self, in_channels, num_classes, num_blocks=4, reduction=2):
        super(SSSERN, self).__init__()
        self.blocks = nn.Sequential(
            *[SSSEBasicBlock(in_channels, 32, reduction) for _ in range(num_blocks)]
        )
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Linear(in_channels, num_classes)
        self.fc = nn.Linear(512, num_classes)
    
    def forward(self, x):
        x = self.blocks(x)
        x = self.global_pool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
    
def create_model(config):
    num_classes = config['model']['num_classes']
    params = config['model']['parameters']
    in_channels = params.get('in_channels', 6)
    num_blocks = params.get('num_blocks', 4)
    reduction = params.get('reduction', 2)

    return SSSERN(
        in_channels = in_channels,
        num_classes = num_classes, 
        num_blocks = num_blocks, 
        reduction = reduction
    )