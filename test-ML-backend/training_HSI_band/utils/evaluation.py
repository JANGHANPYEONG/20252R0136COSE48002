import numpy as np
import time
from typing import Dict, List, Tuple, Optional
import pandas as pd

class BandSelectionEvaluator:
    """Band Selection 결과를 평가하는 클래스"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
    
    def start_timer(self):
        """타이머를 시작합니다."""
        self.start_time = time.time()
    
    def end_timer(self) -> float:
        """타이머를 종료하고 경과 시간을 반환합니다."""
        if self.start_time is None:
            return 0.0
        elapsed_time = time.time() - self.start_time
        self.start_time = None
        return elapsed_time
    
    def evaluate_preprocessing(self, 
                             original_bands: int,
                             selected_bands: List[int],
                             target_bands: int,
                             method_name: str) -> Dict:
        """전처리 결과를 평가합니다."""
        metrics = {}
        
        # 선택된 밴드 수
        metrics['selected_count'] = len(selected_bands)
        
        # 목표 밴드 수와의 차이
        metrics['target_diff'] = abs(len(selected_bands) - target_bands)
        
        # 중복 제거율
        metrics['reduction_ratio'] = 1 - (len(selected_bands) / original_bands)
        
        # 밴드 범위
        if selected_bands:
            metrics['band_range'] = f"{min(selected_bands)}-{max(selected_bands)}"
        else:
            metrics['band_range'] = "None"
        
        # 처리 시간 (타이머가 시작된 경우)
        if self.start_time is not None:
            metrics['processing_time'] = self.end_timer()
        
        self.metrics[f'preprocessing_{method_name}'] = metrics
        return metrics
    
    def evaluate_training(self,
                         selected_bands: List[int],
                         band_scores: List[float],
                         target_bands: int,
                         method_name: str) -> Dict:
        """본처리 결과를 평가합니다."""
        metrics = {}
        
        # 선택된 밴드 수
        metrics['selected_count'] = len(selected_bands)
        
        # 목표 밴드 수와의 차이
        metrics['target_diff'] = abs(len(selected_bands) - target_bands)
        
        # 스코어 통계
        if band_scores:
            metrics['score_mean'] = np.mean(band_scores)
            metrics['score_std'] = np.std(band_scores)
            metrics['score_min'] = np.min(band_scores)
            metrics['score_max'] = np.max(band_scores)
        else:
            metrics['score_mean'] = 0.0
            metrics['score_std'] = 0.0
            metrics['score_min'] = 0.0
            metrics['score_max'] = 0.0
        
        # 밴드 범위
        if selected_bands:
            metrics['band_range'] = f"{min(selected_bands)}-{max(selected_bands)}"
        else:
            metrics['band_range'] = "None"
        
        # 처리 시간
        if self.start_time is not None:
            metrics['processing_time'] = self.end_timer()
        
        self.metrics[f'training_{method_name}'] = metrics
        return metrics
    
    def evaluate_pipeline(self,
                         original_bands: int,
                         pre_selected_bands: List[int],
                         final_selected_bands: List[int],
                         final_scores: List[float],
                         target_bands: int,
                         pre_method: str,
                         train_method: str) -> Dict:
        """전체 파이프라인 결과를 평가합니다."""
        metrics = {}
        
        # 전처리 결과
        pre_metrics = self.evaluate_preprocessing(
            original_bands, pre_selected_bands, target_bands, pre_method
        )
        
        # 본처리 결과
        train_metrics = self.evaluate_training(
            final_selected_bands, final_scores, target_bands, train_method
        )
        
        # 전체 파이프라인 메트릭
        metrics['total_reduction_ratio'] = 1 - (len(final_selected_bands) / original_bands)
        metrics['pre_to_final_ratio'] = len(final_selected_bands) / len(pre_selected_bands) if pre_selected_bands else 0
        
        # 전처리와 본처리 결과 통합
        metrics.update({f'pre_{k}': v for k, v in pre_metrics.items()})
        metrics.update({f'train_{k}': v for k, v in train_metrics.items()})
        
        self.metrics['pipeline'] = metrics
        return metrics
    
    def get_summary(self) -> Dict:
        """모든 메트릭의 요약을 반환합니다."""
        return self.metrics
    
    def save_metrics(self, filepath: str):
        """메트릭을 CSV 파일로 저장합니다."""
        # 메트릭을 플랫하게 변환
        flat_metrics = {}
        for category, metrics in self.metrics.items():
            for key, value in metrics.items():
                flat_metrics[f"{category}_{key}"] = value
        
        # DataFrame으로 변환하여 저장
        df = pd.DataFrame([flat_metrics])
        df.to_csv(filepath, index=False)
        print(f"Metrics saved to {filepath}")

def calculate_band_overlap(bands1: List[int], bands2: List[int]) -> float:
    """두 밴드 선택 결과 간의 겹침 비율을 계산합니다."""
    if not bands1 or not bands2:
        return 0.0
    
    overlap = len(set(bands1) & set(bands2))
    union = len(set(bands1) | set(bands2))
    
    return overlap / union if union > 0 else 0.0

def calculate_band_distribution(selected_bands: List[int], 
                              total_bands: int) -> Dict:
    """선택된 밴드의 분포를 분석합니다."""
    if not selected_bands:
        return {"distribution": "No bands selected"}
    
    # 밴드 간격 분석
    sorted_bands = sorted(selected_bands)
    intervals = [sorted_bands[i+1] - sorted_bands[i] for i in range(len(sorted_bands)-1)]
    
    return {
        "min_interval": min(intervals) if intervals else 0,
        "max_interval": max(intervals) if intervals else 0,
        "mean_interval": np.mean(intervals) if intervals else 0,
        "std_interval": np.std(intervals) if intervals else 0,
        "coverage_ratio": len(selected_bands) / total_bands
    } 