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
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import cross_val_score

from utils.dataset import VectorDataset, load_vector_data, split_vector_data
from utils.evaluation import BandSelectionEvaluator
from utils.add_param import add_arg, add_param, validate_config
from utils.model_loader import load_preprocessing_model, load_training_model, validate_model_config

class StandardScalerWrapper:
    """StandardScaler를 래핑하여 MLflow 호환성을 개선하는 클래스"""
    
    def __init__(self, scaler: StandardScaler):
        self.scaler = scaler
    
    def transform(self, X):
        """데이터 변환"""
        return self.scaler.transform(X)
    
    def fit_transform(self, X):
        """데이터 피팅 및 변환"""
        return self.scaler.fit_transform(X)
    
    def inverse_transform(self, X):
        """역변환"""
        return self.scaler.inverse_transform(X)
    
    def predict(self, X):
        """MLflow 호환성을 위한 predict 메서드 (transform과 동일)"""
        return self.scaler.transform(X)
    
    def get_params(self, deep=True):
        """sklearn 호환성을 위한 파라미터 반환"""
        return self.scaler.get_params(deep)
    
    def set_params(self, **params):
        """sklearn 호환성을 위한 파라미터 설정"""
        return self.scaler.set_params(**params)

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

def evaluate_band_selection(spectral_data: np.ndarray, labels: np.ndarray, 
                          selected_bands: List[int], label_name: str, 
                          train_indices: np.ndarray, val_indices: np.ndarray, 
                          test_indices: np.ndarray, scaler: StandardScaler,
                          mlflow_info: Dict, label_type: str) -> Dict[str, float]:
    """
    전체 밴드와 선택된 밴드로 분류/회귀 모델을 훈련하고 비교 평가합니다.
    """
    print(f"\n--- Evaluating Band Selection for {label_name} ({label_type}) ---")
    
    # 전체 밴드 데이터
    X_full = spectral_data
    
    # 선택된 밴드로 데이터 추출
    X_selected = spectral_data[:, selected_bands]
    
    # 데이터 분할 (원본 인덱스 사용)
    X_full_train = X_full[train_indices]
    X_full_val = X_full[val_indices]
    X_full_test = X_full[test_indices]
    
    X_selected_train = X_selected[train_indices]
    X_selected_val = X_selected[val_indices]
    X_selected_test = X_selected[test_indices]
    
    y_train = labels[train_indices]
    y_val = labels[val_indices]
    y_test = labels[test_indices]
    
    # 전체 밴드용 StandardScaler fit
    full_scaler = StandardScaler()
    full_scaler.fit(X_full_train)
    
    # 선택된 밴드용 StandardScaler fit
    selected_scaler = StandardScaler()
    selected_scaler.fit(X_selected_train)
    
    # 스케일링
    X_full_train_scaled = full_scaler.transform(X_full_train)
    X_full_val_scaled = full_scaler.transform(X_full_val)
    X_full_test_scaled = full_scaler.transform(X_full_test)
    
    X_selected_train_scaled = selected_scaler.transform(X_selected_train)
    X_selected_val_scaled = selected_scaler.transform(X_selected_val)
    X_selected_test_scaled = selected_scaler.transform(X_selected_test)
    results = {}
    if label_type == 'classification':
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.svm import SVC
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        from sklearn.model_selection import cross_val_score
        
        models = {
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            'SVM': SVC(kernel='rbf', random_state=42, probability=True)
        }
        
        for model_name, model in models.items():
            print(f"\nTraining {model_name}...")
            
            # 1. 전체 밴드로 모델 훈련 및 평가
            print(f"  Evaluating with ALL bands ({X_full_train_scaled.shape[1]} features)...")
            model_full = type(model)(**model.get_params())
            model_full.fit(X_full_train_scaled, y_train)
            
            y_train_pred_full = model_full.predict(X_full_train_scaled)
            y_val_pred_full = model_full.predict(X_full_val_scaled)
            y_test_pred_full = model_full.predict(X_full_test_scaled)
            
            try:
                y_train_proba_full = model_full.predict_proba(X_full_train_scaled)[:, 1]
                y_val_proba_full = model_full.predict_proba(X_full_val_scaled)[:, 1]
                y_test_proba_full = model_full.predict_proba(X_full_test_scaled)[:, 1]
            except:
                y_train_proba_full = y_train_pred_full
                y_val_proba_full = y_val_pred_full
                y_test_proba_full = y_test_pred_full
            
            # 전체 밴드 지표 계산
            metrics_full = {}
            metrics_full['train_accuracy'] = accuracy_score(y_train, y_train_pred_full)
            metrics_full['train_precision'] = precision_score(y_train, y_train_pred_full, zero_division=0)
            metrics_full['train_recall'] = recall_score(y_train, y_train_pred_full, zero_division=0)
            metrics_full['train_f1'] = f1_score(y_train, y_train_pred_full, zero_division=0)
            metrics_full['val_accuracy'] = accuracy_score(y_val, y_val_pred_full)
            metrics_full['val_precision'] = precision_score(y_val, y_val_pred_full, zero_division=0)
            metrics_full['val_recall'] = recall_score(y_val, y_val_pred_full, zero_division=0)
            metrics_full['val_f1'] = f1_score(y_val, y_val_pred_full, zero_division=0)
            metrics_full['test_accuracy'] = accuracy_score(y_test, y_test_pred_full)
            metrics_full['test_precision'] = precision_score(y_test, y_test_pred_full, zero_division=0)
            metrics_full['test_recall'] = recall_score(y_test, y_test_pred_full, zero_division=0)
            metrics_full['test_f1'] = f1_score(y_test, y_test_pred_full, zero_division=0)
            
            try:
                metrics_full['train_auc'] = roc_auc_score(y_train, y_train_proba_full)
                metrics_full['val_auc'] = roc_auc_score(y_val, y_val_proba_full)
                metrics_full['test_auc'] = roc_auc_score(y_test, y_test_proba_full)
            except:
                metrics_full['train_auc'] = 0.0
                metrics_full['val_auc'] = 0.0
                metrics_full['test_auc'] = 0.0
            
            try:
                cv_scores_full = cross_val_score(model_full, X_full_train_scaled, y_train, cv=5, scoring='accuracy')
                metrics_full['cv_accuracy_mean'] = cv_scores_full.mean()
                metrics_full['cv_accuracy_std'] = cv_scores_full.std()
            except:
                metrics_full['cv_accuracy_mean'] = 0.0
                metrics_full['cv_accuracy_std'] = 0.0
            
            # 2. 선택된 밴드로 모델 훈련 및 평가
            print(f"  Evaluating with SELECTED bands ({X_selected_train_scaled.shape[1]} features)...")
            model_selected = type(model)(**model.get_params())
            model_selected.fit(X_selected_train_scaled, y_train)
            
            y_train_pred_selected = model_selected.predict(X_selected_train_scaled)
            y_val_pred_selected = model_selected.predict(X_selected_val_scaled)
            y_test_pred_selected = model_selected.predict(X_selected_test_scaled)
            
            try:
                y_train_proba_selected = model_selected.predict_proba(X_selected_train_scaled)[:, 1]
                y_val_proba_selected = model_selected.predict_proba(X_selected_val_scaled)[:, 1]
                y_test_proba_selected = model_selected.predict_proba(X_selected_test_scaled)[:, 1]
            except:
                y_train_proba_selected = y_train_pred_selected
                y_val_proba_selected = y_val_pred_selected
                y_test_proba_selected = y_test_pred_selected
            
            # 선택된 밴드 지표 계산
            metrics_selected = {}
            metrics_selected['train_accuracy'] = accuracy_score(y_train, y_train_pred_selected)
            metrics_selected['train_precision'] = precision_score(y_train, y_train_pred_selected, zero_division=0)
            metrics_selected['train_recall'] = recall_score(y_train, y_train_pred_selected, zero_division=0)
            metrics_selected['train_f1'] = f1_score(y_train, y_train_pred_selected, zero_division=0)
            metrics_selected['val_accuracy'] = accuracy_score(y_val, y_val_pred_selected)
            metrics_selected['val_precision'] = precision_score(y_val, y_val_pred_selected, zero_division=0)
            metrics_selected['val_recall'] = recall_score(y_val, y_val_pred_selected, zero_division=0)
            metrics_selected['val_f1'] = f1_score(y_val, y_val_pred_selected, zero_division=0)
            metrics_selected['test_accuracy'] = accuracy_score(y_test, y_test_pred_selected)
            metrics_selected['test_precision'] = precision_score(y_test, y_test_pred_selected, zero_division=0)
            metrics_selected['test_recall'] = recall_score(y_test, y_test_pred_selected, zero_division=0)
            metrics_selected['test_f1'] = f1_score(y_test, y_test_pred_selected, zero_division=0)
            
            try:
                metrics_selected['train_auc'] = roc_auc_score(y_train, y_train_proba_selected)
                metrics_selected['val_auc'] = roc_auc_score(y_val, y_val_proba_selected)
                metrics_selected['test_auc'] = roc_auc_score(y_test, y_test_proba_selected)
            except:
                metrics_selected['train_auc'] = 0.0
                metrics_selected['val_auc'] = 0.0
                metrics_selected['test_auc'] = 0.0
            
            try:
                cv_scores_selected = cross_val_score(model_selected, X_selected_train_scaled, y_train, cv=5, scoring='accuracy')
                metrics_selected['cv_accuracy_mean'] = cv_scores_selected.mean()
                metrics_selected['cv_accuracy_std'] = cv_scores_selected.std()
            except:
                metrics_selected['cv_accuracy_mean'] = 0.0
                metrics_selected['cv_accuracy_std'] = 0.0
            
            # 결과 저장
            results[f"{model_name}_full"] = metrics_full
            results[f"{model_name}_selected"] = metrics_selected
            
            # MLflow에 지표 기록
            for metric_name, value in metrics_full.items():
                mlflow.log_metric(f"{label_name}_{model_name}_full_{metric_name}", value)
            for metric_name, value in metrics_selected.items():
                mlflow.log_metric(f"{label_name}_{model_name}_selected_{metric_name}", value)
            
            # 성능 비교 출력
            print(f"{model_name} Results:")
            print(f"  ALL bands ({X_full_train_scaled.shape[1]} features):")
            print(f"    Test - Accuracy: {metrics_full['test_accuracy']:.4f}, F1: {metrics_full['test_f1']:.4f}")
            print(f"  SELECTED bands ({X_selected_train_scaled.shape[1]} features):")
            print(f"    Test - Accuracy: {metrics_selected['test_accuracy']:.4f}, F1: {metrics_selected['test_f1']:.4f}")
            
            # 성능 차이 계산
            accuracy_diff = metrics_selected['test_accuracy'] - metrics_full['test_accuracy']
            f1_diff = metrics_selected['test_f1'] - metrics_full['test_f1']
            print(f"  Performance difference (selected - full):")
            print(f"    Accuracy: {accuracy_diff:+.4f}, F1: {f1_diff:+.4f}")
            
            # MLflow에 성능 차이 기록
            mlflow.log_metric(f"{label_name}_{model_name}_accuracy_diff", accuracy_diff)
            mlflow.log_metric(f"{label_name}_{model_name}_f1_diff", f1_diff)

            results[f"{model_name}_accuracy_diff"] = accuracy_diff
            results[f"{model_name}_f1_diff"] = f1_diff
    elif label_type == 'regression':
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.linear_model import Ridge
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        from sklearn.model_selection import cross_val_score
        
        models = {
            'RandomForestRegressor': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            'Ridge': Ridge(random_state=42)
        }
        
        for model_name, model in models.items():
            print(f"\nTraining {model_name}...")
            
            # 1. 전체 밴드로 모델 훈련 및 평가
            print(f"  Evaluating with ALL bands ({X_full_train_scaled.shape[1]} features)...")
            model_full = type(model)(**model.get_params())
            model_full.fit(X_full_train_scaled, y_train)
            
            y_train_pred_full = model_full.predict(X_full_train_scaled)
            y_val_pred_full = model_full.predict(X_full_val_scaled)
            y_test_pred_full = model_full.predict(X_full_test_scaled)
            
            # 전체 밴드 지표 계산
            metrics_full = {}
            metrics_full['train_mse'] = mean_squared_error(y_train, y_train_pred_full)
            metrics_full['train_mae'] = mean_absolute_error(y_train, y_train_pred_full)
            metrics_full['train_r2'] = r2_score(y_train, y_train_pred_full)
            metrics_full['val_mse'] = mean_squared_error(y_val, y_val_pred_full)
            metrics_full['val_mae'] = mean_absolute_error(y_val, y_val_pred_full)
            metrics_full['val_r2'] = r2_score(y_val, y_val_pred_full)
            metrics_full['test_mse'] = mean_squared_error(y_test, y_test_pred_full)
            metrics_full['test_mae'] = mean_absolute_error(y_test, y_test_pred_full)
            metrics_full['test_r2'] = r2_score(y_test, y_test_pred_full)
            
            try:
                cv_scores_full = cross_val_score(model_full, X_full_train_scaled, y_train, cv=5, scoring='r2')
                metrics_full['cv_r2_mean'] = cv_scores_full.mean()
                metrics_full['cv_r2_std'] = cv_scores_full.std()
            except:
                metrics_full['cv_r2_mean'] = 0.0
                metrics_full['cv_r2_std'] = 0.0
            
            # 2. 선택된 밴드로 모델 훈련 및 평가
            print(f"  Evaluating with SELECTED bands ({X_selected_train_scaled.shape[1]} features)...")
            model_selected = type(model)(**model.get_params())
            model_selected.fit(X_selected_train_scaled, y_train)
            
            y_train_pred_selected = model_selected.predict(X_selected_train_scaled)
            y_val_pred_selected = model_selected.predict(X_selected_val_scaled)
            y_test_pred_selected = model_selected.predict(X_selected_test_scaled)
            
            # 선택된 밴드 지표 계산
            metrics_selected = {}
            metrics_selected['train_mse'] = mean_squared_error(y_train, y_train_pred_selected)
            metrics_selected['train_mae'] = mean_absolute_error(y_train, y_train_pred_selected)
            metrics_selected['train_r2'] = r2_score(y_train, y_train_pred_selected)
            metrics_selected['val_mse'] = mean_squared_error(y_val, y_val_pred_selected)
            metrics_selected['val_mae'] = mean_absolute_error(y_val, y_val_pred_selected)
            metrics_selected['val_r2'] = r2_score(y_val, y_val_pred_selected)
            metrics_selected['test_mse'] = mean_squared_error(y_test, y_test_pred_selected)
            metrics_selected['test_mae'] = mean_absolute_error(y_test, y_test_pred_selected)
            metrics_selected['test_r2'] = r2_score(y_test, y_test_pred_selected)
            
            try:
                cv_scores_selected = cross_val_score(model_selected, X_selected_train_scaled, y_train, cv=5, scoring='r2')
                metrics_selected['cv_r2_mean'] = cv_scores_selected.mean()
                metrics_selected['cv_r2_std'] = cv_scores_selected.std()
            except:
                metrics_selected['cv_r2_mean'] = 0.0
                metrics_selected['cv_r2_std'] = 0.0
            
            # 결과 저장
            results[f"{model_name}_full"] = metrics_full
            results[f"{model_name}_selected"] = metrics_selected
            
            # MLflow에 지표 기록
            for metric_name, value in metrics_full.items():
                mlflow.log_metric(f"{label_name}_{model_name}_full_{metric_name}", value)
            for metric_name, value in metrics_selected.items():
                mlflow.log_metric(f"{label_name}_{model_name}_selected_{metric_name}", value)
            
            # 성능 비교 출력
            print(f"{model_name} Results:")
            print(f"  ALL bands ({X_full_train_scaled.shape[1]} features):")
            print(f"    Test - R2: {metrics_full['test_r2']:.4f}, MSE: {metrics_full['test_mse']:.4f}")
            print(f"  SELECTED bands ({X_selected_train_scaled.shape[1]} features):")
            print(f"    Test - R2: {metrics_selected['test_r2']:.4f}, MSE: {metrics_selected['test_mse']:.4f}")
            
            # 성능 차이 계산
            r2_diff = metrics_selected['test_r2'] - metrics_full['test_r2']
            mse_diff = metrics_selected['test_mse'] - metrics_full['test_mse']
            print(f"  Performance difference (selected - full):")
            print(f"    R2: {r2_diff:+.4f}, MSE: {mse_diff:+.4f}")
            
            # MLflow에 성능 차이 기록
            mlflow.log_metric(f"{label_name}_{model_name}_r2_diff", r2_diff)
            mlflow.log_metric(f"{label_name}_{model_name}_mse_diff", mse_diff)
    else:
        print(f"[Warning] Unknown label_type: {label_type}. No evaluation performed.")
    return results

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
                            mlflow_info: Dict, train_indices: np.ndarray, 
                            val_indices: np.ndarray, test_indices: np.ndarray,
                            scaler: StandardScaler, label_type: str, 
                            full_spectral_data: np.ndarray, full_labels: np.ndarray) -> Tuple[List[int], List[int], List[float], Dict]:
    """단일 라벨에 대한 밴드 선택을 수행하고 평가합니다."""
    print(f"\n--- Processing Label {label_idx+1}: {label_name} ---")
    
    # MLflow 중첩 실행
    with mlflow.start_run(run_name=f"label_{label_idx+1}_{label_name}", nested=True) as label_run:
        # 1. 전처리 모델 로딩 및 실행
        print(f"Step 1: Preprocessing for {label_name}")
        pre_config_with_mlflow = pre_config.copy()
        pre_config_with_mlflow['mlflow_info'] = mlflow_info.copy()
        pre_config_with_mlflow['mlflow_info']['current_label'] = label_name
        pre_config_with_mlflow['mlflow_info']['current_label_idx'] = label_idx
        
        pre_model = load_preprocessing_model(pre_config_with_mlflow, label_type)
        
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
        
        train_model = load_training_model(train_config_with_mlflow, label_type)
        
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
        
        # 3. 밴드 선택 결과 평가
        print(f"Step 3: Evaluating Band Selection for {label_name}")
        evaluation_results = evaluate_band_selection(
            spectral_data=full_spectral_data,  # 전체 데이터셋 사용
            labels=full_labels,  # 전체 라벨 데이터에서 해당 라벨만
            selected_bands=final_selected_bands,
            label_name=label_name,
            train_indices=train_indices,
            val_indices=val_indices,
            test_indices=test_indices,
            scaler=scaler,
            mlflow_info=mlflow_info,
            label_type=label_type
        )
        
        # 평가 결과를 MLflow에 기록
        mlflow.log_dict(evaluation_results, f"evaluation/{label_name}_evaluation_results.json")
        
        return pre_selected_bands, final_selected_bands, band_scores, evaluation_results

