import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Any, Tuple, List
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
import time
from tqdm import tqdm
from torchmetrics.classification import MultilabelF1Score, MultilabelPrecision, MultilabelRecall, MultilabelAUROC, MulticlassF1Score, MulticlassPrecision, MulticlassRecall, MulticlassAUROC
from torchmetrics.regression import MeanSquaredError, MeanAbsoluteError, R2Score
from sklearn.metrics import roc_auc_score
import tempfile
import os
import torch


class MultiTaskLossWrapper(nn.Module):
    """멀티태스크 손실을 위한 래퍼 클래스"""
    
    def __init__(self, task_num: int, loss_fn: str = 'uncertainty'):
        """
        Args:
            task_num: 태스크 수
            loss_fn: 손실 함수 타입 ('uncertainty', 'equal', 'dynamic')
        """
        super(MultiTaskLossWrapper, self).__init__()
        self.task_num = task_num
        self.loss_fn = loss_fn
        
        if loss_fn == 'uncertainty':
            self.log_vars = nn.Parameter(torch.zeros(task_num))
        elif loss_fn == 'equal':
            self.register_parameter('log_vars', None)
        elif loss_fn == 'dynamic':
            self.log_vars = nn.Parameter(torch.zeros(task_num))
        else:
            raise ValueError(f"Unknown loss function type: {loss_fn}")
    
    def forward(self, losses: List[torch.Tensor]) -> torch.Tensor:
        """
        Args:
            losses: 각 태스크의 손실 리스트
        
        Returns:
            가중 평균 손실
        """
        if self.loss_fn == 'uncertainty':
            # 불확실성 기반 가중치
            precision = torch.exp(-self.log_vars)
            losses = torch.stack(losses)  # (task_num,)
            loss = torch.sum(precision * losses + self.log_vars)
        elif self.loss_fn == 'equal':
            # 동일 가중치
            losses = torch.stack(losses)  # (task_num,)
            loss = torch.mean(losses)
        elif self.loss_fn == 'dynamic':
            # 동적 가중치 (학습 가능)
            weights = torch.softmax(self.log_vars, dim=0)
            losses = torch.stack(losses)  # (task_num,)
            loss = torch.sum(weights * losses)
        
        return loss
    
    def get_weights(self) -> torch.Tensor:
        """현재 가중치를 반환합니다."""
        if self.loss_fn == 'uncertainty':
            return torch.exp(-self.log_vars)
        elif self.loss_fn == 'equal':
            # log_vars가 없으므로 device를 안전하게 추출
            device = next(self.parameters()).device
            return torch.ones(self.task_num, device=device) / self.task_num
        elif self.loss_fn == 'dynamic':
            return torch.softmax(self.log_vars, dim=0)


