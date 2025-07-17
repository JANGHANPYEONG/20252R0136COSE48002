import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import mlflow
import mlflow.pytorch
from typing import Dict, Any, Tuple
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.dataset import load_image_data, split_image_data
from utils.model_loader import load_training_model, validate_model_config, save_model_to_mlflow
from utils.column_info import load_column_config

class HSIImageTrainer:
    """HSI 이미지 훈련을 위한 클래스"""
    
    def __init__(self, config_path: str):
        """
        Args:
            config_path: 설정 파일 경로
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print(f"Using device: {self.device}")
        print(f"Config loaded from: {config_path}")
        
        # MLflow 설정
        mlflow.set_tracking_uri(self.config['mlflow']['tracking_uri'])
        mlflow.set_experiment(self.config['experiment'])
        
    def _load_config(self) -> Dict:
        """설정 파일을 로드합니다."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        # 훈련 설정 파일 로드
        training_config_path = config['training']['config_path']
        if not os.path.exists(training_config_path):
            raise FileNotFoundError(f"Training config file not found: {training_config_path}")
        
        with open(training_config_path, 'r') as f:
            training_config = json.load(f)
        
        # 컬럼 설정 로드
        column_config = load_column_config()
        
        # 설정 병합
        merged_config = {
            **config,
            **training_config,
            **column_config
        }
        
        return merged_config
    
    def _setup_data_loaders(self) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """데이터 로더를 설정합니다."""
        data_config = self.config.get('data', {})
        data_split_config = self.config.get('data_split', {})
        csv_path = data_config.get('csv_path', '../datasets_HSI/label.csv')
        
        # 이미지 데이터셋 로드
        print("Loading image dataset...")
        dataset = load_image_data(csv_path, self.config)
        
        # 데이터셋 분할
        train_ratio = data_split_config.get('train_ratio', 0.8)
        val_ratio = data_split_config.get('val_ratio', 0.1)
        test_ratio = data_split_config.get('test_ratio', 0.1)
        random_state = self.config.get('hyperparameters', {}).get('seed', 42)
        
        train_dataset, val_dataset, test_dataset = split_image_data(
            dataset, train_ratio, val_ratio, test_ratio, random_state
        )
        
        # 데이터 로더 설정
        batch_size = self.config['training']['parameters'].get('batch_size', 16)
        num_workers = data_config.get('num_workers', 4)
        pin_memory = data_config.get('pin_memory', True)
        
        train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True,
            num_workers=num_workers, pin_memory=pin_memory
        )
        
        val_loader = DataLoader(
            val_dataset, batch_size=batch_size, shuffle=False,
            num_workers=num_workers, pin_memory=pin_memory
        )
        
        test_loader = DataLoader(
            test_dataset, batch_size=batch_size, shuffle=False,
            num_workers=num_workers, pin_memory=pin_memory
        )
        
        return train_loader, val_loader, test_loader
    
    def _setup_model(self) -> nn.Module:
        """모델을 설정합니다."""
        # 모델 설정 검증
        if not validate_model_config(self.config, 'training'):
            raise ValueError("Invalid training model configuration")
        
        # 모델 로드
        model = load_training_model(self.config)
        model = model.to(self.device)
        
        return model
    
    def _setup_optimizer_and_scheduler(self, model: nn.Module) -> Tuple[optim.Optimizer, Any]:
        """옵티마이저와 스케줄러를 설정합니다."""
        params = self.config['training']['parameters']
        learning_rate = params.get('learning_rate', 0.001)
        weight_decay = params.get('weight_decay', 0.0001)
        optimizer_name = params.get('optimizer', 'adam')
        scheduler_name = params.get('scheduler', 'reduce_lr_on_plateau')
        
        # 옵티마이저 설정
        if optimizer_name.lower() == 'adam':
            optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        elif optimizer_name.lower() == 'sgd':
            optimizer = optim.SGD(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        else:
            raise ValueError(f"Unknown optimizer: {optimizer_name}")
        
        # 스케줄러 설정
        scheduler = None
        if scheduler_name == 'reduce_lr_on_plateau':
            scheduler_patience = params.get('scheduler_patience', 5)
            scheduler_factor = params.get('scheduler_factor', 0.5)
            scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, mode='min', patience=scheduler_patience, factor=scheduler_factor
            )
        
        return optimizer, scheduler
    
    def _calculate_loss(self, outputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """손실을 계산합니다."""
        # 멀티라벨 분류를 위한 BCE 손실
        criterion = nn.BCELoss()
        return criterion(outputs, targets)
    
    def _calculate_metrics(self, outputs: torch.Tensor, targets: torch.Tensor) -> Dict[str, float]:
        """평가 지표를 계산합니다."""
        # 확률을 이진 예측으로 변환
        predictions = (outputs > 0.5).float()
        
        # 정확도
        accuracy = accuracy_score(targets.cpu().numpy().flatten(), 
                                predictions.cpu().numpy().flatten())
        
        # 각 클래스별 정밀도, 재현율, F1-score
        precision, recall, f1, _ = precision_recall_fscore_support(
            targets.cpu().numpy(), predictions.cpu().numpy(), 
            average='macro', zero_division=0
        )
        
        # AUC (각 클래스별 평균)
        try:
            auc = roc_auc_score(targets.cpu().numpy(), outputs.cpu().numpy(), 
                               average='macro', multi_class='ovr')
        except:
            auc = 0.0
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc': auc
        }
    
    def _train_epoch(self, model: nn.Module, train_loader: DataLoader, 
                    optimizer: optim.Optimizer, criterion: nn.Module) -> Dict[str, float]:
        """한 에포크를 훈련합니다."""
        model.train()
        total_loss = 0.0
        all_outputs = []
        all_targets = []
        
        for batch_idx, (images, targets, _) in enumerate(train_loader):
            images = images.to(self.device)
            targets = targets.to(self.device)
            
            optimizer.zero_grad()
            
            outputs = model(images)
            loss = criterion(outputs, targets)
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            all_outputs.append(outputs.detach())
            all_targets.append(targets.detach())
            
            if batch_idx % 10 == 0:
                print(f"Batch {batch_idx}/{len(train_loader)}, Loss: {loss.item():.4f}")
        
        # 전체 배치의 평균 손실과 지표 계산
        avg_loss = total_loss / len(train_loader)
        all_outputs = torch.cat(all_outputs, dim=0)
        all_targets = torch.cat(all_targets, dim=0)
        metrics = self._calculate_metrics(all_outputs, all_targets)
        
        return {'loss': avg_loss, **metrics}
    
    def _validate_epoch(self, model: nn.Module, val_loader: DataLoader, 
                       criterion: nn.Module) -> Dict[str, float]:
        """검증 에포크를 실행합니다."""
        model.eval()
        total_loss = 0.0
        all_outputs = []
        all_targets = []
        
        with torch.no_grad():
            for images, targets, _ in val_loader:
                images = images.to(self.device)
                targets = targets.to(self.device)
                
                outputs = model(images)
                loss = criterion(outputs, targets)
                
                total_loss += loss.item()
                all_outputs.append(outputs)
                all_targets.append(targets)
        
        # 전체 배치의 평균 손실과 지표 계산
        avg_loss = total_loss / len(val_loader)
        all_outputs = torch.cat(all_outputs, dim=0)
        all_targets = torch.cat(all_targets, dim=0)
        metrics = self._calculate_metrics(all_outputs, all_targets)
        
        return {'loss': avg_loss, **metrics}
    
    def train(self):
        """전체 훈련 과정을 실행합니다."""
        print("Starting HSI Image Training...")
        
        # 데이터 로더 설정
        train_loader, val_loader, test_loader = self._setup_data_loaders()
        
        # 모델 설정
        model = self._setup_model()
        
        # 옵티마이저와 스케줄러 설정
        optimizer, scheduler = self._setup_optimizer_and_scheduler(model)
        
        # 손실 함수
        criterion = nn.BCELoss()
        
        # 훈련 파라미터
        epochs = self.config['training']['parameters'].get('epochs', 100)
        early_stopping_patience = self.config['training']['parameters'].get('early_stopping_patience', 10)
        
        # 조기 종료를 위한 변수들
        best_val_loss = float('inf')
        patience_counter = 0
        
        # MLflow 실행 시작
        with mlflow.start_run(run_name=self.config['run']):
            # 설정 로깅
            mlflow.log_params({
                "model_name": self.config['training']['model_name'],
                "learning_rate": self.config['training']['parameters']['learning_rate'],
                "batch_size": self.config['training']['parameters']['batch_size'],
                "epochs": epochs,
                "num_bands": len(self.config.get('wavelengths', [])),
                "num_classes": len(self.config.get('label_columns', [])),
                "image_size": self.config.get('image_size', [256, 256])
            })
            
            print(f"Training for {epochs} epochs...")
            
            for epoch in range(epochs):
                print(f"\nEpoch {epoch+1}/{epochs}")
                print("-" * 50)
                
                # 훈련
                train_metrics = self._train_epoch(model, train_loader, optimizer, criterion)
                
                # 검증
                val_metrics = self._validate_epoch(model, val_loader, criterion)
                
                # 스케줄러 업데이트
                if scheduler is not None:
                    scheduler.step(val_metrics['loss'])
                
                # 결과 출력
                print(f"Train - Loss: {train_metrics['loss']:.4f}, "
                      f"Accuracy: {train_metrics['accuracy']:.4f}, "
                      f"F1: {train_metrics['f1_score']:.4f}")
                print(f"Val   - Loss: {val_metrics['loss']:.4f}, "
                      f"Accuracy: {val_metrics['accuracy']:.4f}, "
                      f"F1: {val_metrics['f1_score']:.4f}")
                
                # MLflow에 지표 로깅
                for metric_name, value in train_metrics.items():
                    mlflow.log_metric(f"train_{metric_name}", value, step=epoch)
                
                for metric_name, value in val_metrics.items():
                    mlflow.log_metric(f"val_{metric_name}", value, step=epoch)
                
                # 조기 종료 체크
                if val_metrics['loss'] < best_val_loss:
                    best_val_loss = val_metrics['loss']
                    patience_counter = 0
                    
                    # 최고 모델 저장
                    save_model_to_mlflow(model, self.config['training']['model_name'], 
                                       self.config, 'training')
                    print("New best model saved!")
                else:
                    patience_counter += 1
                    if patience_counter >= early_stopping_patience:
                        print(f"Early stopping triggered after {epoch+1} epochs")
                        break
            
            # 테스트 평가
            print("\nEvaluating on test set...")
            test_metrics = self._validate_epoch(model, test_loader, criterion)
            
            print(f"Test Results:")
            for metric_name, value in test_metrics.items():
                print(f"  {metric_name}: {value:.4f}")
                mlflow.log_metric(f"test_{metric_name}", value)
        
        print("Training completed!")

def main():
    """메인 함수"""
    if len(sys.argv) != 2:
        print("Usage: python train_multilabel_HSI_image.py <config_path>")
        print("Example: python train_multilabel_HSI_image.py configs/image_pipeline_config.json")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    try:
        trainer = HSIImageTrainer(config_path)
        trainer.train()
    except Exception as e:
        print(f"Error during training: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
