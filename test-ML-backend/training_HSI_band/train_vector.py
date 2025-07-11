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

def run_integrated_training(pre_config: Dict, train_config: Dict, dataset: VectorDataset, 
                          params: Dict, evaluator: BandSelectionEvaluator, 
                          mlflow_experiment: str, mlflow_run_id: str) -> Tuple[List[int], List[int], List[float]]:
    """전처리와 본처리를 통합하여 하나의 학습 과정으로 실행합니다."""
    print("\n" + "="*50)
    print("     Integrated Band Selection Training")
    print("="*50)
    
    # MLflow 정보를 config에 추가
    mlflow_info = {
        "experiment_name": mlflow_experiment,
        "parent_run_id": mlflow_run_id
    }
    
    # 1. 전처리 모델 로딩 및 실행
    print("Step 1: Preprocessing")
    pre_config_with_mlflow = pre_config.copy()
    pre_config_with_mlflow['mlflow_info'] = mlflow_info
    
    pre_model = load_preprocessing_model(pre_config_with_mlflow)
    
    evaluator.start_timer()
    pre_selected_bands = pre_model.select_bands(
        spectral_data=dataset.spectral_data,
        labels=dataset.labels,
        target_bands=params['pre_target_bands']
    )
    pre_time = evaluator.end_timer()
    
    # 전처리 결과를 MLflow에 기록
    mlflow.log_param("pre_processing_time", pre_time)
    mlflow.log_param("pre_selected_bands_count", len(pre_selected_bands))
    mlflow.log_dict({"pre_selected_bands": pre_selected_bands}, "preprocessing/pre_selected_bands.json")
    
    print(f"Preprocessing completed: {len(pre_selected_bands)} bands selected in {pre_time:.2f}s")
    
    # 2. 본처리 모델 로딩 및 실행 (실제 학습)
    print("Step 2: Training-based Band Selection")
    train_config_with_mlflow = train_config.copy()
    train_config_with_mlflow['mlflow_info'] = mlflow_info
    
    train_model = load_training_model(train_config_with_mlflow)
    
    evaluator.start_timer()
    final_selected_bands, band_scores = train_model.select_bands_with_scores(
        spectral_data=dataset.spectral_data,
        labels=dataset.labels,
        pre_selected_bands=pre_selected_bands,
        target_bands=params['final_target_bands']
    )
    train_time = evaluator.end_timer()
    
    # 본처리 결과를 MLflow에 기록
    mlflow.log_param("training_time", train_time)
    mlflow.log_param("final_selected_bands_count", len(final_selected_bands))
    mlflow.log_dict({
        "final_selected_bands": final_selected_bands,
        "band_scores": band_scores
    }, "training/final_results.json")
    
    print(f"Training completed: {len(final_selected_bands)} bands selected in {train_time:.2f}s")
    
    return pre_selected_bands, final_selected_bands, band_scores

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
    
    # 통합 MLflow run 시작
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
        mlflow.log_param("total_original_bands", dataset.spectral_data.shape[1])
        
        # 통합 학습 실행 (MLflow 정보 전달)
        pre_selected_bands, final_selected_bands, band_scores = run_integrated_training(
            pre_config, train_config, dataset, params, evaluator, 
            experiment, run.info.run_id
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
        
        print(f"\nIntegrated training completed successfully!")
        print(f"MLflow run: {run.info.run_id}")

if __name__ == "__main__":
    main() 