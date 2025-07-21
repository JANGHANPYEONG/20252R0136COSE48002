#!/usr/bin/env python3
"""
Vector ML 모델 학습 파이프라인

이 스크립트는 vector 데이터를 사용하여 ML 모델을 훈련합니다.
멀티태스크 학습을 지원하며, 분류 및 회귀 작업을 동시에 수행할 수 있습니다.

사용법:
    python train_vector.py --config configs/HSI_vector/vector_randomforest.json
"""

from utils.trainer_vector import vectorTrainer
from utils.model_loader_vector import load_model, validate_model_config, get_model_info
from utils.transforms_hsi import get_train_transforms, get_val_transforms, get_test_transforms
from utils.logger import create_logger, log_training_summary
from utils.dataset_vector import load_vector_data, get_label_info
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import sys
import json
import argparse
import numpy as np
import random
import warnings
warnings.filterwarnings('ignore')


# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def load_config(config_path: str) -> dict:
    """설정 파일을 로드합니다."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


def setup_seed(seed: int):
    """랜덤 시드를 설정합니다."""
    np.random.seed(seed)
    random.seed(seed)
    print(f"Random seed set to: {seed}")


def setup_label_info(column_config_path: str):
    """라벨 타입 정보를 설정합니다."""
    # 컬럼 설정에서 라벨 정보 로드
    column_config = load_config(column_config_path)

    label_types = column_config['label_types']
    label_columns = column_config['label_columns']

     # 분류/회귀 라벨 인덱스 설정
    cls_indices = []
    reg_indices = []

    for i, label_name in enumerate(label_columns):
        if label_name in label_types['classification']:
            cls_indices.append(i)
        elif label_name in label_types['regression']:
            reg_indices.append(i)

    print(f"Label setup:")
    print(f"  Classification indices: {cls_indices}")
    print(f"  Regression indices: {reg_indices}")

    return cls_indices, reg_indices


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='HSI Vector Training')
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
    model = config.get('model', {}).get('file', 'vector_randomforest')
    num_classes = config.get('model', {}).get('num_classes', 13)
    csv_path = config.get('data', {}).get('csv', 'data/vector_data.csv')
    column_config_path = config.get('data', {}).get(
        'column_config', 'configs/HSI_vector/column_config.json')
    scaler = config.get('scaler', StandardScaler)

    setup_seed(seed)

    # MLflow 로거 설정
    logger = None
    if not args.no_mlflow:
        logger = create_logger(config)
        logger.start_run()
        
        # 하이퍼파라미터 로깅
        params_to_log = {
            'model_file': model,
            'num_classes': num_classes,
            'seed': seed
        }
        logger.log_params(params_to_log)
    try:
        # 데이터 불러오기
        dataset = load_vector_data(
            csv_path=csv_path,
            column_config_path=column_config_path
        )

        X = dataset.spectral_data
        y = dataset.labels

        val_split = config.get('data', {}).get('val_split', 0.2)
        test_split = config.get('data', {}).get('test_split', 0.1)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_split, random_state=seed
        )

        # 라벨 정보 가져오기
        label_info = get_label_info(column_config_path=column_config_path)
        print(f"Label info: {label_info}")

        clf_indices, reg_indices = setup_label_info(column_config_path=column_config_path)

        # 모델 설정 검증
        print("Validating model configuration...")
        if not validate_model_config(config):
            raise ValueError("Invalid model configuration")

        for i in range(len(y_train)):
            print("-" * 50)
            print(f"Training for label {label_info['label_columns'][i]}...")
            if i in clf_indices:
                task = 'classification'
                model = load_model(config, label_type='classification')
            elif i in reg_indices:
                task = 'regression'
                model = load_model(config, label_type='regression')
            else:
                raise ValueError(f"Unknown label index: {i}")

            print(f"Task for label index {i}: {task}")

            y_train_single_label = y_train[:, i]
            y_test_single_label = y_test[:, i]
            
            # 모델 정보 출력
            model_info = get_model_info(config)
            print(f"Model info: {model_info}")

            # 훈련기 생성
            trainer = vectorTrainer(model, task, config)

            # K-fold 설정
            K_fold = config.get('train', {}).get('K_fold', 5)

            # 훈련 수행
            print("Starting training...")
            training_results = trainer.train(
                X_train=X_train,
                y_train=y_train_single_label,
                K_fold=K_fold,
                logger=logger
            )

            # 테스트 수행
            print("Evaluating on test set...")
            test_metrics = trainer.evaluate(X_test, y_test_single_label)

            # 최종 결과 로깅
            if logger is not None:
                # 스케일러 로깅
                logger.log_scaler(scaler)

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

        print(
            f"Test Combined Score: {test_metrics.get('combined_score', 0):.4f}")

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
