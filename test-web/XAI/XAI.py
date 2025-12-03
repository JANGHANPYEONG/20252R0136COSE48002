# =========================
# CONFIG
# =========================
MODEL_PATH  = "./best_model.pt"   # <-- 모델 state_dict 경로
IMG_FOLDER  = "./image"           # <-- 밴드 이미지 폴더(채널 수 = 파일 장수)
OUTPUT_DIR  = "./image_heatmap"   # <-- heat map 출력 폴더
USE_VAL_TRANSFORMS = False   # True면 get_val_transforms를 원본크기(H0,W0)로만 호출(=크롭 안 함)
TARGET_SIZE = None           # (H,W)로 강제 리사이즈하고 싶으면 (예: (224,224)), None이면 원본 그대로
MEAN = None                  # 채널별 정규화 필요시 리스트(길이=C). 예: [0.48, 0.36, ...]
STD  = None                  # overlay시 heatmap 비율
ALPHA = 1

# =========================
# IMPORTS
# =========================
import os, glob
from typing import Optional, Callable, Any, Tuple, List

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import cv2
import matplotlib.pyplot as plt


# =========================
# SpectrumNet
# =========================
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

    def forward(self, x):
        x = self.squeeze(x)
        out1 = self.expand1x1(x)
        out3 = self.expand3x3(x)
        return torch.cat([out1, out3], dim=1)

