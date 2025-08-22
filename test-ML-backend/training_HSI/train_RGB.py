#!/usr/bin/env python3
"""
RGB 이미지 분류/회귀 학습 파이프라인

이 스크립트는 RGB 이미지를 사용하여 분류 및 회귀 작업을 동시에 수행하는 모델을 훈련합니다.
세그멘테이션 마스크를 선택적으로 적용할 수 있으며, HSI 파이프라인과 호환됩니다.

사용법:
    python3 train_RGB.py --config configs/RGB_image/rgb_resnet.json

"""

import os
import sys
import json
import argparse
import torch
import numpy as np
import random
import torch.backends.cudnn as cudnn
from torch.utils.data import DataLoader
import warnings
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.dataset_rgb import create_rgb_data_loaders
from utils.logger import create_logger, log_training_summary
from utils.trainer import HSITrainer
from utils.transforms_rgb import get_train_transforms, get_val_transforms, get_test_transforms
from utils.model_loader import load_model, validate_model_config, get_model_info as get_model_info_from_config


def load_config(config_path: str) -> dict:
    """설정 파일을 로드합니다."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    return config


def setup_device() -> torch.device:
    """CUDA 전용 디바이스 설정(필수)."""
    assert torch.cuda.is_available(), "CUDA가 필요합니다. GPU 환경을 확인하세요."
    device = torch.device('cuda')
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    # 성능 최적화
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
    return device


def setup_seed(seed: int):
    """랜덤 시드를 설정합니다."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    # 재현성보다 성능 우선(GPU-only): benchmark=True 권장
    cudnn.deterministic = False
    cudnn.benchmark = True
    print(f"Random seed set to: {seed}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='RGB Image Training')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to configuration file')
    parser.add_argument('--no-mlflow', action='store_true',
                       help='Disable MLflow logging')
    parser.add_argument('--save-interval', type=int,
                       help='Epoch interval for model checkpointing')
    args = parser.parse_args()
    
    run_id = None
    
    # 설정 로드
    print("Loading configuration...")
    config = load_config(args.config)
    
    # CLI 파라미터로 save_interval 덮어쓰기
    if args.save_interval is not None:
        config['train']['save_interval'] = args.save_interval
    
    # 시드 설정
    seed = config.get('seed', 42)
    setup_seed(seed)
    
    # 디바이스 설정
    device = setup_device()
    
    # 모델 설정 검증
    print("Validating model configuration...")
    if not validate_model_config(config):
        raise ValueError("Invalid model configuration")
    
    # 모델 정보 출력
    model_info = get_model_info_from_config(config)
    print(f"Model: {model_info['model_file']}")
    print(f"Number of classes: {model_info['num_classes']}")
    print(f"Parameters: {model_info['parameters']}")
    
    # 데이터 설정
    data_config = config['data']
    image_size = tuple(data_config['image_size'])
    batch_size = data_config['batch_size']
    num_workers = data_config['num_workers']
    val_split = data_config['val_split']
    test_split = data_config['test_split']
    aug = data_config['aug']
    
    # 세그멘테이션 설정
    seg_config = config.get('seg', {})
    seg_enabled = seg_config.get('enabled', False)
    seg_mode = seg_config.get('mode', 'precomputed')
    seg_apply = seg_config.get('apply', 'mul')
    
    print(f"Segmentation: {'Enabled' if seg_enabled else 'Disabled'}")
    if seg_enabled:
        print(f"  - Mode: {seg_mode}")
        print(f"  - Apply: {seg_apply}")
    
    # MLflow 로거 설정 (data_config/seg_config 파싱 이후)
    logger = None
    if not args.no_mlflow:
        try:
            logger = create_logger(config)
            logger.start_run(run_name="rgb_training")
            logger.log_params({
                'model_namespace': config['model'].get('namespace', 'RGB_image'),
                'model_file': config['model']['file'],
                'num_classes': config['model']['num_classes'],
                'batch_size': batch_size,
                'epochs': config['train']['epochs'],
                'optimizer': config['train']['optimizer'],
                'lr': config['train']['lr'],
                'scheduler': config['train'].get('scheduler', 'ReduceLROnPlateau'),
                'save_interval': config['train'].get('save_interval', 5),
                'seg_enabled': seg_enabled,
                'seg_mode': seg_mode,
                'seg_apply': seg_apply,
                'seed': seed
            })
        except Exception as e:
            print(f"Warning: MLflow logging failed: {e}")
            logger = None
    
    # 변환 설정
    print("Setting up transforms...")
    train_transform = get_train_transforms(image_size, aug=aug)
    val_transform = get_val_transforms(image_size)
    test_transform = get_test_transforms(image_size)
    
    transform_config = {
        'train': train_transform,
        'val': val_transform,
        'test': test_transform
    }
    
    # 데이터 로더 생성
    print("Creating data loaders...")
    train_loader, val_loader, test_loader, pos_weight_info = create_rgb_data_loaders(
        csv_path=data_config['csv'],
        column_config_path=data_config['column_config'],
        seg_config=seg_config,
        transform_config=transform_config,
        batch_size=batch_size,
        num_workers=num_workers,
        val_split=val_split,
        test_split=test_split,
        seed=seed
    )
    
    # 모델 생성
    print("Creating model...")
    model = load_model(config)
    model = model.to(device)
    
    # 트레이너 생성
    print("Creating trainer...")
    trainer = HSITrainer(model, device, config, pos_weight_info=pos_weight_info)

    # 학습
    training_results = trainer.train(train_loader, val_loader, config['train']['epochs'], logger=logger)

    # 평가
    test_metrics = trainer.evaluate(test_loader)

    # 로그/요약
    if logger:
        try:
            logger.log_training_curve(
                training_results['train_losses'],
                training_results['val_losses'],
                training_results['train_metrics'],
                training_results['val_metrics'],
                plot_keys=config.get('plot_keys', ["cls_f1_score","reg_r2","combined_score"])
            )
            final_metrics = {
                **test_metrics,
                'best_val_loss': trainer.best_val_loss,
                'best_val_combined_score': training_results['best_val_metrics'].get('combined_score', 0),
                'training_time_minutes': training_results['training_time'] / 60.0
            }
            
            # NaN 가드 추가
            import math
            final_metrics = {k: (0.0 if (isinstance(v, float) and math.isnan(v)) else v)
                             for k, v in final_metrics.items()}
            
            logger.log_metrics(final_metrics)
            logger.log_config(config, config_name="rgb_config.json")
        except Exception as e:
            print(f"Warning: MLflow logging failed: {e}")
        finally:
            logger.end_run()


if __name__ == '__main__':
    main()