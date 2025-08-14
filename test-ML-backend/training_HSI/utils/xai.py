from typing import Optional, Tuple, List, Dict
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
                score = torch.sigmoid(logits)[0, index]
            else: # 회귀 task
                y = outputs.get("regression", None)
                if y is None:
                    raise RuntimeError("회귀 task인데 outputs에서 인덱싱 불가")
                score = y[0, index]
        else: # 단일 출력 텐서
            if is_cls:
                score = torch.sigmoid(outputs)[0, index]
            else:
                scrore = outputs[0, index]

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
            if m.kernel_size != (1, 1):
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
) -> Dict[str, Optional[str]]:
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
