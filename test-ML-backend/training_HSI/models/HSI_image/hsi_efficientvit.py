import importlib
from typing import List, Optional, Tuple, Any
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------
# Utilities
# ---------------------------

def _to_2tuple(x):
    if isinstance(x, (list, tuple)):
        assert len(x) == 2
        return tuple(x)
    return (x, x)

def _linear_drop_path_rates(total_blocks: int, drop_path: float) -> List[float]:
    if total_blocks == 0 or drop_path <= 0:
        return [0.0] * total_blocks
    return [drop_path * i / (total_blocks - 1) for i in range(total_blocks)]

class DropPath(nn.Module):
    """Stochastic Depth"""
    def __init__(self, drop_prob: float = 0.):
        super().__init__()
        self.drop_prob = float(drop_prob)

    def forward(self, x):
        if self.drop_prob == 0. or not self.training:
            return x
        keep_prob = 1 - self.drop_prob
        shape = (x.shape[0],) + (1,) * (x.ndim - 1)
        random_tensor = keep_prob + torch.rand(shape, dtype=x.dtype, device=x.device)
        random_tensor.floor_()
        return x.div(keep_prob) * random_tensor


# ---------------------------
# Fallback EfficientViT-like Block
# (간이 구현: Conv-FFN + MHSA 유사 + FFN, Sandwich layout)
# ---------------------------

class MHSALite(nn.Module):
    """
    간단한 멀티헤드 셀프어텐션(이미지용).
    입력/출력: (B, H, W, C) 채널-라스트 형식으로 사용.
    """
    def __init__(self, dim, num_heads=4, qkv_bias=True, attn_drop=0.0, proj_drop=0.0):
        super().__init__()
        assert dim % num_heads == 0
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.scale = self.head_dim ** -0.5

        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(dim, dim)
        self.proj_drop = nn.Dropout(proj_drop)

    def forward(self, x):  # x: (B, H, W, C)
        B, H, W, C = x.shape
        N = H * W
        x_ = x.view(B, N, C)
        qkv = self.qkv(x_).reshape(B, N, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]   # (B, heads, N, head_dim)

        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)

        out = (attn @ v).transpose(1, 2).reshape(B, N, C)
        out = self.proj(out)
        out = self.proj_drop(out)
        out = out.view(B, H, W, C)
        return out

class FFN(nn.Module):
    def __init__(self, dim, mlp_ratio=4.0, drop=0.0, act_layer=nn.GELU):
        super().__init__()
        hidden = int(dim * mlp_ratio)
        self.fc1 = nn.Linear(dim, hidden)
        self.act = act_layer()
        self.drop1 = nn.Dropout(drop)
        self.fc2 = nn.Linear(hidden, dim)
        self.drop2 = nn.Dropout(drop)

    def forward(self, x):  # (B,H,W,C)
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop1(x)
        x = self.fc2(x)
        x = self.drop2(x)
        return x

class EfficientViTBlockFallback(nn.Module):
    """
    EfficientViT block 대체용 간이 블록.
    LayerNorm(채널라스트) + FFN -> MHSA -> FFN (sandwich)
    """
    def __init__(self, dim, num_heads, mlp_ratio=4.0, drop=0.0, attn_drop=0.0, drop_path=0.0, norm_eps=1e-6):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim, eps=norm_eps)
        self.pre_ffn = FFN(dim, mlp_ratio=mlp_ratio, drop=drop)
        self.norm2 = nn.LayerNorm(dim, eps=norm_eps)
        self.attn = MHSALite(dim, num_heads=num_heads, attn_drop=attn_drop, proj_drop=drop)
        self.norm3 = nn.LayerNorm(dim, eps=norm_eps)
        self.post_ffn = FFN(dim, mlp_ratio=mlp_ratio, drop=drop)
        self.drop_path = DropPath(drop_path) if drop_path > 0 else nn.Identity()

    def forward(self, x):  # x: (B,C,H,W) -> 채널라스트로 변환
        x = x.permute(0, 2, 3, 1)  # (B,H,W,C)

        y = self.norm1(x)
        y = self.pre_ffn(y)
        x = x + self.drop_path(y)

        y = self.norm2(x)
        y = self.attn(y)
        x = x + self.drop_path(y)

        y = self.norm3(x)
        y = self.post_ffn(y)
        x = x + self.drop_path(y)

        x = x.permute(0, 3, 1, 2)  # (B,C,H,W)
        return x


