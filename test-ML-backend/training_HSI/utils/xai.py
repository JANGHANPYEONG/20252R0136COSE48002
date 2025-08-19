from typing import Optional, Any, List, Dict, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2
import os 

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

    # 입력 샘플 크기로 업샘플링
    _, _, H, W = image_tensor_bchw.shape
    if cam_b1hw.shape[-2:] != (H, W):
        cam_b1hw = F.interpolate(cam_b1hw, size=(H, W), mode="bilinear", align_corners=False)


    # 정규화 + 업샘플
    cam = cam_b1hw[0, 0]                       # (h, w), torch
    cam = cam - cam.min()
    if cam.max().item() > 0:
        cam = cam / cam.max()
    cam = cam.detach().cpu().numpy().astype(np.float32)  # [0,1]
    return {
        "cam": cam,                     # (H, W) float32 [0,1]
        "target_index": used_index,
        "layer": used_layer,
        "task": task
    }

def save_cam_arrays(
    cam: np.ndarray,                   # (H, W) float32 [0,1]
    rgb: Optional[np.ndarray] = None,  # (H, W, 3) uint8, RGB
    overlay: Optional[np.ndarray] = None, # (H, W, 3) uint8, RGB
    *,
    save_dir: str = "xai_outputs",
    basename: str = "gradcam",
    save_heatmap: bool = True,
    save_rgb: bool = False, # 원본 저장
    save_overlay: bool = False, # overlay 저장 
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
        self.attns: List[torch.Tensor] = [] # (B, H, N, N), softmax된 확률
        self.grad_attns: List[Optional[torch.Tensor]] = [] # backward 훅에서 받은 grad

    def fwd(self, module, inp, out):
        # block.attn.forward에서 softmax 후 확률을 module.attn에 저장했다 가정
        attn = getattr(module, "attn", None)
        if attn is None:
            # out이 (x, attn) 튜플이면 두번째 쓰도록
            if isinstance(out, (tuple, list)) and len(out) >= 2 and out[-1] is not None:
                attn = out[-1]
            elif isinstance(out, dict) and "attn" in out:
                attn = out["attn"]
        if attn is None:
            # 모듈 내부에 softmax 전/후 중간 텐서가 없으면 포기
            raise RuntimeError(f"Cannot find attention probs in module: {module.__class__.__name__}")
        self.attns.append(attn)
    
    def bwd(self, module, grad_input, grad_output):
        g = None
        if len(grad_output) >= 2 and grad_output[-1] is not None:
            g = grad_output[-1]
        elif len(grad_output) >= 1:
            g = grad_output[0]
        self.grad_attns.append(g)    
    
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
    mats = []
    for A, G in zip(attns, grads):
        # A: (B, H, N, N) 이여야 함
        if G is None:
            # grad가 없으면 해당 레이어는 순수 A로 사용
            GwA = F.relu(A)
        else:
            # 브로드캐스트 맞는지 확인
            if G.shape != A.shape:
                # 일부 구현에서 grad_output shape가 다를 수 있음 → 헤드 평균 후 브로드캐스트 등 보정
                Gm = G
                if Gm.dim() == 3:  # (B, N, N)
                    Gm = Gm.unsqueeze(1).expand_as(A)
                GwA = F.relu(A * F.relu(Gm))
            else:
                GwA = F.relu(A * F.relu(G))
        M = GwA.mean(dim=1)  # (B, N, N)
        M = M / (M.sum(dim=-1, keepdim=True) + eps)
        if add_residual:
            I = torch.eye(M.size(-1), device=M.device).unsqueeze(0)
            M = M + I
            M = M / (M.sum(dim=-1, keepdim=True) + eps)
        mats.append(M)

    R = mats[0]
    for L in mats[1:]:
        R = torch.bmm(R, L)
    return R[:, 0]  # (B, N)

@torch.enable_grad()
def generate_attention_arrays_from_lastyear(
    model: nn.Module,
    image_tensor_bchw: torch.Tensor,   # (1,C,H,W)
    outputs,                           # fresh forward 할 것이므로 형식 무관
    *,
    task: str,                         # 'classification' | 'regression'
    target_index: Optional[int],
    assume_cls_token: bool = True,
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
        side = int(round(np.sqrt(float(N_img))))
        Hp, Wp = side, int(np.ceil(N_img / max(side, 1)))
        img_tokens = img_tokens[:Hp*Wp]

        grid = img_tokens.reshape(Hp, Wp)
        grid = grid - grid.min()
        if grid.max().item() > 0:
            grid = grid / grid.max()
        cam = F.interpolate(grid.unsqueeze(0).unsqueeze(0), size=(H, W),
                            mode="bilinear", align_corners=False)[0, 0]
        cam = cam.detach().cpu().numpy().astype(np.float32)

        return {"cam": cam, "target_index": int(target_index),
                "layer": "attn-rollout(lastyear)", "task": task}
    finally:
        for h in hooks:
            h.remove()