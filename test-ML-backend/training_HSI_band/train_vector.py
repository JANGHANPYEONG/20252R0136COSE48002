import argparse
import json
import pandas as pd
import mlflow
import torch
import random
import numpy as np
import os
from typing import Dict, List, Tuple

from utils.dataset import VectorDataset, load_vector_data
from utils.evaluation import BandSelectionEvaluator
from utils.add_param import add_arg, add_param, validate_config
from utils.model_loader import load_preprocessing_model, load_training_model, validate_model_config

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

def load_config(config_path: str) -> Dict:
    """Config 파일을 로드합니다."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config

def run_preprocessing_stage(pre_config: Dict, dataset: VectorDataset, params: Dict, evaluator: BandSelectionEvaluator) -> List[int]:
    """전처리 단계를 실행합니다."""
    print("\n" + "="*50)
    print("     Preprocessing Stage")
    print("="*50)
    
    # 전처리 모델 로딩
    pre_model = load_preprocessing_model(pre_config)
    
    # 전처리 실행
    evaluator.start_timer()
    pre_selected_bands = pre_model.select_bands(
        spectral_data=dataset.spectral_data,
        labels=dataset.labels,
        target_bands=params['pre_target_bands']
    )
    
    # 전처리 결과 평가
    pre_metrics = evaluator.evaluate_preprocessing(
        original_bands=dataset.spectral_data.shape[1],
        selected_bands=pre_selected_bands,
        target_bands=params['pre_target_bands'],
        method_name=pre_config['preprocessing']['model_name']
    )
    
    print(f"Preprocessing completed: {len(pre_selected_bands)} bands selected")
    print(f"Preprocessing metrics: {pre_metrics}")
    
    return pre_selected_bands

def run_training_stage(train_config: Dict, dataset: VectorDataset, pre_selected_bands: List[int], 
                      params: Dict, evaluator: BandSelectionEvaluator) -> Tuple[List[int], List[float]]:
    """본처리 단계를 실행합니다."""
    print("\n" + "="*50)
    print("     Training Stage")
    print("="*50)
    
    # 본처리 모델 로딩
    train_model = load_training_model(train_config)
    
    # 전처리된 데이터로 본처리 실행
    evaluator.start_timer()
    final_selected_bands, band_scores = train_model.select_bands_with_scores(
        spectral_data=dataset.spectral_data,
        labels=dataset.labels,
        pre_selected_bands=pre_selected_bands,
        target_bands=params['final_target_bands']
    )
    
    # 본처리 결과 평가
    train_metrics = evaluator.evaluate_training(
        selected_bands=final_selected_bands,
        band_scores=band_scores,
        target_bands=params['final_target_bands'],
        method_name=train_config['training']['model_name']
    )
    
    print(f"Training completed: {len(final_selected_bands)} bands selected")
    print(f"Training metrics: {train_metrics}")
    
    return final_selected_bands, band_scores

def main():
    # Config 파일 파싱
    config_argparser = argparse.ArgumentParser(description='HSI Vector Band Selection Pipeline')
    config_argparser.add_argument('--config', default="./configs/vector_pipeline_config.json", 
                                 type=str, help="Path to main config file")
    config_args, remaining_args = config_argparser.parse_known_args()
    
    # 메인 config 로드
    main_config = load_config(config_args.config)
    
    # Arguments 파싱
    args, train_type = add_arg(main_config, remaining_args)
    
    # 파라미터 설정
    params = add_param(train_type, args, main_config)
    
    # Config 유효성 검증
    if not validate_config(main_config):
        raise ValueError("Invalid main config")
    
    # 전처리/본처리 config 로드
    pre_config = load_config(params['pre_config_path'])
    train_config = load_config(params['train_config_path'])
    
    # 모델 config 유효성 검증
    if not validate_model_config(pre_config, 'preprocessing'):
        raise ValueError("Invalid preprocessing config")
    if not validate_model_config(train_config, 'training'):
        raise ValueError("Invalid training config")
    
    # MLflow 설정
    experiment = args.experiment if args.experiment is not None else main_config.get('experiment', 'hsi_band_selection')
    run_name = args.run if args.run is not None else main_config.get('run', 'vector_pipeline')
    port = args.port
    
    mlflow.set_tracking_uri('http://0.0.0.0:' + str(port))
    mlflow.set_experiment(experiment)
    
    # 랜덤 시드 설정
    seed = args.seed if args.seed is not None else main_config.get('hyperparameters', {}).get('seed', 42)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    # 데이터 로딩
    csv_path = args.csv_path if args.csv_path else main_config.get('data', {}).get('csv_path', './datasets_HSI/label/label.csv')
    dataset = load_vector_data(csv_path, main_config, is_train=True)
    
    print(f"\nDataset loaded: {dataset.get_spectral_info()}")
    
    # 평가기 초기화
    evaluator = BandSelectionEvaluator()
    
    # MLflow run 시작
    with mlflow.start_run(run_name=run_name) as run:
        print(f"MLflow run_id: {run.info.run_id}")
        
        # 기본 파라미터 MLflow에 기록
        mlflow.log_dict(main_config, 'config/main_config.json')
        mlflow.log_dict(pre_config, 'config/pre_config.json')
        mlflow.log_dict(train_config, 'config/train_config.json')
        
        mlflow.log_param("pre_target_bands", params['pre_target_bands'])
        mlflow.log_param("final_target_bands", params['final_target_bands'])
        mlflow.log_param("pre_model", pre_config['preprocessing']['model_name'])
        mlflow.log_param("train_model", train_config['training']['model_name'])
        mlflow.log_param("csv_path", csv_path)
        mlflow.log_param("seed", seed)
        
        # 전처리 단계 실행
        pre_selected_bands = run_preprocessing_stage(pre_config, dataset, params, evaluator)
        
        # 본처리 단계 실행
        final_selected_bands, band_scores = run_training_stage(
            train_config, dataset, pre_selected_bands, params, evaluator
        )
        
        # 전체 파이프라인 평가
        pipeline_metrics = evaluator.evaluate_pipeline(
            original_bands=dataset.spectral_data.shape[1],
            pre_selected_bands=pre_selected_bands,
            final_selected_bands=final_selected_bands,
            final_scores=band_scores,
            target_bands=params['final_target_bands'],
            pre_method=pre_config['preprocessing']['model_name'],
            train_method=train_config['training']['model_name']
        )
        
        # 결과를 MLflow에 기록
        mlflow.log_dict(pipeline_metrics, 'results/pipeline_metrics.json')
        
        # 선택된 밴드 정보 저장
        results = {
            'pre_selected_bands': pre_selected_bands,
            'final_selected_bands': final_selected_bands,
            'band_scores': band_scores,
            'pipeline_metrics': pipeline_metrics
        }
        
        mlflow.log_dict(results, 'results/band_selection_results.json')
        
        # 결과 출력
        print("\n" + "="*50)
        print("     Final Results")
        print("="*50)
        print(f"Original bands: {dataset.spectral_data.shape[1]}")
        print(f"Pre-selected bands: {len(pre_selected_bands)}")
        print(f"Final selected bands: {len(final_selected_bands)}")
        print(f"Final band scores range: {min(band_scores):.4f} - {max(band_scores):.4f}")
        print(f"Total reduction ratio: {pipeline_metrics['total_reduction_ratio']:.2%}")
        
        # 결과 저장 (옵션)
        if params['save_results']:
            output_dir = params['output_dir']
            os.makedirs(output_dir, exist_ok=True)
            
            # 메트릭 저장
            evaluator.save_metrics(os.path.join(output_dir, 'metrics.csv'))
            
            # 결과 JSON 저장
            with open(os.path.join(output_dir, 'results.json'), 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\nResults saved to: {output_dir}")
        
        print(f"\nPipeline completed successfully!")
        print(f"MLflow run: {run.info.run_id}")

if __name__ == "__main__":
    main() 