# ---------------------------
# Patch/Stem & Head
# ---------------------------

class ConvStem(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, stride: int = 2, eps: float = 1e-5):
        super().__init__()
        self.conv = nn.Conv2d(in_ch, out_ch, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn = nn.BatchNorm2d(out_ch, eps=eps)
        self.act = nn.GELU()

    def forward(self, x):
        return self.act(self.bn(self.conv(x)))

class ClassRegHead(nn.Module):
    def __init__(self, in_dim: int, num_classes: int, num_regression_targets: int, dropout: float = 0.0):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
        cls_out = num_classes if num_classes > 0 else 0
        reg_out = num_regression_targets if num_regression_targets > 0 else 0
        self.cls = nn.Linear(in_dim, cls_out) if cls_out > 0 else None
        self.reg = nn.Linear(in_dim, reg_out) if reg_out > 0 else None

    def forward(self, x):
        x = self.pool(x).flatten(1)     # (B,C)
        x = self.dropout(x)
        cls = self.cls(x) if self.cls is not None else None
        reg = self.reg(x) if self.reg is not None else None

        # 이전 예시와 동일하게 하나의 Tensor로 반환
        if cls is None and reg is None:
            return torch.empty(x.size(0), 0, device=x.device)
        if cls is None:
            return reg
        if reg is None:
            return cls
        return torch.cat([cls, reg], dim=1)


# ---------------------------
# EfficientViT Wrapper
# ---------------------------

class EfficientViTWrapper(nn.Module):
    """
    - external_impl가 주어지면 해당 레포의 EfficientViT block/스테이지를 사용
    - 아니면 Fallback 블록으로 구성
    """
    def __init__(
        self,
        in_channels: int,
        image_size: Tuple[int, int],
        embed_dims: List[int],
        depths: List[int],
        num_heads: List[int],
        mlp_ratios: List[float],
        drop: float = 0.0,
        attn_drop: float = 0.0,
        drop_path: float = 0.0,
        norm_eps: float = 1e-6,
        stem_cfg: Optional[dict] = None,
        head_cfg: Optional[dict] = None,
        use_abs_pos_emb: bool = False,
        num_classes: int = 0,
        num_regression_targets: int = 0,
        external_impl: Optional[dict] = None,
    ):
        super().__init__()

        H, W = image_size
        self.use_abs_pos_emb = use_abs_pos_emb
        self.image_size = (H, W)

        # Stem
        stem_out = stem_cfg.get("out_channels", 32) if stem_cfg else 32
        stem_stride = stem_cfg.get("stride", 2) if stem_cfg else 2
        stem_bn_eps = stem_cfg.get("bn_eps", 1e-5) if stem_cfg else 1e-5
        self.stem = ConvStem(in_channels, stem_out, stride=stem_stride, eps=stem_bn_eps)

        # Stage chans
        stage_dims = [stem_out] + list(embed_dims)

        # Absolute Pos Emb (선택 사항)
        if self.use_abs_pos_emb:
            # 간단한 learnable 2D pos emb (stage 1 입력 기준)
            self.pos_emb = nn.Parameter(torch.zeros(1, stage_dims[1], H // stem_stride, W // stem_stride))
            nn.init.trunc_normal_(self.pos_emb, std=0.02)
        else:
            self.pos_emb = None

        # External EfficientViT block (Cream repo) 준비
        block_cls = None
        if external_impl and external_impl.get("module") and external_impl.get("class_name"):
            try:
                ext_mod = importlib.import_module(external_impl["module"])
                block_cls = getattr(ext_mod, external_impl["class_name"])
            except Exception as e:
                print(f"[EfficientViTWrapper] External impl import failed: {e}. Use fallback block.")

        # DropPath rates 전개
        total_blocks = sum(depths)
        dpr = _linear_drop_path_rates(total_blocks, drop_path)
        dp_cursor = 0

        stages = []
        in_dim = stage_dims[0]
        for si, (out_dim, depth, nhead, mlp_ratio) in enumerate(zip(embed_dims, depths, num_heads, mlp_ratios)):
            stage = []
            # 다운샘플(간단 conv)로 stage 전환
            stage.append(nn.Conv2d(in_dim, out_dim, kernel_size=3, stride=2, padding=1, bias=False))
            stage.append(nn.BatchNorm2d(out_dim, eps=1e-5))
            stage.append(nn.GELU())
            in_dim = out_dim

            for bi in range(depth):
                dp = dpr[dp_cursor] if dp_cursor < len(dpr) else 0.0
                dp_cursor += 1
                if block_cls is not None:
                    # Cream repo의 블록 시그니처에 맞춰 kwargs 전달 (필요 시 수정)
                    blk = block_cls(dim=out_dim, num_heads=nhead, mlp_ratio=mlp_ratio,
                                    drop=drop, attn_drop=attn_drop, drop_path=dp, norm_eps=norm_eps)
                else:
                    blk = EfficientViTBlockFallback(dim=out_dim, num_heads=nhead,
                                                    mlp_ratio=mlp_ratio, drop=drop,
                                                    attn_drop=attn_drop, drop_path=dp, norm_eps=norm_eps)
                stage.append(blk)

            stages.append(nn.Sequential(*stage))

        self.stages = nn.ModuleList(stages)
        head_dropout = head_cfg.get("dropout", 0.0) if head_cfg else 0.0
        self.head = ClassRegHead(in_dim, num_classes, num_regression_targets, dropout=head_dropout)

    def forward(self, x):
        # (B,C,H,W)
        x = self.stem(x)
        if self.pos_emb is not None:
            # 첫 stage 입력에만 pos_emb 더해줌
            # 크기가 다르면 보간
            if x.shape[2:] != self.pos_emb.shape[2:]:
                pos = F.interpolate(self.pos_emb, size=x.shape[2:], mode="bicubic", align_corners=False)
            else:
                pos = self.pos_emb
            x = x + pos

        for stage in self.stages:
            x = stage(x)
        out = self.head(x)
        return out


# ---------------------------
# Factory
# ---------------------------

def create_model(config: dict) -> nn.Module:
    """
    config["model"] 섹션을 사용해 EfficientViT 기반 모델을 생성하고 반환.
    출력은 (B, num_classes + num_regression_targets) 형태의 하나의 Tensor.
    """
    mcfg = config["model"]

    # 필수/기본값
    in_channels = mcfg.get("in_channels", 3)
    num_classes = mcfg.get("num_classes", 0)
    num_regression_targets = mcfg.get("num_regression_targets", 0)

    image_size = tuple(mcfg.get("image_size", [224, 224]))
    embed_dims = mcfg.get("embed_dims", [64, 128, 192, 256])
    depths = mcfg.get("depths", [2, 2, 6, 2])
    num_heads = mcfg.get("num_heads", [2, 4, 6, 8])
    mlp_ratios = mcfg.get("mlp_ratios", [4.0, 4.0, 4.0, 4.0])

    drop = float(mcfg.get("dropout", 0.0))
    attn_drop = float(mcfg.get("attn_dropout", 0.0))
    drop_path = float(mcfg.get("drop_path", 0.0))
    norm_eps = float(mcfg.get("norm_eps", 1e-6))

    use_abs_pos_emb = bool(mcfg.get("use_abs_pos_emb", False))
    stem_cfg = mcfg.get("stem", {"out_channels": 32, "stride": 2, "bn_eps": 1e-5})
    head_cfg = mcfg.get("head", {"pool": "global_avg", "classifier_bias": True, "label_smoothing": 0.0, "dropout": 0.0})

    external_impl = mcfg.get("external_impl", None)
    # 예시:
    # "external_impl": {
    #   "module": "EfficientViT.classification.model.efficientvit",  # PYTHONPATH에 이 모듈이 있도록
    #   "class_name": "EfficientViTBlock"  # 해당 파일 내 블록 클래스명
    # }

    model = EfficientViTWrapper(
        in_channels=in_channels,
        image_size=_to_2tuple(image_size),
        embed_dims=embed_dims,
        depths=depths,
        num_heads=num_heads,
        mlp_ratios=mlp_ratios,
        drop=drop,
        attn_drop=attn_drop,
        drop_path=drop_path,
        norm_eps=norm_eps,
        stem_cfg=stem_cfg,
        head_cfg=head_cfg,
        use_abs_pos_emb=use_abs_pos_emb,
        num_classes=num_classes,
        num_regression_targets=num_regression_targets,
        external_impl=external_impl,
    )

    # Freeze stages (옵션)
    freeze_stages = int(mcfg.get("freeze_stages", 0))
    if freeze_stages > 0:
        # stem + 앞쪽 N개 stage 고정
        modules_to_freeze = [model.stem] + [model.stages[i] for i in range(min(freeze_stages, len(model.stages)))]
        for m in modules_to_freeze:
            for p in m.parameters():
                p.requires_grad = False

    return model