class HSITrainer:
    """HSI 모델 훈련을 위한 클래스"""
    
    def __init__(self, model: nn.Module, device: torch.device, config: Dict[str, Any], pos_weight_info: Dict[str, Any] = None):
        """
        Args:
            model: 훈련할 모델
            device: 사용할 디바이스
            config: 설정 딕셔너리
            pos_weight_info: pos_weight 계산을 위한 라벨 통계 정보
        """
        self.model = model
        self.device = device
        self.config = config
        self.pos_weight_info = pos_weight_info
        
        # AMP 및 Gradient Clipping 설정
        self.use_amp = config.get('train', {}).get('use_amp', False)
        self.grad_clip_norm = config.get('train', {}).get('grad_clip_norm', None)
        
        if self.use_amp and torch.cuda.is_available():
            self.scaler = torch.cuda.amp.GradScaler()
            print("AMP (Automatic Mixed Precision) enabled")
        else:
            self.scaler = None
        
        # 라벨 정보 설정
        self._setup_label_info()
        
        # 손실 래퍼 설정 (optimizer보다 먼저 생성)
        self.loss_wrapper = self._setup_loss_wrapper().to(self.device)
        
        # 옵티마이저 설정
        self.optimizer = self._setup_optimizer()
        
        # 스케줄러 설정
        self.scheduler = self._setup_scheduler()
        
        # 손실 함수 설정 (pos_weight_info 사용)
        self.criterions = self._setup_criterions()
        
        # 메트릭 설정
        self._setup_metrics()
        
        # 훈련 상태 초기화
        self.best_val_loss = float('inf')
        self.best_val_metrics = {}
        self.patience_counter = 0
        self.early_stopping_patience = config.get('train', {}).get('early_stopping_patience', 10)
        self.save_interval = config.get('train', {}).get('save_interval', 5)

    def _setup_optimizer(self) -> optim.Optimizer:
        """옵티마이저를 설정합니다."""
        train_config = self.config.get('train', {})
        optimizer_name = train_config.get('optimizer', 'AdamW')
        lr = train_config.get('lr', 3e-4)
        weight_decay = train_config.get('weight_decay', 1e-4)
        
        # model + loss_wrapper 파라미터를 모두 포함
        params = list(self.model.parameters())
        if hasattr(self.loss_wrapper, 'parameters') and any(p.requires_grad for p in self.loss_wrapper.parameters()):
            params += list(self.loss_wrapper.parameters())
        
        if optimizer_name.lower() == 'adamw':
            return optim.AdamW(params, lr=lr, weight_decay=weight_decay)
        elif optimizer_name.lower() == 'adam':
            return optim.Adam(params, lr=lr, weight_decay=weight_decay)
        elif optimizer_name.lower() == 'sgd':
            return optim.SGD(params, lr=lr, weight_decay=weight_decay)
        else:
            raise ValueError(f"Unknown optimizer: {optimizer_name}")
    
    def _setup_scheduler(self):
        """스케줄러를 설정합니다."""
        train_config = self.config.get('train', {})
        scheduler_name = train_config.get('scheduler', 'ReduceLROnPlateau')
        
        if scheduler_name == 'ReduceLROnPlateau':
            patience = train_config.get('scheduler_patience', 5)
            factor = train_config.get('scheduler_factor', 0.5)
            return optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer, mode='min', patience=patience, factor=factor
            )
        elif scheduler_name == 'CosineAnnealingLR':
            T_max = train_config.get('scheduler_t_max', 50)
            return optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=T_max)
        else:
            return None
    
    def _setup_label_info(self):
        """라벨 타입 정보를 설정합니다."""
        # 회귀 전용 모델 - 모든 5개 출력이 회귀
        self.cls_indices = []  # 분류 없음
        self.reg_indices = [0, 1, 2, 3, 4]  # 모든 5개 출력이 회귀 (Total, Marbling, Meat Color, Texture, Moisture)

        print(f"Label setup (regression-only model):")
        print(f"  Classification indices: {self.cls_indices}")
        print(f"  Regression indices: {self.reg_indices}")
    
    def _setup_criterions(self) -> Dict[str, nn.Module]:
        """손실 함수들을 설정합니다."""
        criterions = {}
        # 회귀 전용 모델
        if self.reg_indices:
            criterions['regression'] = nn.MSELoss().to(self.device)
            print("MSELoss for regression tasks")
        return criterions
    
    def _setup_loss_wrapper(self) -> MultiTaskLossWrapper:
        """MultiTaskLossWrapper를 설정합니다."""
        train_config = self.config.get('train', {})
        loss_fn = train_config.get('loss_fn', 'equal')  # 회귀 전용이므로 equal 사용

        # 회귀 전용 - 1개 태스크
        task_num = 1

        return MultiTaskLossWrapper(task_num=task_num, loss_fn=loss_fn)
    
    def _update_metrics(self, outputs: torch.Tensor, targets: torch.Tensor):
        """
        배치별 메트릭을 업데이트합니다. (회귀 전용)
        """
        # 회귀 메트릭 업데이트 - 모든 5개 출력
        reg_outputs = outputs  # (B, 5) - Total, Marbling, Meat Color, Texture, Moisture
        reg_targets = targets[:, self.reg_indices]  # (B, 5)

        # 전체 평균 메트릭 업데이트
        self.metrics['reg_mse'].update(reg_outputs.flatten(), reg_targets.flatten())
        self.metrics['reg_mae'].update(reg_outputs.flatten(), reg_targets.flatten())
        self.metrics['reg_r2'].update(reg_outputs.flatten(), reg_targets.flatten())

        # AUC 계산을 위한 데이터 저장 (배치별)
        if not hasattr(self, '_auc_outputs'):
            self._auc_outputs = []
            self._auc_targets = []

        self._auc_outputs.append(reg_outputs.detach().cpu().numpy())
        self._auc_targets.append(reg_targets.detach().cpu().numpy())
    
    def _compute_metrics(self) -> Dict[str, float]:
        """누적된 메트릭을 계산합니다."""
        metrics = {}

        # 회귀 메트릭 계산
        try:
            mse = self.metrics['reg_mse'].compute().item()
            mae = self.metrics['reg_mae'].compute().item()
            r2 = self.metrics['reg_r2'].compute().item()

            metrics.update({
                'mse': mse,
                'mae': mae,
                'r2': r2
            })
        except ValueError as e:
            # 샘플이 부족하거나 계산 불가능한 경우 기본값 사용
            metrics.update({
                'mse': 999.0,
                'mae': 999.0,
                'r2': -999.0
            })

        # AUC 계산 (회귀에서 연속값을 이용한 ROC-AUC)
        try:
            if hasattr(self, '_auc_outputs') and self._auc_outputs:
                all_outputs = np.concatenate(self._auc_outputs, axis=0)  # (N, 5)
                all_targets = np.concatenate(self._auc_targets, axis=0)  # (N, 5)

                # Total score (첫 번째 출력)에 대한 AUC 계산
                # 연속값을 이진 분류 문제로 변환 (중간값 기준)
                total_outputs = all_outputs[:, 0]  # Total 예측값
                total_targets = all_targets[:, 0]   # Total 실제값

                # 중간값을 기준으로 이진화
                median_target = np.median(total_targets)
                binary_targets = (total_targets >= median_target).astype(int)

                if len(np.unique(binary_targets)) > 1:  # 두 클래스 모두 존재할 때만
                    auc = roc_auc_score(binary_targets, total_outputs)
                    metrics['auc'] = auc
                else:
                    metrics['auc'] = 0.5  # 기본값
            else:
                metrics['auc'] = 0.5
        except Exception as e:
            print(f"AUC calculation failed: {e}")
            metrics['auc'] = 0.5

        # Combined score = R2 점수 (R2가 높을수록 좋음)
        metrics['combined_score'] = max(0, metrics.get('r2', 0))

        return metrics
    
    def _setup_metrics(self):
        """TorchMetrics를 설정합니다."""
        self.metrics = {}

        # 회귀 메트릭 설정 (회귀 전용 모델)
        self.metrics['reg_mse'] = MeanSquaredError().to(self.device)
        self.metrics['reg_mae'] = MeanAbsoluteError().to(self.device)
        self.metrics['reg_r2'] = R2Score().to(self.device)
    
    def _calculate_loss(self, outputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """회귀 손실을 계산합니다."""
        losses = []
        loss_components = {}

        # 회귀 손실 계산 (모든 5개 출력)
        reg_outputs = outputs  # (B, 5)
        reg_targets = targets[:, self.reg_indices]  # (B, 5)
        reg_loss = self.criterions['regression'](reg_outputs, reg_targets)
        losses.append(reg_loss)
        loss_components['regression_loss'] = reg_loss.item()

        # MultiTaskLossWrapper로 손실 결합 (단일 태스크)
        total_loss = self.loss_wrapper(losses)

        return total_loss, loss_components
    
    def _calculate_metrics(self, outputs: torch.Tensor, targets: torch.Tensor) -> Dict[str, float]:
        """평가 지표를 계산합니다 (기존 방식 - evaluate에서 사용)."""
        # 메트릭 리셋
        for metric in self.metrics.values():
            metric.reset()
        
        # 배치별 메트릭 업데이트
        self._update_metrics(outputs, targets)
        
        # 메트릭 계산
        return self._compute_metrics()
    
    def _train_epoch(self, train_loader: DataLoader) -> Tuple[float, Dict[str, float]]:
        """한 에포크를 훈련합니다 (메모리 효율적)."""
        self.model.train()
        total_loss = 0.0
        processed = 0  # 실제 처리된 배치 수 추적

        # 메트릭 리셋
        for metric in self.metrics.values():
            if metric is not None:
                metric.reset()

        # AUC 계산용 데이터 리셋
        self._auc_outputs = []
        self._auc_targets = []
        
        pbar = tqdm(train_loader, desc="Training")
        for batch_idx, batch in enumerate(pbar):
            if batch is None or len(batch) == 0 or batch[0].numel() == 0:
                continue
            images, targets, _, sample_indices = batch
            images = images.to(self.device)
            targets = targets.to(self.device)
            
            self.optimizer.zero_grad()
            
            # AMP 적용
            if self.use_amp:
                with torch.cuda.amp.autocast():
                    outputs = self.model(images)
                    loss, loss_components = self._calculate_loss(outputs, targets)
                
                # GradScaler를 사용한 backward 및 step
                self.scaler.scale(loss).backward()
                
                # Gradient clipping
                if self.grad_clip_norm is not None:
                    self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_norm)
                
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(images)
                loss, loss_components = self._calculate_loss(outputs, targets)
                
                loss.backward()
                
                # Gradient clipping
                if self.grad_clip_norm is not None:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_norm)
                
                self.optimizer.step()
            
            total_loss += loss.item()
            processed += 1  # 유효한 배치 처리 완료 시 카운트
            
            # 배치별 메트릭 업데이트 (메모리 효율적)
            self._update_metrics(outputs, targets)
            
            # 진행률 업데이트
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        # 실제 처리된 배치의 평균 손실 계산
        avg_loss = total_loss / max(1, processed)
        
        # 메트릭 계산
        metrics = self._compute_metrics()
        
        return avg_loss, metrics
    
    def _validate_epoch(self, val_loader: DataLoader) -> Tuple[float, Dict[str, float]]:
        """한 에포크를 검증합니다 (메모리 효율적)."""
        self.model.eval()
        total_loss = 0.0
        processed = 0  # 실제 처리된 배치 수 추적

        # 메트릭 리셋
        for metric in self.metrics.values():
            if metric is not None:
                metric.reset()

        # AUC 계산용 데이터 리셋
        self._auc_outputs = []
        self._auc_targets = []
        
        with torch.no_grad():
            pbar = tqdm(val_loader, desc="Validation")
            for batch_idx, batch in enumerate(pbar):
                if batch is None or len(batch) == 0 or batch[0].numel() == 0:
                    continue
                images, targets, _, sample_indices = batch
                images = images.to(self.device)
                targets = targets.to(self.device)
                
                # AMP 적용 (검증 시에도 일관성 유지)
                if self.use_amp:
                    with torch.cuda.amp.autocast():
                        outputs = self.model(images)
                        loss, loss_components = self._calculate_loss(outputs, targets)
                else:
                    outputs = self.model(images)
                    loss, loss_components = self._calculate_loss(outputs, targets)
                
                total_loss += loss.item()
                processed += 1  # 유효한 배치 처리 완료 시 카운트
                
                # 배치별 메트릭 업데이트 (메모리 효율적)
                self._update_metrics(outputs, targets)
                
                # 진행률 업데이트
                pbar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        # 실제 처리된 배치의 평균 손실 계산
        avg_loss = total_loss / max(1, processed)
        
        # 메트릭 계산
        metrics = self._compute_metrics()
        
        return avg_loss, metrics
    
    def set_train_loader(self, train_loader):
        """train_loader를 외부에서 세팅하고 pos_weight를 재계산한다."""
        # pos_weight_info를 미리 받았으므로 이 메서드는 더 이상 필요하지 않음
        # 하위 호환성을 위해 남겨둠
        pass
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
              num_epochs: int, logger=None) -> Dict[str, List[float]]:
        """전체 훈련을 수행합니다."""
        print(f"Starting training for {num_epochs} epochs...")
        
        # 훈련 기록
        train_losses = []
        val_losses = []
        train_metrics = {}
        val_metrics = {}
        
        start_time = time.time()
        
        for epoch in range(num_epochs):
            print(f"\nEpoch {epoch+1}/{num_epochs}")
            print("-" * 50)
            
            # 훈련
            train_loss, train_epoch_metrics = self._train_epoch(train_loader)
            
            # 검증
            val_loss, val_epoch_metrics = self._validate_epoch(val_loader)
            
            # 스케줄러 업데이트
            if self.scheduler is not None:
                if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_loss)
                else:
                    self.scheduler.step()
            
            # 기록 저장
            train_losses.append(train_loss)
            val_losses.append(val_loss)
            
            # 동적 삽입 방식으로 메트릭 저장
            for key, val in train_epoch_metrics.items():
                train_metrics.setdefault(key, []).append(val)
            for key, val in val_epoch_metrics.items():
                val_metrics.setdefault(key, []).append(val)
            
            # 결과 출력
            print(f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
            print(f"Train R2: {train_epoch_metrics.get('r2', 0):.4f}, Val R2: {val_epoch_metrics.get('r2', 0):.4f}")
            print(f"Train MSE: {train_epoch_metrics.get('mse', 0):.4f}, Val MSE: {val_epoch_metrics.get('mse', 0):.4f}")
            print(f"Train MAE: {train_epoch_metrics.get('mae', 0):.4f}, Val MAE: {val_epoch_metrics.get('mae', 0):.4f}")
            print(f"Train AUC: {train_epoch_metrics.get('auc', 0):.4f}, Val AUC: {val_epoch_metrics.get('auc', 0):.4f}")
            print(f"Combined Score: {train_epoch_metrics.get('combined_score', 0):.4f}")
            
            # MLflow 로깅
            if logger is not None:
                epoch_metrics = {
                    'train_loss': train_loss,
                    'val_loss': val_loss,
                    **{f'train_{k}': v for k, v in train_epoch_metrics.items()},
                    **{f'val_{k}': v for k, v in val_epoch_metrics.items()}
                }
                logger.log_metrics(epoch_metrics, step=epoch)
            
            # 체크포인트 저장 조건 확인
            should_checkpoint = val_loss < self.best_val_loss
            
            if should_checkpoint:
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    self.best_val_metrics = val_epoch_metrics
                    self.patience_counter = 0
                
                # 모델 저장
                if logger is not None:
                    with tempfile.TemporaryDirectory() as d:
                        save_path = os.path.join(d, "best_model.pt")
                        torch.save(self.model.state_dict(), save_path)
                        logger.log_artifact(save_path, "models")
                    print(f"[Checkpoint] Best model saved (epoch {epoch+1})", flush=True)
            else:
                if val_loss >= self.best_val_loss:
                    self.patience_counter += 1
            
            # Early stopping 체크
            if self.patience_counter >= self.early_stopping_patience:
                print(f"Early stopping triggered after {epoch+1} epochs")
                break
        
        training_time = time.time() - start_time
        
        print(f"\nTraining completed in {training_time/60:.2f} minutes")
        print(f"Best validation loss: {self.best_val_loss:.4f}")
        print(f"Best validation R2: {self.best_val_metrics.get('r2', 0):.4f}")
        print(f"Best validation MSE: {self.best_val_metrics.get('mse', 0):.4f}")
        print(f"Best validation MAE: {self.best_val_metrics.get('mae', 0):.4f}")
        print(f"Best validation AUC: {self.best_val_metrics.get('auc', 0):.4f}")
        print(f"Best combined score: {self.best_val_metrics.get('combined_score', 0):.4f}")
        
        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
            'train_metrics': train_metrics,
            'val_metrics': val_metrics,
            'best_val_metrics': self.best_val_metrics,
            'training_time': training_time
        }
    
    def evaluate(self, test_loader: DataLoader) -> Dict[str, float]:
        """테스트 데이터로 평가합니다."""
        print("Evaluating on test set...")
        
        test_loss, test_metrics = self._validate_epoch(test_loader)
        
        print(f"Test Loss: {test_loss:.4f}")
        print(f"Test R2: {test_metrics.get('r2', 0):.4f}")
        print(f"Test MSE: {test_metrics.get('mse', 0):.4f}")
        print(f"Test MAE: {test_metrics.get('mae', 0):.4f}")
        print(f"Test AUC: {test_metrics.get('auc', 0):.4f}")
        print(f"Test combined score: {test_metrics.get('combined_score', 0):.4f}")
        
        return test_metrics 