class SpectrumNet(nn.Module):
    def __init__(self, in_channels, num_classes, dropout=0.0):
        super(SpectrumNet, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels, 96, kernel_size=2, stride=1),
            nn.BatchNorm2d(96),
            nn.ReLU(inplace=True)
        )
        module_settings = [
            (16, 96, 32),
            (16, 96, 32),
            (32, 192, 64),  # + MaxPool
            (32, 192, 64),
            (48, 288, 96),
            (48, 288, 96),
            (64, 385, 128), # + MaxPool
            (64, 385, 128),
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
        return torch.flatten(x, 1)

# =========================
# Grad-CAM
# =========================

class GradCAM:
    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None
        self.fh = target_layer.register_forward_hook(self._forward_hook)
        self.bh = target_layer.register_full_backward_hook(self._backward_hook)

    def _forward_hook(self, module, inp, out):
        self.activations = out.detach()

    def _backward_hook(self, module, grad_in, grad_out):
        self.gradients = grad_out[0].detach()

    def remove(self):
        self.fh.remove()
        self.bh.remove()

    @torch.enable_grad()
    def generate(self, x, target_index=None, assume_regression=False, normalize=True, upsample=True):
        self.model.zero_grad(set_to_none=True)
        x = x.requires_grad_(True)
        out = self.model(x)

        if out.ndim == 2 and out.shape[1] > 1 and not assume_regression:
            idx = out.argmax(dim=1) if target_index is None else torch.as_tensor([int(target_index)]*out.shape[0], device=out.device)
            score = out.gather(1, idx.view(-1, 1)).sum()
        elif out.ndim == 2 and out.shape[1] >= 1:
            idx = 0 if target_index is None else int(target_index)
            score = out[:, idx].sum()
        else:
            score = out.sum()

        score.backward(retain_graph=False)

        A = self.activations
        G = self.gradients
        weights = G.mean(dim=(2, 3), keepdim=True)
        cam = (weights * A).sum(dim=1, keepdim=True)
        cam = F.relu(cam)

        if normalize:
            eps = 1e-8
            cam_min = cam.amin(dim=(2, 3), keepdim=True)
            cam_max = cam.amax(dim=(2, 3), keepdim=True)
            cam = (cam - cam_min) / (cam_max - cam_min + eps)

        if upsample:
            cam = F.interpolate(cam, size=x.shape[-2:], mode="bilinear", align_corners=False)
        return cam  # (B,1,H,W)


# =========================
# last Conv layer 찾기
# =========================
def find_last_conv_layer_excluding(model: nn.Module, exclude_names=("conv_final",)) -> nn.Module:
    last_conv = None
    for name, m in model.named_modules():
        if isinstance(m, nn.Conv2d) and all(ex not in name for ex in exclude_names):
            last_conv = m
    if last_conv is None:
        raise RuntimeError("No suitable Conv2d layer found for Grad-CAM.")
    return last_conv


# =========================
# 폴더 -> (C,H,W) 로더
# =========================
def load_multiband_image(folder: str, expected_channels: Optional[int] = None,
                         sort_key: Optional[Callable[[str], Any]] = None) -> torch.Tensor:
    exts = ("*.png", "*.jpg", "*.jpeg", "*.tif", "*.tiff", "*.bmp")
    paths = []
    for e in exts:
        paths.extend(glob.glob(os.path.join(folder, e)))
    if not paths:
        raise FileNotFoundError(f"No images found in: {folder}")

    paths = sorted(paths, key=sort_key) if sort_key else sorted(paths)
    if expected_channels is not None and len(paths) < expected_channels:
        raise ValueError(f"Expected >= {expected_channels} images, but found {len(paths)} in {folder}")

    use_paths = paths if expected_channels is None else paths[:expected_channels]

    bands, base_size = [], None
    for p in use_paths:
        im = Image.open(p).convert("L")
        if base_size is None:
            base_size = im.size
        elif im.size != base_size:
            im = im.resize(base_size, resample=Image.BILINEAR)
        bands.append(np.array(im, dtype=np.float32))

    x = np.stack(bands, axis=-1)  # (H,W,C)
    if x.max() > 1.0:
        x = x / 255.0
    return torch.from_numpy(x).permute(2, 0, 1).contiguous().float()  # (C,H,W)

# =========================
# CAM display
# =========================
def show_overlays(x_bchw: torch.Tensor,
                        cam_b1hw: torch.Tensor,
                        alpha: float = 0.45,
                        names: Optional[List[str]] = None,
                        save_dir: Optional[str] = None):
    """
    x_bchw: (1, C, H, W)
    cam_b1hw: (1, 1, H, W)
    """
    print(f"[XAI][Heatmap] 1. 입력 텐서 shape: {x_bchw.shape}, CAM shape: {cam_b1hw.shape}")
    x = x_bchw[0].detach().cpu().numpy()        # (C,H,W)
    cam = cam_b1hw[0,0].detach().cpu().numpy()  # (H,W)
    C, H, W = x.shape
    print(f"[XAI][Heatmap] 2. 채널 수: {C}, 이미지 크기: {H}x{W}")

    print("[XAI][Heatmap] 3. CAM 후처리 및 컬러맵 적용 중...")
    cam_u8 = (np.clip(cam, 0, 1) * 255).astype(np.uint8)
    cam_u8 = cv2.resize(cam_u8, (W, H), interpolation=cv2.INTER_LINEAR)
    heatmap = cv2.applyColorMap(cam_u8, cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    print("[XAI][Heatmap] 4. Matplotlib 시각화 준비 중...")
    plt.figure(figsize=(6, 6))
    plt.imshow(heatmap)
    plt.title("Grad-CAM Heatmap")
    plt.axis('off')
    plt.show()

    print("[XAI][Heatmap] 5. 파일 저장 중...")
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "heatmap.png")
        Image.fromarray(heatmap).save(save_path)
        print(f"[XAI][Heatmap] 저장 완료: {save_path}")


# =========================
# 실행부
# =========================
if __name__ == "__main__":
    print("[XAI] 1. 디바이스 설정 중...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[XAI] 사용 디바이스: {device}")

    print(f"[XAI] 2. 입력 이미지 로드 중: {IMG_FOLDER}")
    x_chw = load_multiband_image(IMG_FOLDER, expected_channels=None)
    C_in = x_chw.shape[0]
    x = x_chw.unsqueeze(0).to(device)  # (1,C,H,W)
    print(f"[XAI] 입력 이미지 shape: {x.shape}")

    print(f"[XAI] 3. 모델 로드 중: {MODEL_PATH}")
    ckpt = torch.load(MODEL_PATH, map_location=device)
    if isinstance(ckpt, nn.Module):
        model = ckpt.to(device).eval()
        print("[XAI] 모델 타입: nn.Module (직접 저장)")
    elif isinstance(ckpt, dict):
        sd = ckpt.get("state_dict", ckpt.get("model_state_dict", ckpt))
        if not isinstance(sd, dict):
            raise RuntimeError("Unsupported checkpoint structure. Expecting state_dict-like dict.")
        num_classes = None
        for k, v in sd.items():
            if k.endswith("conv_final.weight") and v.ndim == 4:
                num_classes = int(v.shape[0]); break
        if num_classes is None:
            for k, v in sd.items():
                if k.endswith("conv_final.bias") and v.ndim == 1:
                    num_classes = int(v.shape[0]); break
        if num_classes is None:
            raise RuntimeError("num_classes 추정 실패. conv_final.weight/bias가 없습니다.")
        model = SpectrumNet(in_channels=C_in, num_classes=num_classes, dropout=0.0).to(device)
        missing, unexpected = model.load_state_dict(sd, strict=False)
        if missing:   print("[XAI][warn] missing keys:", missing)
        if unexpected: print("[XAI][warn] unexpected keys:", unexpected)
        model.eval()
        print(f"[XAI] 모델 타입: state_dict, num_classes={num_classes}")
    else:
        raise RuntimeError("Unsupported checkpoint object type.")

    print("[XAI] 4. Grad-CAM 타깃 레이어 찾는 중...")
    target_layer = find_last_conv_layer_excluding(model, exclude_names=("conv_final",))
    print(f"[XAI] Grad-CAM 타깃 레이어: {target_layer}")

    print("[XAI] 5. 모델 예측 및 CAM 생성 중...")
    with torch.no_grad():
        logits = model(x)
    is_multiclass = (logits.ndim == 2 and logits.shape[1] > 1)
    pred_idx = int(logits.argmax(dim=1).item()) if is_multiclass else 0
    print(f"[XAI] 예측 결과: {logits.cpu().numpy()}")
    print(f"[XAI] 예측 클래스: {pred_idx}")

    cam_engine = GradCAM(model, target_layer)
    cam = cam_engine.generate(
        x,
        target_index=pred_idx,
        assume_regression=not is_multiclass,
        normalize=True,
        upsample=True
    )
    print("[XAI] 6. Heatmap 생성 및 저장 중...")
    show_overlays(x, cam, alpha=ALPHA, names=None, save_dir=OUTPUT_DIR)
    print(f"[XAI] 7. 완료! 결과는 {OUTPUT_DIR} 폴더에 저장됨.")