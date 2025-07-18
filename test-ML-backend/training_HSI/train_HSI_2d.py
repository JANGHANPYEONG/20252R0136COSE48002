#!/usr/bin/env python3
"""
HSI 2D CNN 학습 파이프라인

이 스크립트는 HSI(Hyperspectral Imaging) 데이터를 사용하여 2D CNN 모델을 훈련합니다.
멀티태스크 학습을 지원하며, 분류 및 회귀 작업을 동시에 수행할 수 있습니다.

사용법:
    python train_HSI_2d.py --config configs/HSI_image/hsi_resnet.json
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

from utils.dataset_hsi import create_hsi_data_loaders, get_label_info
from utils.logger import create_logger, log_training_summary
from utils.trainer import HSITrainer
from utils.transforms_hsi import get_train_transforms, get_val_transforms, get_test_transforms
from models.HSI_image.hsi_resnet import create_hsi_resnet_model, get_model_info


def load_config(config_path: str) -> dict:
    """설정 파일을 로드합니다."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    return config


def setup_device() -> torch.device:
    """디바이스를 설정합니다."""
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        device = torch.device('cpu')
        print("Using CPU")
    
    return device


def setup_seed(seed: int):
    """랜덤 시드를 설정합니다."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    cudnn.deterministic = True
    cudnn.benchmark = False
    print(f"Random seed set to: {seed}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='HSI 2D CNN Training')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to configuration file')
    parser.add_argument('--no-mlflow', action='store_true',
                       help='Disable MLflow logging')
    args = parser.parse_args()
    
    # 설정 로드
    print("Loading configuration...")
    config = load_config(args.config)
    
    # 시드 설정
    seed = config.get('seed', 42)
    setup_seed(seed)
    
    # 디바이스 설정
    device = setup_device()
    
    # MLflow 로거 설정
    logger = None
    if not args.no_mlflow:
        logger = create_logger(config)
        logger.start_run()
        
        # 하이퍼파라미터 로깅
        params_to_log = {
            'model_file': config['model']['file'],
            'num_classes': config['model']['num_classes'],
            'batch_size': config['data']['batch_size'],
            'epochs': config['train']['epochs'],
            'optimizer': config['train']['optimizer'],
            'lr': config['train']['lr'],
            'scheduler': config['train']['scheduler'],
            'seed': seed
        }
        logger.log_params(params_to_log)
    
    try:
        # Transform 설정
        print("Setting up transforms...")
        train_transform = get_train_transforms(
            crop_size=tuple(config.get('data', {}).get('crop_size', [224, 224])),
            use_flip=config.get('data', {}).get('use_flip', True),
            use_rotation=config.get('data', {}).get('use_rotation', True),
            use_noise=config.get('data', {}).get('use_noise', True),
            use_brightness_contrast=config.get('data', {}).get('use_brightness_contrast', True)
        )
        image_size = tuple(config.get('data', {}).get('crop_size', [224, 224]))
        val_transform = get_val_transforms(image_size=image_size)
        test_transform = get_test_transforms(image_size=image_size)
        
        # 데이터 로더 생성
        print("Creating data loaders...")
        train_loader, val_loader, test_loader, scaler = create_hsi_data_loaders(
            csv_path=config['data']['csv'],
            column_config_path=config['data']['column_config'],
            batch_size=config['data']['batch_size'],
            num_workers=config['data']['num_workers'],
            val_split=config['data']['val_split'],
            test_split=config['data']['test_split'],
            random_state=seed,
            train_transform=train_transform,
            val_transform=val_transform,
            test_transform=test_transform
        )
        
        # 라벨 정보 가져오기
        label_info = get_label_info(config['data']['column_config'])
        print(f"Label info: {label_info}")
        
        # 모델 생성
        print("Creating model...")
        model = create_hsi_resnet_model(config)
        model = model.to(device)
        
        # 모델 정보 출력
        model_info = get_model_info(model)
        print(f"Model info: {model_info}")
        
        # 훈련기 생성
        trainer = HSITrainer(model, device, config)
        
        # 플롯 키 설정
        plot_keys = config.get('plot_keys', ["cls_f1_score", "reg_r2", "combined_score"])
        
        # 훈련 수행
        print("Starting training...")
        training_results = trainer.train(
            train_loader=train_loader,
            val_loader=val_loader,
            num_epochs=config['train']['epochs'],
            logger=logger
        )
        
        # 테스트 평가
        print("Evaluating on test set...")
        test_metrics = trainer.evaluate(test_loader)
        
        # 최종 결과 로깅
        if logger is not None:
            # 스케일러 로깅
            logger.log_scaler(scaler)
            
            # 훈련 곡선 로깅 (plot_keys 전달)
            logger.log_training_curve(
                training_results['train_losses'], 
                training_results['val_losses'], 
                training_results['train_metrics'], 
                training_results['val_metrics'],
                plot_keys=plot_keys
            )
            
            # 최종 메트릭 로깅
            final_metrics = {
                **test_metrics,
                'best_val_loss': trainer.best_val_loss,
                'best_val_combined_score': training_results['best_val_metrics'].get('combined_score', 0)
            }
            
            # 분류 메트릭 추가
            if 'cls_f1_score' in test_metrics:
                final_metrics.update({
                    'best_val_cls_f1': training_results['best_val_metrics'].get('cls_f1_score', 0),
                    'best_val_cls_auc': training_results['best_val_metrics'].get('cls_auc', 0)
                })
            
            # 회귀 메트릭 추가
            if 'reg_r2' in test_metrics:
                final_metrics.update({
                    'best_val_reg_r2': training_results['best_val_metrics'].get('reg_r2', 0),
                    'best_val_reg_mse': training_results['best_val_metrics'].get('reg_mse', 0)
                })
            
            log_training_summary(
                logger=logger,
                config=config,
                final_metrics=final_metrics,
                training_time=training_results['training_time']
            )
        
        print("Training completed successfully!")
        
        if 'cls_f1_score' in test_metrics:
            print(f"Test F1 Score: {test_metrics['cls_f1_score']:.4f}")
            print(f"Test AUC: {test_metrics['cls_auc']:.4f}")
        
        if 'reg_r2' in test_metrics:
            print(f"Test R2 Score: {test_metrics['reg_r2']:.4f}")
            print(f"Test MSE: {test_metrics['reg_mse']:.4f}")
        
        print(f"Test Combined Score: {test_metrics.get('combined_score', 0):.4f}")
        
    except Exception as e:
        print(f"Error during training: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        # MLflow run 종료
        if logger is not None:
            logger.end_run()


if __name__ == "__main__":
    main()
