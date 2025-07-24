import torch
import torch.nn as nn

class PatchEmbedding(nn.Module):
    def __init__(self, in_channels, patch_size, emb_dim, img_size):
        super().__init__()
        self.patch_size = patch_size
        self.n_patches = (img_size // patch_size) ** 2
        self.proj = nn.Conv2d(in_channels, emb_dim, kernel_size=patch_size, stride=patch_size)

    def forward(self, x):
        x = self.proj(x)  # (B, emb_dim, H/patch, W/patch)
        x = x.flatten(2)  # (B, emb_dim, N)
        x = x.transpose(1, 2)  # (B, N, emb_dim)
        return x

class ViT(nn.Module):
    def __init__(self, in_channels, img_size, patch_size, emb_dim, depth, num_heads, mlp_dim, num_classes, dropout=0.1):
        super().__init__()
        self.patch_embed = PatchEmbedding(in_channels, patch_size, emb_dim, img_size)
        n_patches = self.patch_embed.n_patches
        self.cls_token = nn.Parameter(torch.zeros(1, 1, emb_dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, n_patches + 1, emb_dim))
        encoder_layer = nn.TransformerEncoderLayer(d_model=emb_dim, nhead=num_heads, dim_feedforward=mlp_dim, dropout=dropout, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=depth)
        self.norm = nn.LayerNorm(emb_dim)
        self.head = nn.Linear(emb_dim, num_classes)
        self._init_weights()

    def _init_weights(self):
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.cls_token, std=0.02)
        nn.init.xavier_uniform_(self.head.weight)
        nn.init.constant_(self.head.bias, 0)

    def forward(self, x):
        B = x.size(0)
        x = self.patch_embed(x)
        cls_tokens = self.cls_token.expand(B, -1, -1)
        x = torch.cat((cls_tokens, x), dim=1)
        x = x + self.pos_embed
        x = self.transformer(x)
        x = self.norm(x[:, 0])  # cls token
        x = self.head(x)
        return x

def create_model(config: dict) -> nn.Module:
    mcfg = config['model']
    in_channels = mcfg.get('in_channels', 5)
    img_size = mcfg.get('img_size', 224)
    patch_size = mcfg.get('patch_size', 16)
    emb_dim = mcfg.get('emb_dim', 128)
    depth = mcfg.get('depth', 6)
    num_heads = mcfg.get('num_heads', 4)
    mlp_dim = mcfg.get('mlp_dim', 256)
    num_classes = mcfg.get('num_classes', 13)
    dropout = mcfg.get('dropout', 0.1)
    return ViT(
        in_channels=in_channels,
        img_size=img_size,
        patch_size=patch_size,
        emb_dim=emb_dim,
        depth=depth,
        num_heads=num_heads,
        mlp_dim=mlp_dim,
        num_classes=num_classes,
        dropout=dropout
    ) 