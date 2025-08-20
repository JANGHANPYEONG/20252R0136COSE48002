from typing import Optional, Any, List, Dict, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2
import os 

# RGB 변환 함수들 (주석 처리됨 - RGB 데이터가 없을 때 대비)
def hsi_to_rgb_simple(image_cube_hwc: np.ndarray, wavelengths: Optional[List[float]] = None) -> np.ndarray:
    """
    분광 데이터를 RGB로 변환하는 간단한 방법
    현재는 첫 3개 채널을 사용하여 RGB를 근사
    향후 적절한 스펙트럴 응답 함수나 컬러 매칭 함수를 사용할 수 있음
    
    Args:
        image_cube_hwc: (H, W, C) 분광 이미지 큐브
        wavelengths: 파장 정보 (현재 미사용)
    
    Returns:
        rgb_image: (H, W, 3) RGB 이미지 [0, 255] uint8
    """
    H, W, C = image_cube_hwc.shape
    
    if C >= 3:
        # 첫 3개 채널을 RGB로 사용
        rgb_channels = image_cube_hwc[:, :, :3]
    else:
        # 채널이 3개 미만이면 반복하여 채움
        rgb_channels = np.zeros((H, W, 3), dtype=image_cube_hwc.dtype)
        for i in range(3):
            rgb_channels[:, :, i] = image_cube_hwc[:, :, i % C]
    
    # 정규화 및 uint8 변환
    rgb_norm = (rgb_channels - rgb_channels.min()) / (rgb_channels.max() - rgb_channels.min() + 1e-8)
    rgb_uint8 = (rgb_norm * 255).astype(np.uint8)
    
    return rgb_uint8

def create_overlay_image(base_image: np.ndarray, cam: np.ndarray, alpha: float = 0.35) -> np.ndarray:
    """
    기본 이미지와 CAM을 오버레이하여 최종 이미지 생성
    
    Args:
        base_image: (H, W, 3) RGB 기본 이미지 [0, 255] uint8
        cam: (H, W) CAM 배열 [0, 1] float32
        alpha: 오버레이 투명도 (0: CAM 없음, 1: CAM만)
    
    Returns:
        overlay_image: (H, W, 3) 오버레이된 RGB 이미지 [0, 255] uint8
    """
    H, W = cam.shape
    
    # 기본 이미지를 CAM 크기에 맞춤
    if base_image.shape[:2] != (H, W):
        base_resized = cv2.resize(base_image, (W, H))
    else:
        base_resized = base_image.copy()
    
    # CAM을 컬러맵으로 변환 (COLORMAP_JET 사용)
    cam_u8 = (np.clip(cam, 0, 1) * 255).astype(np.uint8)
    cam_color = cv2.applyColorMap(cam_u8, cv2.COLORMAP_JET)  # BGR
    cam_color_rgb = cv2.cvtColor(cam_color, cv2.COLOR_BGR2RGB)  # RGB로 변환
    
    # 오버레이 생성
    overlay = ((1 - alpha) * base_resized.astype(np.float32) + 
               alpha * cam_color_rgb.astype(np.float32))
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)
    
    return overlay 

# GradCAM class 
class GradCAM:
    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None
        self.fh = target_layer.register_forward_hook(self._forward_hook)
        self.bh = target_layer.register_full_backward_hook(self._backward_hook)

    def _forward_hook(self, module, inp, out):
        self.activations = out # (B, C, H, W)
    
    def _backward_hook(self, module, grad_in, grad_out):
        self.gradients = grad_out[0]
    
    def remove(self):
        self.fh.remove()
        self.bh.remove()
    
    @torch.enable_grad()
    def generate(
        self,
        x: torch.Tensor, #(1, C, H, W) : input tensor
        outputs, # model fresh forward outputs (Tensor or dict)
                 # outputs = {
                 #  "classification": tensor([...]),
                 #  "regression": tensor([...])
                 # }
        *, # 이후 인자는 keyword 전용
        task: str, # 'classification' 혹은 'regression'
        index: int, # CAM 뽑을 target index
    ):
        """
        returns: (1, 1, H, W) tensor, [0, 1] 내 정규화 
        """
        self.model.zero_grad(set_to_none=True)

        # score 선택 (특정 클래스 선택)
        is_cls = (task == "classification")

        if isinstance(outputs, dict): # multi output 모델 
            if is_cls: # 분류 task
                logits = outputs.get("classification", None)
                if logits is None:
                    raise RuntimeError("분류 task인데 outputs에서 인덱싱 불가")
                score = logits[0, index]
            else: # 회귀 task
                y = outputs.get("regression", None)
                if y is None:
                    raise RuntimeError("회귀 task인데 outputs에서 인덱싱 불가")
                score = y[0, index]
        else: # 단일 출력 텐서
            score = outputs[0, index]

        # GradCAM score
        score.backward(retain_graph=False)

        A = self.activations # (1, C, H, W)
        dA = self.gradients  # (1, C, H, W)
        w = dA.mean(dim=(2, 3), keepdim=True) # (1, C, 1, 1)
        cam = (w * A).sum(dim=1, keepdim=True) # (1, 1, H, W)
        cam = F.relu(cam)

        return cam
    
