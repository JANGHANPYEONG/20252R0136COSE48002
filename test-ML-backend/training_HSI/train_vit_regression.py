#!/usr/bin/env python3
"""
ViT Regression 모델을 사용한 HSI 회귀 학습 파이프라인
C:/sanhak/manage-dataset/result 데이터셋 사용 (회귀 전용)

이 스크립트는 Vision Transformer를 사용하여 5개 회귀 출력을 예측합니다:
- Total, Marbling, Meat Color, Texture, Surface Moisture

사용법:
    python train_vit_regression.py --config configs/HSI_image/hsi_vit_regression.json
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

from utils.dataset_vit_regression import create_vit_regression_data_loaders
from utils.logger_vit_regression import create_logger, log_training_summary
from utils.trainer_vit_regression import HSITrainer
from utils.transforms_hsi import get_train_transforms, get_val_transforms, get_test_transforms
from utils.model_loader import load_model, validate_model_config, get_model_info as get_model_info_from_config


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
    parser = argparse.ArgumentParser(description='ViT Regression HSI Training')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to configuration file')
    parser.add_argument('--no-mlflow', action='store_true',
                       help='Disable MLflow logging')
    parser.add_argument('--save-interval', type=int,
                       help='Epoch interval for model checkpointing')
    args = parser.parse_args()

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

    # MLflow 로거 설정
    logger = None
    if not args.no_mlflow:
        try:
            logger = create_logger(config)
            logger.start_run()

            # 하이퍼파라미터 로깅
            params_to_log = {
                'model_file': config['model']['file'],
                'num_classes': config['model']['num_classes'],
                'batch_size': config['data']['batch_size'],
                'epochs': config['train']['epochs'],
                'optimizer': config['train']['optimizer'],
                'lr': float(config['train']['lr']),  # 명시적 float 변환
                'weight_decay': float(config['train'].get('weight_decay', 0)),
                'scheduler': config['train']['scheduler'],
                'save_interval': config['train'].get('save_interval', 5),
                'dropout': config['model'].get('dropout', 0.1),
                'patch_size': config['model'].get('patch_size', 16),
                'emb_dim': config['model'].get('emb_dim', 96),
                'depth': config['model'].get('depth', 4),
                'seed': seed,
                'dataset': 'vit-regression'
            }
            logger.log_params(params_to_log)
        except Exception as e:
            print(f"MLflow connection failed: {e}")
            print("Continuing without MLflow logging...")
            logger = None

    try:
        # Transform 설정
        print("Setting up transforms...")
        train_transform = get_train_transforms(
            crop_size=tuple(config.get('data', {}).get('target_size', [224, 224])),
            use_flip=config.get('data', {}).get('use_flip', True),
            use_rotation=config.get('data', {}).get('use_rotation', True),
            use_noise=config.get('data', {}).get('use_noise', True),
            use_brightness_contrast=config.get('data', {}).get('use_brightness_contrast', True),
            use_advanced_aug=config.get('data', {}).get('use_advanced_aug', True)
        )
        image_size = tuple(config.get('data', {}).get('target_size', [224, 224]))
        val_transform = get_val_transforms(image_size=image_size)
        test_transform = get_test_transforms(image_size=image_size)

        # 데이터 로더 생성
        print("Creating data loaders...")
        scaler_mode = config["data"].get("scaler_mode", "normalized")
        train_loader, val_loader, test_loader, scaler, pos_weight_info = create_vit_regression_data_loaders(
            root_dir=config['data']['root_dir'],
            batch_size=config['data']['batch_size'],
            num_workers=config['data']['num_workers'],
            val_split=config['data']['val_split'],
            test_split=config['data']['test_split'],
            train_transform=train_transform,
            val_transform=val_transform,
            test_transform=test_transform,
            scaler_mode=scaler_mode,
            wavelengths=config['data'].get('wavelengths', None),  # None for auto-detection
            wavelength_strategy=config['data'].get('wavelength_strategy', 'auto'),
            use_rgb=config['data'].get('use_rgb', True),
            target_size=tuple(config['data'].get('target_size', [224, 224])),
            missing_wavelength_strategy=config['data'].get('missing_wavelength_strategy', 'interpolate'),
            random_state=seed
        )

        # 라벨 정보 출력
        print(f"Dataset info:")
        print(f"  Total samples: {pos_weight_info['total_samples']}")
        print(f"  Class distribution: {pos_weight_info['class_counts']}")

        # pos_weight 정보 출력
        if pos_weight_info['cls_indices']:
            print(f"  Classification indices: {pos_weight_info['cls_indices']}")
            print(f"  Regression indices: {pos_weight_info['reg_indices']}")

        # 모델 설정 검증
        print("Validating model configuration...")
        if not validate_model_config(config):
            raise ValueError("Invalid model configuration")

        # 모델 생성
        print("Creating model...")
        model = load_model(config)
        model = model.to(device)

        # 모델 정보 출력
        model_info = get_model_info_from_config(config)
        print(f"Model config info: {model_info}")

        # 모델 파라미터 정보 출력
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"Model parameters: {total_params:,} total, {trainable_params:,} trainable")

        # 훈련기 생성 (pos_weight_info 전달)
        print("Creating trainer...")
        trainer = HSITrainer(model, device, config, pos_weight_info=pos_weight_info)

        # 플롯 키 설정 (회귀 전용)
        plot_keys = config.get('plot_keys', ["r2", "mse", "combined_score"])

        # 훈련 수행
        print("Starting training...")
        import time
        start_time = time.time()
        training_results = trainer.train(
            train_loader=train_loader,
            val_loader=val_loader,
            num_epochs=config['train']['epochs'],
            logger=logger
        )
        end_time = time.time()
        training_time = end_time - start_time

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

            # 회귀 메트릭 추가
            final_metrics.update({
                'best_val_r2': training_results['best_val_metrics'].get('r2', 0),
                'best_val_mse': training_results['best_val_metrics'].get('mse', 0),
                'best_val_mae': training_results['best_val_metrics'].get('mae', 0)
            })

            logger.log_metrics(final_metrics)
            log_training_summary(logger, config, final_metrics, training_time)

        # 최종 결과 출력
        print("\n" + "="*50)
        print("Training completed!")
        print("="*50)

        print(f"\nTest Results:")
        for key, value in test_metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")

        print(f"\nBest Validation Results:")
        if training_results.get('best_val_metrics'):
            for key, value in training_results['best_val_metrics'].items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")

        # 모델 저장
        save_dir = os.path.join('checkpoints', config.get('experiment', 'default'))
        os.makedirs(save_dir, exist_ok=True)
        final_model_path = os.path.join(save_dir, 'final_model.pth')
        torch.save({
            'model_state_dict': model.state_dict(),
            'config': config,
            'test_metrics': test_metrics,
            'best_val_metrics': training_results.get('best_val_metrics', {})
        }, final_model_path)

        if logger:
            logger.log_artifact(final_model_path)

        print(f"\nFinal model saved to: {final_model_path}")

    except KeyboardInterrupt:
        print("\n" + "="*50)
        print("Training interrupted by user")
        print("="*50)
    except Exception as e:
        print(f"\n" + "="*50)
        print(f"Training failed with error: {e}")
        print("="*50)
        import traceback
        traceback.print_exc()
    finally:
        if logger:
            logger.end_run()
            print("MLflow run ended")


if __name__ == '__main__':
    main()