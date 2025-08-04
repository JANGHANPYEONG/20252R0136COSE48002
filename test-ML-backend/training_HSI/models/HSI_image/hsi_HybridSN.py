import torch
import torch.nn as nn

class HybridSN(nn.Module):
    def __init__(self, in_chs, patch_size, class_nums,
                 conv1_kernel, conv2_kernel, conv3_kernel, conv4_kernel,
                 conv_channels, fc_units, fc_dropout=0.4, activation='relu'):
        super().__init__()
        act_fn = nn.ReLU if activation == 'relu' else nn.LeakyReLU
        self.in_chs = in_chs
        self.patch_size = patch_size
        self.conv1 = nn.Sequential(
            nn.Conv3d(in_channels=1, out_channels=conv_channels[0], kernel_size=tuple(conv1_kernel)),
            act_fn(inplace=True))
        self.conv2 = nn.Sequential(
            nn.Conv3d(in_channels=conv_channels[0], out_channels=conv_channels[1], kernel_size=tuple(conv2_kernel)),
            act_fn(inplace=True))
        self.conv3 = nn.Sequential(
            nn.Conv3d(in_channels=conv_channels[1], out_channels=conv_channels[2], kernel_size=tuple(conv3_kernel)),
            act_fn(inplace=True))
        self.conv4 = nn.Sequential(
            nn.Conv2d(in_channels=conv_channels[2], out_channels=conv_channels[3], kernel_size=tuple(conv4_kernel)),
            act_fn(inplace=True))
        self.x2_shape = self.get_shape_after_2dconv()
        self.dense1 = nn.Sequential(
            nn.Linear(self.x2_shape, fc_units[0]),
            act_fn(inplace=True),
            nn.Dropout(p=fc_dropout))
        self.dense2 = nn.Sequential(
            nn.Linear(fc_units[0], fc_units[1]),
            act_fn(inplace=True),
            nn.Dropout(p=fc_dropout))
        self.dense3 = nn.Sequential(
            nn.Linear(fc_units[1], class_nums)
        )
    def get_shape_after_2dconv(self):
        x = torch.zeros((1, self.in_chs, self.patch_size, self.patch_size))
        with torch.no_grad():
            x = self.conv1(x.unsqueeze(1))
            x = self.conv2(x)
            x = self.conv3(x)
            # 채널, 공간 차원 정렬 후 conv4 적용
            x = x.permute(0, 1, 3, 4, 2).contiguous()  # [B, C, H, W, S]
            x = x[:, :, :, :, 0]  # S=1 slice만 사용 (spectral 차원 축소)
            x = self.conv4(x)
        return x.shape[1]*x.shape[2]*x.shape[3]
    def forward(self, X):
        X = X.unsqueeze(1)
        x = self.conv1(X)
        x = self.conv2(x)
        x = self.conv3(x)
        x = x.permute(0, 1, 3, 4, 2).contiguous()
        x = x[:, :, :, :, 0]
        x = self.conv4(x)
        x = x.contiguous().view(x.shape[0], -1)
        x = self.dense1(x)
        x = self.dense2(x)
        out = self.dense3(x)
        return out

def create_model(config: dict) -> nn.Module:
    mcfg = config['model']
    return HybridSN(
        in_chs=mcfg.get('in_chs', 5),
        patch_size=mcfg.get('patch_size', 25),
        class_nums=mcfg.get('num_classes', 13),  # num_classes 사용
        conv1_kernel=mcfg.get('conv1_kernel', [3, 3, 3]),  # 5채널에 맞게 조정
        conv2_kernel=mcfg.get('conv2_kernel', [1, 3, 3]),
        conv3_kernel=mcfg.get('conv3_kernel', [1, 3, 3]),
        conv4_kernel=mcfg.get('conv4_kernel', [3, 3]),
        conv_channels=mcfg.get('conv_channels', [8, 16, 32, 64]),
        fc_units=mcfg.get('fc_units', [256, 128]),
        fc_dropout=mcfg.get('fc_dropout', 0.4),
        activation=mcfg.get('activation', 'relu')
    )