# task 추정
@torch.no_grad()
def _infer_task_from_outputs(outputs) -> str:
    if isinstance(outputs, dict):
        if "classification" in outputs:
            return "classification"
        if "regression" in outputs:
            return "regression"
    else:
        if outputs.ndim == 2 and outputs.shape[1] > 1:
            return "classification"
        return "regression"

# 마지막 conv 레이어 찾는 함수 (1x1 제외)
def find_last_conv_layer(model: nn.Module):
    last_conv = None
    for name, m in model.named_modules():
        if isinstance(m, nn.Conv2d):
            ks = m.kernel_size
            if isinstance(ks, int):
                kH = kW = ks
            else:
                kH, kW = ks
            if not (kH == 1 and kW == 1):
                last_conv = m
    if last_conv is None:
        raise RuntimeError("No conv2d layer for Grad-CAM")
    return last_conv

# CAM 배열 생성
def generate_cam_arrays(
    model: nn.Module,
    image_tensor_bchw: torch.Tensor,   # (1, C, H, W) on same device as model
    outputs,                           # forward outputs (dict or tensor) - 참고용
    *,
    task: str,                         # 'classification' | 'regression'
    target_index: Optional[int],
    target_layer_name: Optional[str],
    image_cube_hwc: np.ndarray,        # (H, W, C) float32
    wavelengths: Optional[List[float]],
    rgb_strategy: str = "auto",
    alpha: float = 0.35
):
    # 타깃 레이어 선택
    if target_layer_name:
        layer = model
        for part in target_layer_name.split('.'):
            layer = layer[int(part)] if part.isdigit() else getattr(layer, part)
        used_layer = target_layer_name
    else:
        layer = find_last_conv_layer(model)
        used_layer = "(auto-last-conv-non1x1)"

    # fresh forward with hooks ON
    engine = GradCAM(model, layer)
    try:
        image_tensor_bchw = image_tensor_bchw.requires_grad_(True)
        fresh_out = model(image_tensor_bchw)

        # task/target index 결정
        is_cls = (task == "classification")
        if target_index is not None:
            used_index = int(target_index)
        else:
            if isinstance(fresh_out, dict):
                if is_cls:
                    logits = fresh_out.get("classification", None)
                    if logits is None:
                        task = _infer_task_from_outputs(fresh_out)
                        is_cls = (task == "classification")
                        logits = fresh_out["classification"] if is_cls else fresh_out["regression"]
                    with torch.no_grad():
                        probs = torch.sigmoid(logits)[0]
                        used_index = int(torch.argmax(probs).item())
                else:
                    used_index = 0
            else:
                if is_cls:
                    with torch.no_grad():
                        probs = torch.sigmoid(fresh_out)[0]
                        used_index = int(torch.argmax(probs).item())
                else:
                    used_index = 0

        # CAM 생성
        cam_b1hw = engine.generate(
            image_tensor_bchw,
            fresh_out,
            task=task,
            index=used_index,
        )  # (1,1,h,w)
    finally:
        engine.remove()

    # 입력 샘플 크기로 업샘플링 (고품질 보간 사용)
    _, _, H, W = image_tensor_bchw.shape
    if cam_b1hw.shape[-2:] != (H, W):
        # bicubic 보간으로 더 선명한 업샘플링
        cam_b1hw = F.interpolate(cam_b1hw, size=(H, W), mode="bicubic", align_corners=False)


    # 정규화 + 업샘플
    cam = cam_b1hw[0, 0]                       # (h, w), torch
    cam = cam - cam.min()
    if cam.max().item() > 0:
        cam = cam / cam.max()
    cam = cam.detach().cpu().numpy().astype(np.float32)  # [0,1]
    
    # 첫 번째 채널을 기본 이미지로 사용 (그레이스케일)
    first_band = image_cube_hwc[:, :, 0]  # (H, W)
    
    # 그레이스케일을 RGB로 변환
    first_band_norm = (first_band - first_band.min()) / (first_band.max() - first_band.min() + 1e-8)
    first_band_rgb = np.stack([first_band_norm] * 3, axis=-1)  # (H, W, 3)
    first_band_rgb = (first_band_rgb * 255).astype(np.uint8)
    
    # RGB 변환 시도 (주석 처리됨 - RGB 데이터가 없을 때 대비)
    # try:
    #     if rgb_strategy == "spectral" and wavelengths:
    #         rgb_image = hsi_to_rgb_spectral_matching(image_cube_hwc, wavelengths)
    #     else:
    #         rgb_image = hsi_to_rgb_simple(image_cube_hwc, wavelengths)
    # except Exception as e:
    #     print(f"RGB 변환 실패, 첫 번째 채널 사용: {e}")
    #     rgb_image = first_band_rgb
    
    # 현재는 첫 번째 채널만 사용 (RGB 데이터 없음)
    rgb_image = first_band_rgb
    
    # CAM과 기본 이미지의 크기를 맞춤
    if cam.shape != rgb_image.shape[:2]:
        cam_resized = cv2.resize(cam, (rgb_image.shape[1], rgb_image.shape[0]))
    else:
        cam_resized = cam
    
    # 오버레이 이미지 생성
    overlay_image = create_overlay_image(rgb_image, cam_resized, alpha)
    
    return {
        "cam": cam_resized,                     # (H, W) float32 [0,1]
        "first_band_rgb": rgb_image,            # (H, W, 3) uint8, 첫 번째 채널 RGB
        "overlay": overlay_image,               # (H, W, 3) uint8, 오버레이된 이미지
        "target_index": used_index,
        "layer": used_layer,
        "task": task
    }

