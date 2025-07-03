import timm
import torch
import torch.nn as nn


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# n : batch size
# m : number of pairs
# k X k : resolution of the embedding grid
# D : dimension of each token embedding
# x : a tensor of n embedding grids, shape=[n, D, k, k]
def position_sampling(k, m, n):
    pos_1 = torch.randint(k, size=(n, m, 2))
    pos_2 = torch.randint(k, size=(n, m, 2))
    return pos_1.to(device), pos_2.to(device)

def collect_samples(x, pos, n):
    _, c, h, w = x.size()
    x = x.view(n, c, -1).permute(1, 0, 2).reshape(c, -1)
    pos = ((torch.arange(n).long().to(pos.device) * h * w).view(n, 1) + pos[:, :, 0] * h + pos[:, :, 1]).view(-1)
    return (x[:, pos]).view(c, n, -1).permute(1, 0, 2)

def dense_relative_localization_loss(x, drloc_mlp, m):
    n, D, k, k = x.size()
    pos_1, pos_2 = position_sampling(k, m, n)
    deltaxy = abs((pos_1 - pos_2).float())  # [n, m, 2]
    deltaxy /= k
    pts_1 = collect_samples(x, pos_1, n).transpose(1, 2)  # [n, m, D]
    pts_2 = collect_samples(x, pos_2, n).transpose(1, 2)  # [n, m, D]
    predxy = drloc_mlp(torch.cat([pts_1, pts_2], dim=2))
    return nn.L1Loss()(predxy, deltaxy)

class DRLocMLP(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(DRLocMLP, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        return self.layers(x)

drloc_mlp = DRLocMLP(2 * 768, 1024, 2).to(device)

class SelectAdaptivePool2d(nn.Module):
    def __init__(self, pool_type='avg', flatten=True):
        super(SelectAdaptivePool2d, self).__init__()
        if pool_type == 'avg':
            self.pool = nn.AdaptiveAvgPool2d((1, 1))  # Adaptive Average Pooling
        elif pool_type == 'max':
            self.pool = nn.AdaptiveMaxPool2d((1, 1))  # Adaptive Max Pooling
        else:
            raise ValueError("Unsupported pool_type: {}".format(pool_type))
        
        self.flatten = flatten

    def forward(self, x):
        # x shape: (batch_size, 7, 7, 768)
        x = x.permute(0, 3, 1, 2)  # Change to (batch_size, 768, 7, 7)
        x = self.pool(x)  # Pooling to (batch_size, 768, 1, 1)
        if self.flatten:
            x = x.view(x.size(0), -1)  # Flatten to (batch_size, 768)
        return x 

class BaseModel(nn.Module):
    def __init__(self, model_name, pretrained, num_classes, in_chans):
        super(BaseModel, self).__init__()
        self.base_model = timm.create_model(model_name=model_name, pretrained=pretrained, num_classes=num_classes, in_chans=in_chans)

        self.base_model.head.global_pool = nn.Identity()
        self.global_pool = SelectAdaptivePool2d()

    def forward(self, x, m):
        
        x = self.base_model(x) # x: n, k, k, d

        patch_token = x.permute(0, 3, 1, 2) # n, d, k, k

        # drloc_loss 계산
        drloc_loss = dense_relative_localization_loss(patch_token, drloc_mlp, m)


        # Classifier head 적용
        x = self.global_pool(x)

        return x, drloc_loss

    

class MLP_layer(nn.Module):
    def __init__(self, base_model, out_dim):
        super().__init__()
        self.base_model = base_model
        self.out_dim = out_dim

        self.num_features = self.base_model.base_model.num_features
        
        # out_dim 개수만큼 MLP 생성
        self.mlp_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.num_features, 64),
                nn.ReLU(),
                nn.Linear(64, 1)
            ) for _ in range(out_dim)
        ])

    def forward(self, x, m):
        base_output, drloc_loss = self.base_model(x, m)
        
        features = base_output

        outputs = [head(features) for head in self.mlp_heads]

        return torch.cat(outputs, dim=1), drloc_loss

def create_model(model_name, pretrained, num_classes, in_chans, out_dim, config):

    if out_dim <= 0:
        raise ValueError("오류: out_dim이 0 이하입니다.")

    base_model = BaseModel(model_name, pretrained, num_classes, in_chans)
    model = MLP_layer(base_model, out_dim)

    return model
