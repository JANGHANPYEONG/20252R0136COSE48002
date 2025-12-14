#!/usr/bin/env python3
"""
Transfer Learning ViT + K-Fold Cross Validation
작은 데이터셋(159개)을 위한 최적화된 학습 파이프라인

특징:
- ImageNet Pretrained ViT 사용
- 5-Fold Cross Validation
- RGB와 파장 분리 정규화

사용법:
    python train_vit_transfer_kfold.py --config configs/HSI_image/hsi_vit_transfer_kfold.json
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

from utils.dataset_vit_regression import ViTRegressionDataset
from utils.logger_vit_regression import create_logger, log_training_summary
from utils.trainer_kfold import KFoldTrainer
from utils.transforms_hsi import get_train_transforms, get_val_transforms
from utils.model_loader import validate_model_config


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


def create_model_fn(config: dict):
    """모델 생성 함수를 반환합니다."""
    def _create_model():
        from models.HSI_image.hsi_vit_transfer import create_model
        return create_model(config)
    return _create_model


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Transfer Learning ViT + K-Fold Cross Validation')
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
        try:
            logger = create_logger(config)
            logger.start_run()

            # 하이퍼파라미터 로깅
            params_to_log = {
                'model_file': config['model']['file'],
                'timm_model': config['model']['timm_model_name'],
                'pretrained': config['model']['pretrained'],
                'freeze_backbone': config['model']['freeze_backbone'],
                'num_classes': config['model']['num_classes'],
                'kfold_splits': config['kfold']['n_splits'],
                'batch_size': config['data']['batch_size'],
                'epochs': config['train']['epochs'],
                'optimizer': config['train']['optimizer'],
                'lr': config['train']['lr'],
                'weight_decay': config['train']['weight_decay'],
                'scheduler': config['train']['scheduler'],
                'seed': seed,
                'dataset': 'vit-transfer-kfold'
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

        # 전체 데이터셋 생성 (K-Fold용)
        print("Creating full dataset...")
        scaler_mode = config["data"].get("scaler_mode", "normalized")
        full_dataset = ViTRegressionDataset(
            root_dir=config['data']['root_dir'],
            transform=train_transform,  # Train transform 사용
            scaler=None,
            fit_scaler=True,
            scaler_mode=scaler_mode,
            wavelengths=config['data'].get('wavelengths', None),
            wavelength_strategy=config['data'].get('wavelength_strategy', 'auto'),
            use_rgb=config['data'].get('use_rgb', True),
            target_size=tuple(config['data'].get('target_size', [224, 224])),
            missing_wavelength_strategy=config['data'].get('missing_wavelength_strategy', 'use_available')
        )

        print(f"Total samples: {len(full_dataset)}")

        # pos_weight 정보 생성 (전체 데이터셋 기준)
        from utils.dataset_vit_regression import _calculate_pos_weight_info
        pos_weight_info = _calculate_pos_weight_info(full_dataset, list(range(len(full_dataset))))

        # 모델 생성 함수
        model_fn = create_model_fn(config)

        # 모델 정보 출력 (샘플)
        print("Creating sample model for inspection...")
        sample_model = model_fn()
        total_params = sum(p.numel() for p in sample_model.parameters())
        trainable_params = sum(p.numel() for p in sample_model.parameters() if p.requires_grad)
        print(f"Model parameters: {total_params:,} total, {trainable_params:,} trainable")
        del sample_model  # 메모리 해제

        # K-Fold Trainer 생성
        print("\nCreating K-Fold Trainer...")
        kfold_trainer = KFoldTrainer(
            config=config,
            device=device,
            create_model_fn=model_fn,
            dataset=full_dataset,
            pos_weight_info=pos_weight_info
        )

        # K-Fold 훈련 수행
        print("\nStarting K-Fold Cross Validation...")
        import time
        start_time = time.time()
        kfold_results = kfold_trainer.train(logger=logger)
        total_time = time.time() - start_time

        # 최종 결과 로깅
        if logger is not None:
            # 스케일러 로깅
            logger.log_scaler(full_dataset.scaler)

            # 최종 메트릭
            final_metrics = kfold_results['aggregated_results']
            logger.log_metrics(final_metrics)

            # 훈련 요약
            log_training_summary(logger, config, final_metrics, total_time)

        # 결과 저장
        save_dir = os.path.join('checkpoints', config.get('experiment', 'default'))
        os.makedirs(save_dir, exist_ok=True)

        results_path = os.path.join(save_dir, 'kfold_results.json')
        with open(results_path, 'w') as f:
            # numpy 타입을 python 타입으로 변환
            def convert_to_serializable(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_to_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_serializable(item) for item in obj]
                else:
                    return obj

            serializable_results = convert_to_serializable(kfold_results)
            json.dump(serializable_results, f, indent=2)

        print(f"\nK-Fold results saved to: {results_path}")

        if logger:
            logger.log_artifact(results_path)

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
