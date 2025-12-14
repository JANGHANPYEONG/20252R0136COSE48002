import timm
import torch
import torch.nn as nn
import torch.nn.functional as F


class MoE(nn.module):
    """ 
    Top-1 Routing MoE for ViT MLP
    experts: list of expert MLPs
    gate: gating network (Linear)
    """
    def __init__(self, hidden_dim: int, ff_dim: int, num_experts: int):
        super().__init__()
        self.num_experts = num_experts

        # Expert MLPs
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, ff_dim),
                nn.GELU(),
                nn.Linear(ff_dim, hidden_dim),
            )
            for _ in range(num_experts)
        ])

        self.gate = nn.Linear(hidden_dim, num_experts)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, N, C = x.shape

        gate_scores = F.softmax(self.gate(x), dim=-1)
        expert_idx = gate_scores.argmax(dim=-1)
        out = torch.zeros_like(x).to(x.dtype)

        for expert_id, expert in enumerate(self.experts):
            mask = (expert_idx == expert_id)
            if mask.sum() == 0:
                continue

            x_e = x[mask]
            out_e = expert(x_e)

            out[mask] = out_e

        return out


def create_model(config: dict) -> nn.Module:
    mcfg = config['model']

    model = timm.create_model(
        model_name=mcfg['model_name'],
        pretrained=mcfg.get('pretrained', False),
    )

    patch_embed = model.patch_embed
    old_proj = patch_embed.proj
    embed_dim = old_proj.out_channels
    kernel_size = old_proj.kernel_size
    stride = old_proj.stride
    padding = old_proj.padding

    new_proj = nn.Conv2d(
        in_channels=mcfg["in_channels"],
        out_channels=embed_dim,
        kernel_size=kernel_size,
        stride=stride,
        padding=padding,
        bias=True
    )

    patch_embed.proj = new_proj

    for idx, block in enumerate(model.blocks):
        if not idx % 2:
            hidden_dim = block.norm1.normalized_shape[0]
            ff_dim = block.mlp.fc1.weight.shape[0]
            block.mlp = MoE(
                hidden_dim=hidden_dim,
                ff_dim=ff_dim,
                num_experts=mcfg['num_experts'],
            )

    if hasattr(model, 'head'):
        model.head = nn.Linear(embed_dim, mcfg['num_classes'])
    elif hasattr(model, 'classifier'):
        model.classifier = nn.Linear(embed_dim, mcfg['num_classes'])
    else:
        raise ValueError('No head found in the model.')
    
    return model