def _make_rgb_from_cube(cube_hwc):
    C = cube_hwc.shape[-1]
    if C >= 3:
        rgb = cube_hwc[..., :3]
    else:
        # 1밴드 → gray 3채널, 2밴드 → 마지막 채널 복제
        if C == 1:
            rgb = np.repeat(cube_hwc, 3, axis=-1)
        else:  # C==2
            rgb = np.concatenate([cube_hwc, cube_hwc[..., -1:]], axis=-1)
    # 정규화
    rgb = (rgb - rgb.min()) / (rgb.max() - rgb.min() + 1e-6)
    return (rgb * 255).astype(np.uint8)

def save_cam_arrays(
    cam: np.ndarray,                   # (H, W) float32 [0,1]
    rgb: Optional[np.ndarray] = None,  # (H, W, 3) uint8, RGB
    overlay: Optional[np.ndarray] = None, # (H, W, 3) uint8, RGB
    *,
    save_dir: str = "xai_outputs",
    basename: str = "gradcam",
    save_heatmap: bool = False,
    save_rgb: bool = False, # 첫 번째 채널 저장
    save_overlay: bool = True, # overlay 저장 
):
    """
    CAM / 원본 / Overlay를 파일로 저장합니다.
    CAM은 COLORMAP_JET 적용된 히트맵으로 저장합니다.
    Returns: {"heatmap": path or None, "rgb": path or None, "overlay": path or None}
    """
    os.makedirs(save_dir, exist_ok=True)
    paths = {"heatmap": None, "rgb": None, "overlay": None}

    # CAM 히트맵 저장
    if save_heatmap:
        cam_u8 = (np.clip(cam, 0, 1) * 255).astype(np.uint8)
        cam_color = cv2.applyColorMap(cam_u8, cv2.COLORMAP_JET)  # BGR
        p = os.path.join(save_dir, f"{basename}_heatmap.png")
        cv2.imwrite(p, cam_color)
        paths["heatmap"] = p

    # RGB 저장 (옵션)
    if save_rgb and rgb is not None:
        p = os.path.join(save_dir, f"{basename}_rgb.png")
        cv2.imwrite(p, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        paths["rgb"] = p

    # Overlay 저장 (옵션)
    if save_overlay and overlay is not None:
        p = os.path.join(save_dir, f"{basename}_overlay.png")
        cv2.imwrite(p, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        paths["overlay"] = p

    return paths

    # CAM 히트맵 저장
    # Heatmap 저장
    if save_heatmap:
        p = os.path.join(save_dir, f"{basename}_heatmap.png")
        hm = (cam * 255).astype(np.uint8)

        hm_color = cv2.applyColorMap(hm, cv2.COLORMAP_JET)

        if cube_hwc is not None:
            rgb = _make_rgb_from_cube(cube_hwc)
            hm_color = cv2.resize(hm_color, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(p, hm_color)
        paths["heatmap"] = p

    # RGB 저장 (옵션)
    if save_rgb and cube_hwc is not None:
        rgb = _make_rgb_from_cube(cube_hwc)
        p = os.path.join(save_dir, f"{basename}_rgb.png")
        cv2.imwrite(p, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        paths["rgb"] = p

    # Overlay 저장 (옵션)
    if save_overlay and cube_hwc is not None:
        rgb = _make_rgb_from_cube(cube_hwc)
        heatmap_color = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
        
        if heatmap_color.shape[:2] != rgb.shape[:2]:
            heatmap_color = cv2.resize(heatmap_color, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_CUBIC)

        overlay = cv2.addWeighted(rgb, 0.6, heatmap_color, 0.4, 0)
        p = os.path.join(save_dir, f"{basename}_overlay.png")
        cv2.imwrite(p, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        paths["overlay"] = p

    return paths

def cam_to_png_bytes(cam: np.ndarray) -> bytes:
    """
    CAM 배열(float32 [0,1])을 PNG 바이트로 변환
    """
    cam_u8 = (np.clip(cam, 0, 1) * 255).astype(np.uint8)
    cam_color = cv2.applyColorMap(cam_u8, cv2.COLORMAP_JET)  # BGR
    success, buf = cv2.imencode(".png", cam_color)
    if not success:
        raise RuntimeError("PNG 인코딩 실패")
    return buf.tobytes()


# ------------------- attention 기반 XAI -----------------
# attention class
class _AttnCollector:
    def __init__(self):
        self.attns = []       # list of (B, H, N, N) 또는 (B, N, N)도 허용 → 표준화
        self.grad_attns = []  # list of same-shape grads or None

    def _standardize(self, t):
        if t is None:
            return None
        # 허용 형태: (B, H, N, N) 또는 (B, N, N)
        if t.dim() == 3:                  # (B, N, N) → (B, 1, N, N)
            t = t.unsqueeze(1)
        elif t.dim() == 4:
            pass
        else:
            raise RuntimeError(f"Unexpected attention shape: {tuple(t.shape)}")

        # 비정사각형이면 min 축으로 크롭하여 정사각형으로 맞춤
        Nq, Nk = t.shape[-2], t.shape[-1]
        if Nq != Nk:
            m = min(Nq, Nk)
            t = t[..., :m, :m]
        return t

    def fwd(self, module, inp, out):
        attn = getattr(module, "attn", None)
        if attn is None:
            if isinstance(out, (tuple, list)) and len(out) >= 2 and out[-1] is not None:
                attn = out[-1]
            elif isinstance(out, dict) and "attn" in out:
                attn = out["attn"]
        if attn is None:
            raise RuntimeError(f"Cannot find attention probs in module: {module.__class__.__name__}")
        if attn.dim() >= 2:
            attn = attn.softmax(dim=-1)
        attn = self._standardize(attn)
        self.attns.append(attn)

    def bwd(self, module, grad_input, grad_output):
        g = None
        if len(grad_output) >= 2 and grad_output[-1] is not None:
            g = grad_output[-1]
        elif len(grad_output) >= 1:
            g = grad_output[0]
        self.grad_attns.append(self._standardize(g))
    
def _find_vit_attention_modules(model: nn.Module):
    mods = []
    for name, m in model.named_modules():
        # MultiheadAttention 유사 구조 탐색
        if hasattr(m, "num_heads") and (
            hasattr(m, "attn_drop") or hasattr(m, "dropout")
        ):
            mods.append(m)
        elif name.endswith(".attn") and hasattr(m, "attn_drop"):
            mods.append(m)
    return mods

def _rollout_grad_attn(attns, grads, add_residual=True, eps=1e-6):
    assert len(attns) == len(grads) and len(attns) > 0

    def match_shape(A, G):
        if G is None:
            return None
        # A, G 모두 (B, H, N, N) 보장되어야 함. 아닐 경우 보정.
        if G.dim() == 3:            # (B, N, N) -> (B,1,N,N)
            G = G.unsqueeze(1)
        if A.dim() == 3:
            A = A.unsqueeze(1)

        # 마지막 두 축이 다르면 교집합으로 크롭
        N_A = A.shape[-1]
        N_G = G.shape[-1]
        if (A.shape[-2] != A.shape[-1]) or (G.shape[-2] != G.shape[-1]):
            mA = min(A.shape[-2], A.shape[-1])
            A = A[..., :mA, :mA]
        if (G.shape[-2] != G.shape[-1]):
            mG = min(G.shape[-2], G.shape[-1])
            G = G[..., :mG, :mG]

        # 다시 한 번 A, G의 N 맞추기
        N = min(A.shape[-1], G.shape[-1])
        if (A.shape[-2] != N) or (A.shape[-1] != N):
            A = A[..., :N, :N]
        if (G.shape[-2] != N) or (G.shape[-1] != N):
            G = G[..., :N, :N]
        return A, G

    mats = []
    for A, G in zip(attns, grads):
        if A is None:
            continue
        # 표준화 재확인
        if A.dim() == 3: A = A.unsqueeze(1)  # (B,1,N,N)
        if (A.shape[-2] != A.shape[-1]):     # 정사각형 강제
            m = min(A.shape[-2], A.shape[-1])
            A = A[..., :m, :m]

        if G is None:
            GwA = F.relu(A)
        else:
            A, G = match_shape(A, G)
            GwA = F.relu(A * F.relu(G))

        M = GwA.mean(dim=1)  # (B, N, N)  헤드 평균
        M = M / (M.sum(dim=-1, keepdim=True) + eps)
        if add_residual:
            I = torch.eye(M.size(-1), device=M.device, dtype=M.dtype).unsqueeze(0)
            M = M + I
            M = M / (M.sum(dim=-1, keepdim=True) + eps)
        mats.append(M)

    R = mats[0]
    for L in mats[1:]:
        R = torch.bmm(R, L)
    return R[:, 0]  # (B, N)

@torch.enable_grad()
def generate_attention_arrays(
    model: nn.Module,
    image_tensor_bchw: torch.Tensor,   # (1,C,H,W)
    outputs,                           # fresh forward 할 것이므로 형식 무관
    *,
    task: str,                         # 'classification' | 'regression'
    target_index: Optional[int],
    assume_cls_token: bool = True,
    image_cube_hwc: Optional[np.ndarray] = None,  # 추가: 원본 이미지 큐브
    wavelengths: Optional[List[float]] = None,     # 추가: 파장 정보
    alpha: float = 0.35,                          # 추가: 오버레이 투명도
) -> Dict[str, Any]:
    device = image_tensor_bchw.device
    B, C, H, W = image_tensor_bchw.shape
    assert B == 1, "batch=1만 지원"

    attn_mods = _find_vit_attention_modules(model)
    if not attn_mods:
        raise RuntimeError("ViT attention 모듈(block.attn)을 찾지 못했습니다.")

    collector = _AttnCollector()
    hooks = []
    for m in attn_mods:
        hooks.append(m.register_forward_hook(collector.fwd))
        hooks.append(m.register_full_backward_hook(collector.bwd))

    try:
        x = image_tensor_bchw.requires_grad_(True)
        fresh_out = model(x)
        is_cls = (task == "classification")

        # target 자동 결정
        if target_index is None:
            t = fresh_out["classification"] if (isinstance(fresh_out, dict) and is_cls) \
                else fresh_out["regression"] if isinstance(fresh_out, dict) else fresh_out
            if is_cls:
                with torch.no_grad():
                    target_index = int(torch.argmax(torch.sigmoid(t)[0]).item())
            else:
                target_index = 0

        score_t = fresh_out["classification"][0, target_index] if (isinstance(fresh_out, dict) and is_cls) \
            else fresh_out["regression"][0, target_index] if isinstance(fresh_out, dict) \
            else fresh_out[0, target_index]

        model.zero_grad(set_to_none=True)
        score_t.backward(retain_graph=False)

        if not collector.attns:
            raise RuntimeError("attention 텐서 수집 실패")

        relev_tokens = _rollout_grad_attn(collector.attns, collector.grad_attns)  # (B,N)
        relev_tokens = relev_tokens[0]  # (N,)

        # N = 1 + Hp*Wp (CLS 포함 가정)
        if assume_cls_token:
            img_tokens = relev_tokens[1:]
        else:
            img_tokens = relev_tokens
        N_img = img_tokens.numel()
        if N_img == 0:  # 엣지 케이스 방지
            cam = torch.ones((1,1,H,W), device=device)[0,0].detach().cpu().numpy().astype(np.float32)
            result = {"cam": cam, "target_index": int(target_index),
                    "layer": "attn-rollout", "task": task}
            # 기본 이미지 정보도 포함
            if image_cube_hwc is not None:
                first_band = image_cube_hwc[:, :, 0]
                first_band_norm = (first_band - first_band.min()) / (first_band.max() - first_band.min() + 1e-8)
                first_band_rgb = np.stack([first_band_norm] * 3, axis=-1)
                first_band_rgb = (first_band_rgb * 255).astype(np.uint8)
                overlay_image = create_overlay_image(first_band_rgb, cam, alpha)
                result["first_band_rgb"] = first_band_rgb
                result["overlay"] = overlay_image
            return result
        side = int(round(np.sqrt(float(N_img))))
        Hp, Wp = side, int(np.ceil(N_img / max(side, 1)))
        img_tokens = img_tokens[:Hp*Wp]

        grid = img_tokens.reshape(Hp, Wp)
        grid = grid - grid.min()
        if grid.max().item() > 0:
            grid = grid / grid.max()
        # bicubic 보간으로 더 선명한 업샘플링
        cam = F.interpolate(grid.unsqueeze(0).unsqueeze(0), size=(H, W),
                            mode="bicubic", align_corners=False)[0, 0]
        cam = cam.detach().cpu().numpy().astype(np.float32)

        result = {"cam": cam, "target_index": int(target_index),
                "layer": "attn-rollout", "task": task}
        
        # 원본 이미지 큐브가 있으면 첫 번째 채널과 오버레이 생성
        if image_cube_hwc is not None:
            # 첫 번째 채널을 기본 이미지로 사용
            first_band = image_cube_hwc[:, :, 0]  # (H, W)
            
            # 그레이스케일을 RGB로 변환
            first_band_norm = (first_band - first_band.min()) / (first_band.max() - first_band.min() + 1e-8)
            first_band_rgb = np.stack([first_band_norm] * 3, axis=-1)  # (H, W, 3)
            first_band_rgb = (first_band_rgb * 255).astype(np.uint8)
            
            # RGB 변환 시도 (주석 처리됨)
            # try:
            #     if wavelengths:
            #         rgb_image = hsi_to_rgb_spectral_matching(image_cube_hwc, wavelengths)
            #     else:
            #         rgb_image = hsi_to_rgb_simple(image_cube_hwc, wavelengths)
            # except Exception as e:
            #     print(f"RGB 변환 실패, 첫 번째 채널 사용: {e}")
            #     rgb_image = first_band_rgb
            
            # 현재는 첫 번째 채널만 사용
            rgb_image = first_band_rgb
            
            # CAM과 기본 이미지의 크기를 맞춤
            if cam.shape != rgb_image.shape[:2]:
                cam_resized = cv2.resize(cam, (rgb_image.shape[1], rgb_image.shape[0]))
            else:
                cam_resized = cam
            
            # 오버레이 이미지 생성
            overlay_image = create_overlay_image(rgb_image, cam_resized, alpha)
            
            result["first_band_rgb"] = rgb_image
            result["overlay"] = overlay_image
            result["cam"] = cam_resized  # 크기 조정된 CAM 사용

        return result
    finally:
        for h in hooks:
            h.remove()