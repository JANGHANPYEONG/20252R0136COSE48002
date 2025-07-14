import argparse
import json
import pandas as pd
import mlflow
import torch
import random
import numpy as np
import os
from typing import Dict, List, Tuple
from collections import defaultdict

from utils.dataset import VectorDataset, load_vector_data
from utils.evaluation import BandSelectionEvaluator
from utils.add_param import add_arg, add_param, validate_config
from utils.model_loader import load_preprocessing_model, load_training_model, validate_model_config

def convert_numpy_types(obj):
    """NumPy 타입을 Python 기본 타입으로 변환"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {convert_numpy_types(k): convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

def load_config(config_path: str) -> Dict:
    """Config 파일을 로드합니다."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config

def run_single_label_training(label_idx: int, label_name: str, spectral_data: np.ndarray, 
                            single_label: np.ndarray, pre_config: Dict, train_config: Dict,
                            params: Dict, evaluator: BandSelectionEvaluator,
                            mlflow_info: Dict) -> Tuple[List[int], List[int], List[float]]:
    """단일 라벨에 대한 밴드 선택을 수행합니다."""
    print(f"\n--- Processing Label {label_idx+1}: {label_name} ---")
    
    # MLflow 중첩 실행
    with mlflow.start_run(run_name=f"label_{label_idx+1}_{label_name}", nested=True) as label_run:
        # 1. 전처리 모델 로딩 및 실행
        print(f"Step 1: Preprocessing for {label_name}")
        pre_config_with_mlflow = pre_config.copy()
        pre_config_with_mlflow['mlflow_info'] = mlflow_info.copy()
        pre_config_with_mlflow['mlflow_info']['current_label'] = label_name
        pre_config_with_mlflow['mlflow_info']['current_label_idx'] = label_idx
        
        pre_model = load_preprocessing_model(pre_config_with_mlflow)
        
        evaluator.start_timer()
        pre_selected_bands = pre_model.select_bands(
            spectral_data=spectral_data,
            labels=single_label,
            target_bands=params['pre_target_bands']
        )
        pre_time = evaluator.end_timer()
        
        # 전처리 결과를 MLflow에 기록
        mlflow.log_param("label_name", label_name)
        mlflow.log_param("label_index", label_idx)
        mlflow.log_param("pre_processing_time", pre_time)
        mlflow.log_param("pre_selected_bands_count", len(pre_selected_bands))
        mlflow.log_dict({"pre_selected_bands": pre_selected_bands}, "preprocessing/pre_selected_bands.json")
        
        print(f"Preprocessing completed for {label_name}: {len(pre_selected_bands)} bands selected in {pre_time:.2f}s")
        
        # 2. 본처리 모델 로딩 및 실행
        print(f"Step 2: Training-based Band Selection for {label_name}")
        train_config_with_mlflow = train_config.copy()
        train_config_with_mlflow['mlflow_info'] = mlflow_info.copy()
        train_config_with_mlflow['mlflow_info']['current_label'] = label_name
        train_config_with_mlflow['mlflow_info']['current_label_idx'] = label_idx
        
        train_model = load_training_model(train_config_with_mlflow)
        
        evaluator.start_timer()
        final_selected_bands, band_scores = train_model.select_bands_with_scores(
            spectral_data=spectral_data,
            labels=single_label,
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
        
        print(f"Training completed for {label_name}: {len(final_selected_bands)} bands selected in {train_time:.2f}s")
        
        return pre_selected_bands, final_selected_bands, band_scores

def main():
    # Config 파일 파싱
    config_argparser = argparse.ArgumentParser(description='HSI Multi-Label Vector Band Selection Pipeline')
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
    experiment = args.experiment if args.experiment is not None else main_config.get('experiment', 'hsi_multilabel_band_selection')
    run_name = args.run if args.run is not None else main_config.get('run', 'multilabel_vector_pipeline')
    
    # MLflow 설정을 파라미터에서 가져오기
    mlflow_tracking_uri = params['mlflow_tracking_uri']
    mlflow_port = params['mlflow_port']
    
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment)
    
    # 랜덤 시드 설정
    seed = args.seed if args.seed is not None else main_config.get('hyperparameters', {}).get('seed', 42)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    # 데이터 로딩
    csv_path = params['csv_path']
    dataset = load_vector_data(csv_path, main_config, is_train=True)
    
    print(f"\nDataset loaded: {dataset.get_spectral_info()}")
    print(f"CSV path: {csv_path}")
    print(f"Total samples: {len(dataset)}")
    print(f"Total spectral bands: {dataset.spectral_data.shape[1]}")
    print(f"Total labels: {dataset.labels.shape[1]}")
    
    # 라벨 정보 가져오기
    column_config = json.load(open("datasets_HSI/column_config.json", 'r'))
    label_names = column_config['label_columns']
    num_labels = len(label_names)
    
    print(f"Label names: {label_names}")
    
    # 평가기 초기화
    evaluator = BandSelectionEvaluator()
    
    # 전체 결과 저장용 딕셔너리
    all_results = {
        'label_results': {},
        'summary': {
            'total_labels': num_labels,
            'label_names': label_names,
            'original_bands': dataset.spectral_data.shape[1],
            'pre_target_bands': params['pre_target_bands'],
            'final_target_bands': params['final_target_bands']
        }
    }
    
    # 통합 MLflow run 시작
    with mlflow.start_run(run_name=run_name) as run:
        print(f"MLflow run_id: {run.info.run_id}")
        print(f"MLflow tracking URI: {mlflow_tracking_uri}")
        
        # MLflow 정보 설정
        mlflow_info = {
            "experiment_name": experiment,
            "parent_run_id": run.info.run_id
        }
        
        # 기본 파라미터 MLflow에 기록
        mlflow.log_dict(main_config, 'config/main_config.json')
        mlflow.log_dict(pre_config, 'config/pre_config.json')
        mlflow.log_dict(train_config, 'config/train_config.json')
        
        # 파라미터 기록
        mlflow.log_param("total_labels", num_labels)
        mlflow.log_param("pre_target_bands", params['pre_target_bands'])
        mlflow.log_param("final_target_bands", params['final_target_bands'])
        mlflow.log_param("pre_model", pre_config['preprocessing']['model_name'])
        mlflow.log_param("train_model", train_config['training']['model_name'])
        mlflow.log_param("csv_path", csv_path)
        mlflow.log_param("seed", seed)
        mlflow.log_param("total_original_bands", dataset.spectral_data.shape[1])
        
        # 각 라벨별로 개별 학습 수행
        for label_idx in range(num_labels):
            label_name = label_names[label_idx]
            single_label = dataset.labels[:, label_idx]
            
            print(f"\n{'='*60}")
            print(f"Processing Label {label_idx+1}/{num_labels}: {label_name}")
            print(f"{'='*60}")
            
            # 단일 라벨에 대한 밴드 선택 수행
            pre_selected_bands, final_selected_bands, band_scores = run_single_label_training(
                label_idx, label_name, dataset.spectral_data, single_label,
                pre_config, train_config, params, evaluator, mlflow_info
            )
            
            # 결과 저장 (밴드 인덱스를 int로 변환)
            label_result = {
                'label_name': label_name,
                'label_index': label_idx,
                'pre_selected_bands': [int(band) for band in pre_selected_bands],
                'final_selected_bands': [int(band) for band in final_selected_bands],
                'band_scores': band_scores,
                'label_distribution': {
                    'total_samples': len(single_label),
                    'positive_samples': int(np.sum(single_label)),
                    'negative_samples': int(np.sum(single_label == 0)),
                    'positive_ratio': float(np.mean(single_label))
                }
            }
            
            all_results['label_results'][label_name] = label_result
            
            # MLflow에 라벨별 결과 기록
            mlflow.log_dict(label_result, f'label_results/{label_name}_results.json')
        
        # 전체 요약 통계 계산
        print(f"\n{'='*60}")
        print("     Multi-Label Band Selection Summary")
        print(f"{'='*60}")
        
        # 밴드 선택 통계
        all_pre_bands = set()
        all_final_bands = set()
        band_usage_count = defaultdict(int)
        
        for label_name, result in all_results['label_results'].items():
            # 밴드 인덱스를 int로 변환하여 처리
            pre_bands = [int(band) for band in result['pre_selected_bands']]
            final_bands = [int(band) for band in result['final_selected_bands']]
            
            all_pre_bands.update(pre_bands)
            all_final_bands.update(final_bands)
            
            for band in final_bands:
                band_usage_count[band] += 1
        
        # 요약 통계 (NumPy 타입을 Python 기본 타입으로 변환)
        summary_stats = {
            'unique_pre_bands': len(all_pre_bands),
            'unique_final_bands': len(all_final_bands),
            'most_used_bands': [(int(k), int(v)) for k, v in sorted(band_usage_count.items(), key=lambda x: x[1], reverse=True)],
            'band_usage_distribution': {int(k): int(v) for k, v in band_usage_count.items()},
            'average_bands_per_label': float(len(all_final_bands) / num_labels)
        }
        
        all_results['summary']['statistics'] = summary_stats
        
        # 결과 출력
        print(f"Total labels processed: {num_labels}")
        print(f"Unique pre-selected bands across all labels: {len(all_pre_bands)}")
        print(f"Unique final selected bands across all labels: {len(all_final_bands)}")
        print(f"Average bands per label: {summary_stats['average_bands_per_label']:.2f}")
        
        print(f"\nMost frequently selected bands:")
        for band, count in summary_stats['most_used_bands'][:10]:
            print(f"  Band {band}: selected by {count}/{num_labels} labels")
        
        # MLflow에 전체 결과 기록 (NumPy 타입 변환 후)
        all_results_converted = convert_numpy_types(all_results)
        summary_stats_converted = convert_numpy_types(summary_stats)
        
        mlflow.log_dict(all_results_converted, 'results/multilabel_results.json')
        mlflow.log_dict(summary_stats_converted, 'results/summary_statistics.json')
        
        # 결과 저장 (옵션)
        if params['save_results']:
            output_dir = params['output_dir']
            os.makedirs(output_dir, exist_ok=True)
            
            # 전체 결과 JSON 저장 (NumPy 타입 변환 후)
            all_results_converted = convert_numpy_types(all_results)
            with open(os.path.join(output_dir, 'multilabel_results.json'), 'w') as f:
                json.dump(all_results_converted, f, indent=2)
            
            # 라벨별 결과 개별 저장
            for label_name, result in all_results['label_results'].items():
                label_dir = os.path.join(output_dir, f'label_{label_name}')
                os.makedirs(label_dir, exist_ok=True)
                
                result_converted = convert_numpy_types(result)
                with open(os.path.join(label_dir, 'band_selection.json'), 'w') as f:
                    json.dump(result_converted, f, indent=2)
            
            print(f"\nResults saved to: {output_dir}")
        
        print(f"\nMulti-label band selection completed successfully!")
        print(f"MLflow run: {run.info.run_id}")

if __name__ == "__main__":
    main() 