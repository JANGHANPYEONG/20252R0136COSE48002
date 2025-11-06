#!/usr/bin/env python3
"""
Meat Freshness 분류 학습 파이프라인

Kaggle Meat Freshness 데이터셋을 사용한 3-class 분류 학습
기존 HSI 파이프라인(train_HSI_2d.py)을 재활용하여 일관된 학습 환경 제공

사용법:
    python3 train_meat_freshness.py --config configs/RGB_image/meat_freshness.json
    python3 train_meat_freshness.py --config configs/RGB_image/meat_freshness.json --no-mlflow
"""

import os
import sys
import json
import argparse
import torch
import numpy as np
import random
import torch.backends.cudnn as cudnn
import warnings
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.dataset_meat_freshness import create_meat_freshness_data_loaders
from utils.logger import create_logger, log_training_summary
from utils.trainer import HSITrainer
from utils.model_loader import load_model, validate_model_config, get_model_info as get_model_info_from_config
import importlib
import tempfile


def create_meat_freshness_column_config(config):
    """Meat Freshness 데이터셋용 column_config 생성"""
    model_config = config['model']
    num_classes = model_config['num_classes']
    class_names = config['data']['class_names']
    
    # 3-class multi-label 형식으로 변환 (one-hot encoding)
    column_config = {
        "column_order": {
            "id_column_index": 0,
            "label_start_index": 1,
            "image_path_start_index": None,
            "rgb_image_path_start_index": None
        },
        "label_columns": class_names,  # ["FRESH", "HALF-FRESH", "SPOILED"]
        "label_types": {
            "classification": class_names,  # 모두 분류 라벨
            "regression": []
        },
        "in_channels": model_config['in_channels'],
        "image_size": config['data']['image_size'],
        "base_dirs": {
            "hsi_image_dir": "",
            "rgb_image_dir": ""
        }
    }
    
    # configs 디렉토리에 저장
    config_dir = os.path.dirname(os.path.abspath(__file__))
    column_config_path = os.path.join(config_dir, 'configs', 'column_config_meat_freshness.json')
    
    with open(column_config_path, 'w') as f:
        json.dump(column_config, f, indent=2)
    
    return column_config_path


def load_hsi_ssanet_model(config):
    """HSI-SSANet 모델 로드"""
    model_config = config['model']
    
    # HSI_image 모듈에서 모델 가져오기
    model_module = importlib.import_module(f'models.HSI_image.{model_config["file"]}')
    
    # column_config 생성 및 저장
    column_config_path = create_meat_freshness_column_config(config)
    
    # config에 column_config 경로 추가
    if 'data' not in config:
        config['data'] = {}
    config['data']['column_config'] = column_config_path
    
    model = model_module.create_model(config)
    
    return model

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
    parser = argparse.ArgumentParser(description='Meat Freshness Classification Training')
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
                'lr': config['train']['lr'],
                'scheduler': config['train']['scheduler'],
                'save_interval': config['train'].get('save_interval', 5),
                'seed': seed
            }
            logger.log_params(params_to_log)
        except Exception as e:
            print(f"MLflow connection failed: {e}")
            print("Continuing without MLflow logging...")
            logger = None
    
    try:
        # 데이터 로더 생성
        print("\nCreating data loaders...")
        data_config = config['data']
        
        train_loader, valid_loader = create_meat_freshness_data_loaders(
            train_dir=data_config['train_dir'],
            valid_dir=data_config['valid_dir'],
            class_names=data_config['class_names'],
            image_size=tuple(data_config['image_size']),
            batch_size=data_config['batch_size'],
            num_workers=data_config['num_workers'],
            use_augmentation=data_config.get('use_flip', False) or data_config.get('use_rotation', False)
        )
        
        # 모델 생성
        print("\nCreating model...")
        model = load_hsi_ssanet_model(config)
        model = model.to(device)
        
        # 모델 정보 출력
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"Model: {config['model']['file']}")
        print(f"  Input channels: {config['model']['in_channels']}")
        print(f"  Num classes: {config['model']['num_classes']}")
        print(f"  Total parameters: {total_params:,}")
        print(f"  Trainable parameters: {trainable_params:,}")
        
        # pos_weight_info 생성 (3-class 분류)
        # 클래스 불균형 보정: 각 클래스의 역빈도를 계산
        train_class_counts = [675, 630, 510]  # FRESH, HALF-FRESH, SPOILED
        total_samples = sum(train_class_counts)
        pos_weights = [total_samples / (len(train_class_counts) * count) for count in train_class_counts]
        
        pos_weight_info = {
            'cls_indices': list(range(config['model']['num_classes'])),  # [0, 1, 2]
            'pos_weight': pos_weights  # [0.89, 0.96, 1.19] - SPOILED에 더 높은 가중치
        }
        
        print(f"Class balancing weights: {pos_weights}")
        
        # 훈련기 생성 (HSITrainer 재사용)
        trainer = HSITrainer(model, device, config, pos_weight_info=pos_weight_info)
        
        # 플롯 키 설정 (분류 작업용)
        plot_keys = config.get('plot_keys', ["accuracy", "precision", "recall", "f1_score"])
        
        # 훈련 수행
        print("\n" + "="*70)
        print("Starting training...")
        print("="*70)
        
        training_results = trainer.train(
            train_loader=train_loader,
            val_loader=valid_loader,
            num_epochs=config['train']['epochs'],
            logger=logger
        )
        
        # 테스트 평가 (validation set 사용)
        print("\nEvaluating on validation set...")
        test_metrics = trainer.evaluate(valid_loader)
        
        # 최종 결과 로깅
        if logger is not None:
            # 훈련 곡선 로깅
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
            
            log_training_summary(
                logger=logger,
                config=config,
                final_metrics=final_metrics,
                training_time=training_results['training_time']
            )

            run_id = logger.run_id
            print(f"\nMLflow run ID: {run_id}")
        
        print("\n" + "="*70)
        print("Training completed successfully!")
        print("="*70)
        
        # 최종 성능 출력
        if 'cls_f1_score' in test_metrics:
            print(f"\nFinal Validation Metrics:")
            print(f"  Accuracy: {test_metrics.get('cls_accuracy', 0):.4f}")
            print(f"  F1 Score: {test_metrics['cls_f1_score']:.4f}")
            print(f"  Precision: {test_metrics.get('cls_precision', 0):.4f}")
            print(f"  Recall: {test_metrics.get('cls_recall', 0):.4f}")
        
        if 'combined_score' in test_metrics:
            print(f"  Combined Score: {test_metrics['combined_score']:.4f}")
        
    except Exception as e:
        print(f"Error during training: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        # MLflow run 종료
        if logger is not None:
            logger.end_run()
            
        return run_id


if __name__ == "__main__":
    main()