def main():
    # Config 파일 파싱
    config_argparser = argparse.ArgumentParser(description='HSI Multi-Label Vector Band Selection Pipeline')
    config_argparser.add_argument('--config', default="./configs/vector_pipeline_config.json", 
                                 type=str, help="Path to main config file")
    config_args, remaining_args = config_argparser.parse_known_args()
    
    # 메인 config 로드
    main_config = load_config(config_args.config)
    label_type = main_config.get('label_type', 'classification')
    
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
    
    # MLflow 호환성을 위한 래퍼 생성
    global_scaler_wrapper = StandardScalerWrapper(global_scaler)
    
    # train 데이터 정규화 (한 번만 수행)
    train_spectral_data_scaled = global_scaler.transform(train_spectral_data)
    
    print(f"StandardScaler fitted on train data: {train_spectral_data.shape}")
    print(f"Train data normalized: {train_spectral_data_scaled.shape}")
    print(f"Scaler mean shape: {global_scaler.mean_.shape}")
    print(f"Scaler scale shape: {global_scaler.scale_.shape}")
    
    # 라벨 정보 가져오기
    column_config = json.load(open("../training_HSI/configs/column_config.json", 'r'))
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
        mlflow.log_param("label_type", label_type)
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
        # 입력 예제 생성 (스펙트럼 데이터의 형태)
        input_example = np.random.randn(1, global_scaler.mean_.shape[0])
        
        mlflow.sklearn.log_model(
            global_scaler_wrapper, 
            name="scaler",
            input_example=input_example,
            registered_model_name=f"standard_scaler_{experiment}"
        )
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
            pre_selected_bands, final_selected_bands, band_scores, evaluation_results = run_single_label_training(
                label_idx, label_name, train_spectral_data_scaled, train_single_label,
                pre_config, train_config, params, evaluator, mlflow_info,
                train_dataset.indices, val_dataset.indices, test_dataset.indices, global_scaler, label_type,
                dataset.spectral_data, dataset.labels[:, label_idx]
            )
            
            # 결과 저장 (밴드 인덱스를 int로 변환)
            label_result = {
                'label_name': label_name,
                'label_index': label_idx,
                'pre_selected_bands': [int(band) for band in pre_selected_bands],
                'final_selected_bands': [int(band) for band in final_selected_bands],
                'band_scores': band_scores,
                'evaluation_results': evaluation_results,
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
        
        # 평가 결과 요약 통계
        evaluation_summary = {}
        if label_type == 'classification':
            base_model_names = ['RandomForest', 'SVM']
            metrics = ['test_accuracy', 'test_f1', 'test_auc']
        else:  # regression
            base_model_names = ['RandomForestRegressor', 'Ridge']
            metrics = ['test_r2', 'test_mse', 'test_mae']
        
        for base_model_name in base_model_names:
            # 전체 밴드와 선택된 밴드 각각에 대해 통계 계산
            for band_type in ['full', 'selected']:
                model_name = f"{base_model_name}_{band_type}"
                model_metrics = {}
                
                for metric in metrics:
                    values = []
                    for label_name, result in all_results['label_results'].items():
                        if 'evaluation_results' in result and model_name in result['evaluation_results']:
                            values.append(result['evaluation_results'][model_name].get(metric, 0.0))
                    
                    if values:
                        model_metrics[f'{metric}_mean'] = float(np.mean(values))
                        model_metrics[f'{metric}_std'] = float(np.std(values))
                        model_metrics[f'{metric}_min'] = float(np.min(values))
                        model_metrics[f'{metric}_max'] = float(np.max(values))
                
                evaluation_summary[model_name] = model_metrics
            
            # 성능 차이 통계 계산
            diff_metrics = {}
            if label_type == 'classification':
                accuracy_diffs = []
                f1_diffs = []

                for label_name, result in all_results['label_results'].items():
                    eval_res = result.get('evaluation_results', {})
                    accuracy_diff_key = f"{base_model_name}_accuracy_diff"
                    f1_diff_key = f"{base_model_name}_f1_diff"

                    if accuracy_diff_key in eval_res:
                        accuracy_diffs.append(eval_res[accuracy_diff_key])
                    if f1_diff_key in eval_res:
                        f1_diffs.append(eval_res[f1_diff_key])

                if accuracy_diffs:
                    diff_metrics['accuracy_diff_mean'] = float(np.mean(accuracy_diffs))
                    diff_metrics['accuracy_diff_std'] = float(np.std(accuracy_diffs))
                if f1_diffs:
                    diff_metrics['f1_diff_mean'] = float(np.mean(f1_diffs))
                    diff_metrics['f1_diff_std'] = float(np.std(f1_diffs))
            else:  # regression
                diff_metrics['r2_diff_mean'] = 0.0
                diff_metrics['mse_diff_mean'] = 0.0
            
            # 각 라벨에서의 성능 차이 평균 계산
            diff_values = []
            for label_name, result in all_results['label_results'].items():
                if 'evaluation_results' in result:
                    if label_type == 'classification':
                        if f"{base_model_name}_accuracy_diff" in result['evaluation_results']:
                            diff_values.append(result['evaluation_results'][f"{base_model_name}_accuracy_diff"])
                    else:  # regression
                        if f"{base_model_name}_r2_diff" in result['evaluation_results']:
                            diff_values.append(result['evaluation_results'][f"{base_model_name}_r2_diff"])
            
            if diff_values:
                if label_type == 'classification':
                    diff_metrics['accuracy_diff_mean'] = float(np.mean(diff_values))
                    diff_metrics['accuracy_diff_std'] = float(np.std(diff_values))
                else:  # regression
                    diff_metrics['r2_diff_mean'] = float(np.mean(diff_values))
                    diff_metrics['r2_diff_std'] = float(np.std(diff_values))
            
            evaluation_summary[f"{base_model_name}_diff"] = diff_metrics
        
        # 요약 통계 (NumPy 타입을 Python 기본 타입으로 변환)
        summary_stats = {
            'unique_pre_bands': len(all_pre_bands),
            'unique_final_bands': len(all_final_bands),
            'most_used_bands': [(int(k), int(v)) for k, v in sorted(band_usage_count.items(), key=lambda x: x[1], reverse=True)],
            'band_usage_distribution': {int(k): int(v) for k, v in band_usage_count.items()},
            'average_bands_per_label': float(len(all_final_bands) / num_labels),
            'evaluation_summary': evaluation_summary
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
        
        # 평가 결과 요약 출력
        print(f"\nEvaluation Summary:")
        for base_model_name in base_model_names:
            print(f"\n{base_model_name}:")
            
            # 전체 밴드 성능
            full_model_name = f"{base_model_name}_full"
            if full_model_name in evaluation_summary:
                print(f"  ALL bands performance:")
                for metric_name, value in evaluation_summary[full_model_name].items():
                    if 'mean' in metric_name:
                        print(f"    {metric_name}: {value:.4f}")
            
            # 선택된 밴드 성능
            selected_model_name = f"{base_model_name}_selected"
            if selected_model_name in evaluation_summary:
                print(f"  SELECTED bands performance:")
                for metric_name, value in evaluation_summary[selected_model_name].items():
                    if 'mean' in metric_name:
                        print(f"    {metric_name}: {value:.4f}")
            
            # 성능 차이
            diff_model_name = f"{base_model_name}_diff"
            if diff_model_name in evaluation_summary:
                print(f"  Performance difference (selected - full):")
                for metric_name, value in evaluation_summary[diff_model_name].items():
                    if 'mean' in metric_name:
                        print(f"    {metric_name}: {value:+.4f}")
        
        # MLflow에 전체 결과 기록 (NumPy 타입 변환 후)
        all_results_converted = convert_numpy_types(all_results)
        summary_stats_converted = convert_numpy_types(summary_stats)
        
        mlflow.log_dict(all_results_converted, 'results/multilabel_results.json')
        mlflow.log_dict(summary_stats_converted, 'results/summary_statistics.json')
        
        # 주요 평가 지표를 MLflow에 기록
        for model_name, metrics in evaluation_summary.items():
            for metric_name, value in metrics.items():
                mlflow.log_metric(f"summary_{model_name}_{metric_name}", value)
        
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