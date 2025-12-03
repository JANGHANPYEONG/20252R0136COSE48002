"""
세그멘테이션 엔진 모듈

이 모듈은 세그멘테이션 마스크 생성을 위한 인터페이스를 제공합니다.
"""

import numpy as np
from PIL import Image
from typing import Optional, Dict, Any
import warnings


class SegmentationEngine:
    """
    세그멘테이션 마스크 생성을 위한 엔진 클래스
    
    현재는 인터페이스만 제공하며, 실제 구현은 후속 개선에서 진행됩니다.
    """
    
    def __init__(self, seg_cfg: Dict[str, Any], device: str = "cpu"):
        """
        세그멘테이션 엔진을 초기화합니다.
        
        Args:
            seg_cfg: 세그멘테이션 설정 딕셔너리
            device: 사용할 디바이스 ("cpu" 또는 "cuda")
        """
        self.seg_cfg = seg_cfg
        self.device = device
        self.mode = seg_cfg.get('mode', 'precomputed')
        
        if self.mode != 'precomputed':
            warnings.warn(
                f"Segmentation mode '{self.mode}' is not yet implemented. "
                "Falling back to precomputed mode."
            )
            self.mode = 'precomputed'
    
    def predict_mask(self, img: Image.Image) -> np.ndarray:
        """
        이미지에서 세그멘테이션 마스크를 예측합니다.
        
        Args:
            img: PIL Image 객체
            
        Returns:
            np.ndarray: 마스크 배열 (H, W, [0,1])
        """
        if self.mode == 'precomputed':
            # precomputed 모드에서는 이 함수가 호출되지 않아야 함
            raise RuntimeError(
                "predict_mask should not be called in precomputed mode. "
                "Masks should be loaded from files instead."
            )
        
        width, height = img.size
        mask = np.ones((height, width), dtype=np.float32)
        
        warnings.warn(
            "Segmentation model not implemented yet. "
            "Returning dummy mask (all ones)."
        )
        
        return mask
    
    def predict_batch_masks(self, imgs: list) -> list:
        """
        배치 이미지에서 세그멘테이션 마스크를 예측합니다.
        
        Args:
            imgs: PIL Image 객체들의 리스트
            
        Returns:
            list: 마스크 배열들의 리스트
        """
        if self.mode == 'precomputed':
            raise RuntimeError(
                "predict_batch_masks should not be called in precomputed mode."
            )
        
        masks = []
        for img in imgs:
            mask = self.predict_mask(img)
            masks.append(mask)
        
        return masks
    
    def get_supported_modes(self) -> list:
        """
        지원되는 세그멘테이션 모드를 반환합니다.
        
        Returns:
            list: 지원되는 모드 리스트
        """
        return ['precomputed']  # 현재는 precomputed만 지원
    
    def is_mode_supported(self, mode: str) -> bool:
        """
        특정 모드가 지원되는지 확인합니다.
        
        Args:
            mode: 확인할 모드명
            
        Returns:
            bool: 지원 여부
        """
        return mode in self.get_supported_modes()


def create_segmentation_engine(seg_cfg: Dict[str, Any], device: str = "cpu") -> SegmentationEngine:
    """
    세그멘테이션 엔진을 생성합니다.
    
    Args:
        seg_cfg: 세그멘테이션 설정 딕셔너리
        device: 사용할 디바이스
        
    Returns:
        SegmentationEngine: 생성된 세그멘테이션 엔진
    """
    return SegmentationEngine(seg_cfg, device)