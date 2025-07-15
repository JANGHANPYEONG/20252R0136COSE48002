import argparse
import json
import pandas as pd
import mlflow
import mlflow.sklearn
import torch
import random
import numpy as np
import os
from typing import Dict, List, Tuple
from collections import defaultdict
from sklearn.preprocessing import StandardScaler

from utils.dataset import VectorDataset, load_vector_data, split_vector_data
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
    # Config 파일을 로드합니다.
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
    
    # trouble shooting을 위한 경로 확인 test code
    print(">> Loaded pre_config:")
    print(json.dumps(pre_config, indent=2, ensure_ascii=False))
    # 파일 경로가 있다면
    if 'preprocessing' in pre_config and 'model_file' in pre_config['preprocessing']:
        mf = pre_config['preprocessing']['model_file']
        print(">> model_file 필드:", mf)
        print(">> os.path.exists:", os.path.exists(mf), "->", os.path.abspath(mf))

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
    
    # GPU 재현성 보장 설정
    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        print("GPU reproducibility settings applied")
    
    # 데이터 로딩
    csv_path = params['csv_path']
    dataset = load_vector_data(csv_path, main_config, is_train=True)
    
    print(f"\nDataset loaded: {dataset.get_spectral_info()}")
    print(f"CSV path: {csv_path}")
    print(f"Total samples: {len(dataset)}")
    print(f"Total spectral bands: {dataset.spectral_data.shape[1]}")
    print(f"Total labels: {dataset.labels.shape[1]}")
    
    # 데이터 분할 수행 (데이터 누출 방지)
    print(f"\n{'='*60}")
    print("     Data Splitting (Preventing Data Leakage)")
    print(f"{'='*60}")
    
    train_ratio = main_config.get('data_split', {}).get('train_ratio', 0.8)
    val_ratio = main_config.get('data_split', {}).get('val_ratio', 0.1)
    test_ratio = main_config.get('data_split', {}).get('test_ratio', 0.1)
    
    train_dataset, val_dataset, test_dataset = split_vector_data(
        dataset, 
        train_ratio=train_ratio,
        val_ratio=val_ratio, 
        test_ratio=test_ratio,
        random_state=seed
    )
    
    # StandardScaler 초기화 및 train 데이터로 fit (데이터 누출 방지)
    print(f"\n{'='*60}")
    print("     StandardScaler Initialization (Train Data Only)")
    print(f"{'='*60}")
    
    train_indices = train_dataset.indices
    train_spectral_data = dataset.spectral_data[train_indices]
    
    # 전체 스펙트럼 데이터에 대한 StandardScaler fit (한 번만)
    global_scaler = StandardScaler()
    global_scaler.fit(train_spectral_data)
    
    # train 데이터 정규화 (한 번만 수행)
    train_spectral_data_scaled = global_scaler.transform(train_spectral_data)
    
    print(f"StandardScaler fitted on train data: {train_spectral_data.shape}")
    print(f"Train data normalized: {train_spectral_data_scaled.shape}")
    print(f"Scaler mean shape: {global_scaler.mean_.shape}")
    print(f"Scaler scale shape: {global_scaler.scale_.shape}")
    
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
            'final_target_bands': params['final_target_bands'],
            'data_split': {
                'train_ratio': train_ratio,
                'val_ratio': val_ratio,
                'test_ratio': test_ratio,
                'train_samples': len(train_dataset),
                'val_samples': len(val_dataset),
                'test_samples': len(test_dataset)
            },
            'preprocessing': {
                'standard_scaler_fitted': True,
                'scaler_mean_shape': global_scaler.mean_.shape[0],
                'scaler_scale_shape': global_scaler.scale_.shape[0],
                'scaler_fitted_on': 'train_data_only'
            }
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
        mlflow.log_param("train_ratio", train_ratio)
        mlflow.log_param("val_ratio", val_ratio)
        mlflow.log_param("test_ratio", test_ratio)
        mlflow.log_param("train_samples", len(train_dataset))
        mlflow.log_param("val_samples", len(val_dataset))
        mlflow.log_param("test_samples", len(test_dataset))
        mlflow.log_param("standard_scaler_fitted", True)
        mlflow.log_param("scaler_mean_shape", global_scaler.mean_.shape[0])
        mlflow.log_param("scaler_scale_shape", global_scaler.scale_.shape[0])
        
        # StandardScaler를 MLflow artifact로 저장 (재현성 보장)
        mlflow.sklearn.log_model(global_scaler, "scaler")
        print("StandardScaler saved as MLflow artifact")
        
        # 각 라벨별로 개별 학습 수행 (정규화된 train 데이터 사용)
        for label_idx in range(num_labels):
            label_name = label_names[label_idx]
            
            # train 데이터에서만 라벨 추출 (이미 정규화된 데이터 사용)
            train_single_label = dataset.labels[train_indices, label_idx]
            
            print(f"\n{'='*60}")
            print(f"Processing Label {label_idx+1}/{num_labels}: {label_name}")
            print(f"Using TRAIN data only: {len(train_dataset)} samples")
            print(f"Using pre-normalized data: {train_spectral_data_scaled.shape}")
            print(f"{'='*60}")
            
            # 단일 라벨에 대한 밴드 선택 수행 (이미 정규화된 train 데이터 사용)
            pre_selected_bands, final_selected_bands, band_scores = run_single_label_training(
                label_idx, label_name, train_spectral_data_scaled, train_single_label,
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
                    'total_samples': len(train_single_label),
                    'positive_samples': int(np.sum(train_single_label)),
                    'negative_samples': int(np.sum(train_single_label == 0)),
                    'positive_ratio': float(np.mean(train_single_label))
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
        
        # 결과 저장 (옵션) - train/val/test 구분
        if params['save_results']:
            output_dir = params['output_dir']
            os.makedirs(output_dir, exist_ok=True)
            
            # 전체 결과 JSON 저장 (NumPy 타입 변환 후)
            all_results_converted = convert_numpy_types(all_results)
            with open(os.path.join(output_dir, 'multilabel_results.json'), 'w') as f:
                json.dump(all_results_converted, f, indent=2)
            
            # val/test 데이터도 같은 스케일러로 변환 (향후 사용을 위해)
            val_indices = val_dataset.indices
            test_indices = test_dataset.indices
            val_spectral_data = dataset.spectral_data[val_indices]
            test_spectral_data = dataset.spectral_data[test_indices]
            
            val_spectral_data_scaled = global_scaler.transform(val_spectral_data)
            test_spectral_data_scaled = global_scaler.transform(test_spectral_data)
            
            # train/val/test 구분된 결과 저장
            train_results = {
                'data_split': 'train',
                'samples': len(train_dataset),
                'label_results': all_results['label_results'],
                'spectral_data_shape': train_spectral_data_scaled.shape,
                'spectral_data_scaled_shape': train_spectral_data_scaled.shape
            }
            
            val_results = {
                'data_split': 'validation',
                'samples': len(val_dataset),
                'label_results': {},  # validation에서는 밴드 선택을 수행하지 않음
                'spectral_data_shape': val_spectral_data_scaled.shape,
                'spectral_data_scaled_shape': val_spectral_data_scaled.shape
            }
            
            test_results = {
                'data_split': 'test',
                'samples': len(test_dataset),
                'label_results': {},  # test에서는 밴드 선택을 수행하지 않음
                'spectral_data_shape': test_spectral_data_scaled.shape,
                'spectral_data_scaled_shape': test_spectral_data_scaled.shape
            }
            
            # 분할별 결과 저장
            for split_name, split_results in [('train', train_results), ('val', val_results), ('test', test_results)]:
                split_dir = os.path.join(output_dir, split_name)
                os.makedirs(split_dir, exist_ok=True)
                
                split_results_converted = convert_numpy_types(split_results)
                with open(os.path.join(split_dir, f'band_selection_{split_name}.json'), 'w') as f:
                    json.dump(split_results_converted, f, indent=2)
            
            # 라벨별 결과 개별 저장 (train 데이터 기반)
            for label_name, result in all_results['label_results'].items():
                label_dir = os.path.join(output_dir, f'label_{label_name}')
                os.makedirs(label_dir, exist_ok=True)
                
                result_converted = convert_numpy_types(result)
                with open(os.path.join(label_dir, 'band_selection_train.json'), 'w') as f:
                    json.dump(result_converted, f, indent=2)
            
            print(f"\nResults saved to: {output_dir}")
            print(f"  - Train results: {len(train_dataset)} samples")
            print(f"  - Validation results: {len(val_dataset)} samples") 
            print(f"  - Test results: {len(test_dataset)} samples")
        
        print(f"\nMulti-label band selection completed successfully!")
        print(f"MLflow run: {run.info.run_id}")

if __name__ == "__main__":
    main() 