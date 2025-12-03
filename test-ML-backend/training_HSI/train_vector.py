#!/usr/bin/env python3
"""
Vector ML 모델 학습 파이프라인

이 스크립트는 HSI 파생 벡터(feature) 데이터를 입력으로 받아 전통 ML 모델
(RandomForest, Gradient Boosting 등)을 학습/튜닝하는 엔드 투 엔드 파이프라인입니다.
설정 파일 하나로 데이터 경로, 라벨/특성 컬럼 정의, 모델 타입과 하이퍼파라미터 그리드,
평가지표, 시드 등을 지정하면 아래 과정을 자동화합니다.

주요 기능:
  - 설정 파일 기반 데이터 로드 및 라벨 메타데이터 추출
  - 학습/테스트 분리와 pos_weight 계산으로 클래스 불균형 대응
  - 모델 구성 검증과 SearchHyperparameter 클래스를 통한 그리드/랜덤 탐색
  - MLflow(선택) 로깅: 하이퍼파라미터, 베스트 모델 아티팩트, 메트릭 기록
  - 멀티태스크 분류/회귀 메트릭 계산 및 컬럼별 테스트 점수 출력

사용 예시:
    python train_vector.py --config configs/HSI_vector/vector_randomforest.json
"""

from utils.trainer_vector import SearchHyperparameter
from utils.model_loader import load_vector_model as load_model, validate_vector_model_config as validate_model_config, get_vector_model_info as get_model_info
from utils.logger import create_logger, log_training_ml_summary
from utils.dataset_vector import load_vector_data, get_label_info
from sklearn.model_selection import train_test_split
import os
import sys
import json
import argparse
import numpy as np
import random
import warnings
import time
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
    print(f"Random seed set to: {seed}\n")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='HSI Vector Training')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to configuration file')
    parser.add_argument('--no-mlflow', action='store_true',
                        help='Disable MLflow logging')
    args = parser.parse_args()

    run_id = None

    # 설정 로드
    print("Loading configuration...")
    config = load_config(args.config)

    # 시드 설정
    seed = config.get('seed', 42)
    csv_path = config.get('data', {}).get('csv', 'data/vector_data.csv')
    column_config_path = config.get('data', {}).get('column_config', 'configs/HSI_vector/column_config.json')
    setup_seed(seed)

    # MLflow 로거 설정
    logger = None
    if not args.no_mlflow:
        logger = create_logger(config)
        logger.start_run(run_name="hsi_vector")
        run_id = logger.run.info.run_id  # MLflow run ID 저장
        
        # 하이퍼파라미터 로깅
        params_to_log = {
            'model_file': config['model']['file'],
            'num_classes': config['model']['num_classes'],
            'method': config['train']['method'],
            'scoring': config['train']['scoring'],
            'seed': seed
        }
        logger.log_params(params_to_log)
    try:
        # 데이터 불러오기
        dataset, pos_weight_info = load_vector_data(
            csv_path=csv_path,
            column_config_path=column_config_path
        )
        #tmp data for hybrid
        y_tmp, _ = load_vector_data(
            csv_path="/mnt/data/datasets_HSI/label/VS_label.csv",
            column_config_path=column_config_path
        )
        y_tmp = y_tmp.labels
        ############################
        X = dataset.spectral_data
        y = dataset.labels

        test_split = config.get('data', {}).get('test_split', 0.1)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_split,
            random_state=seed
        )

        # 라벨 정보 가져오기
        label_info = get_label_info(column_config_path=column_config_path)
        print(f"Label info: {label_info}\n")

        # 모델 설정 검증
        print("Validating model configuration...")
        if not validate_model_config(config):
            raise ValueError("Invalid model configuration")

        # 모델 불러오기
        estimator = load_model(config)

        # 모델 정보 출력
        estimator_info = get_model_info(config)
        print(f"Model info: {estimator_info}\n")

        # Hyperparameter tuning을 위한 class 불러오기
        grid = SearchHyperparameter(
            estimator=estimator,
            config=config,
            pos_weight_info=pos_weight_info
        )
        print('Training and tuning model...')

        start_time = time.time()
        grid.fit(X_train, y_train)
        training_time = time.time() - start_time
        print(f"✅ Training done in {training_time/60:.2f} min")

        if grid.searcher == 'no' :
            y_pred = estimator.predict(X_test)
            results = grid.calculate_metrics(y_tmp, y_pred)
            best_estimator = estimator
            best_val_score = 42
        else :
            best_params = grid.searcher.best_params_
            best_estimator = grid.searcher.best_estimator_
            best_val_score = grid.searcher.best_score_
            print(f"Best Parameter: {best_params}\n")

            # 평가 데이터에 대해 예측 수행
            y_pred = best_estimator.predict(X_test)
            results = grid.calculate_metrics(y_test, y_pred)

        # 최종 결과 로깅
        if logger is not None:
            logger.log_model_ml(best_estimator, "best_model")
            print("Best estimator saved!\n")

            # 최종 메트릭 로깅
            final_metrics = {
                'best_val_loss': best_val_score,
                'combined_score': results['combined_score']
            }
            if 'cls_f1' in results.keys():
                final_metrics['cls_f1'] = results['cls_f1']
            if 'reg_r2' in results.keys():
                final_metrics['reg_r2'] = results['reg_r2']

            log_training_ml_summary(
                logger=logger,
                config=config,
                final_metrics=final_metrics,
                training_time=training_time,
                to_json=results
            )
        print("\nTraining completed successfully!")

        column_names = label_info['label_columns']
        for column_name in column_names:
            print(f"Test scores for {column_name}")
            for metric, val in results[column_name].items():
                print(f"    Test {metric} score: {val:.4f}")
            print()

        print(f"Test Combined Score: {results.get('combined_score', 0):.4f}")

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
