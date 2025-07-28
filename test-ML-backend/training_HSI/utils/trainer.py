import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Any, Tuple, List
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
import time
from tqdm import tqdm
from torchmetrics.classification import MultilabelF1Score, MultilabelPrecision, MultilabelRecall, MultilabelAUROC
from torchmetrics.regression import MeanSquaredError, MeanAbsoluteError, R2Score
import tempfile
import os
import torch
import torch.nn.functional as F


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
            min_lr = train_config.get('min_lr', 1e-7)
            return optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer, mode='min', patience=patience, factor=factor, min_lr=min_lr
            )
        elif scheduler_name == 'CosineAnnealingLR':
            T_max = train_config.get('scheduler_T_max', 50)
            eta_min = train_config.get('scheduler_eta_min', 1e-7)
            return optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer, T_max=T_max, eta_min=eta_min
            )
        elif scheduler_name == 'CosineAnnealingWarmRestarts':
            T_0 = train_config.get('scheduler_T_0', 10)
            T_mult = train_config.get('scheduler_T_mult', 2)
            eta_min = train_config.get('scheduler_eta_min', 1e-7)
            return optim.lr_scheduler.CosineAnnealingWarmRestarts(
                self.optimizer, T_0=T_0, T_mult=T_mult, eta_min=eta_min
            )
        elif scheduler_name == 'OneCycleLR':
            max_lr = train_config.get('max_lr', 1e-3)
            epochs = train_config.get('epochs', 50)
            steps_per_epoch = train_config.get('steps_per_epoch', 100)
            pct_start = train_config.get('pct_start', 0.3)
            anneal_strategy = train_config.get('anneal_strategy', 'cos')
            return optim.lr_scheduler.OneCycleLR(
                self.optimizer, max_lr=max_lr, epochs=epochs, 
                steps_per_epoch=steps_per_epoch, pct_start=pct_start,
                anneal_strategy=anneal_strategy
            )
        elif scheduler_name == 'ExponentialLR':
            gamma = train_config.get('scheduler_gamma', 0.95)
            return optim.lr_scheduler.ExponentialLR(self.optimizer, gamma=gamma)
        elif scheduler_name == 'StepLR':
            step_size = train_config.get('scheduler_step_size', 10)
            gamma = train_config.get('scheduler_gamma', 0.5)
            return optim.lr_scheduler.StepLR(self.optimizer, step_size=step_size, gamma=gamma)
        elif scheduler_name == 'MultiStepLR':
            milestones = train_config.get('scheduler_milestones', [20, 40, 60])
            gamma = train_config.get('scheduler_gamma', 0.5)
            return optim.lr_scheduler.MultiStepLR(self.optimizer, milestones=milestones, gamma=gamma)
        else:
            raise ValueError(f"Unknown scheduler: {scheduler_name}")
    
    def _setup_label_info(self):
        """라벨 타입 정보를 설정합니다."""
        # 컬럼 설정에서 라벨 정보 로드
        column_config_path = self.config['data']['column_config']
        with open(column_config_path, 'r') as f:
            import json
            column_config = json.load(f)
        
        self.label_types = column_config['label_types']
        self.label_columns = column_config['label_columns']
        
        # 분류/회귀 라벨 인덱스 설정
        self.cls_indices = []
        self.reg_indices = []
        
        for i, label_name in enumerate(self.label_columns):
            if label_name in self.label_types['classification']:
                self.cls_indices.append(i)
            elif label_name in self.label_types['regression']:
                self.reg_indices.append(i)
        
        print(f"Label setup:")
        print(f"  Classification indices: {self.cls_indices}")
        print(f"  Regression indices: {self.reg_indices}")
    
    def _setup_criterions(self) -> Dict[str, nn.Module]:
        """손실 함수들을 설정합니다."""
        criterions = {}
        
        # 분류 손실 함수들
        if self.cls_indices:
            cls_loss_type = self.config.get('train', {}).get('cls_loss', 'BCEWithLogitsLoss')
            
            if cls_loss_type == 'BCEWithLogitsLoss':
                # pos_weight 적용
                pos_weights = []
                for idx in self.cls_indices:
                    pos_weight = self.pos_weight_info['pos_weights'][idx] if self.pos_weight_info else 1.0
                    pos_weights.append(pos_weight)
                
                if len(pos_weights) > 0:
                    pos_weight_tensor = torch.tensor(pos_weights, device=self.device)
                    criterions['classification'] = nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)
                else:
                    criterions['classification'] = nn.BCEWithLogitsLoss()
                    
            elif cls_loss_type == 'FocalLoss':
                alpha = self.config.get('train', {}).get('focal_alpha', 0.25)
                gamma = self.config.get('train', {}).get('focal_gamma', 2.0)
                criterions['classification'] = FocalLoss(alpha=alpha, gamma=gamma)
                
            elif cls_loss_type == 'LabelSmoothingLoss':
                smoothing = self.config.get('train', {}).get('label_smoothing', 0.1)
                criterions['classification'] = LabelSmoothingLoss(smoothing=smoothing)
                
            elif cls_loss_type == 'DiceLoss':
                criterions['classification'] = DiceLoss()
                
            else:
                raise ValueError(f"Unknown classification loss: {cls_loss_type}")
        
        # 회귀 손실 함수들
        if self.reg_indices:
            reg_loss_type = self.config.get('train', {}).get('reg_loss', 'MSELoss')
            
            if reg_loss_type == 'MSELoss':
                criterions['regression'] = nn.MSELoss()
            elif reg_loss_type == 'MAELoss':
                criterions['regression'] = nn.L1Loss()
            elif reg_loss_type == 'HuberLoss':
                delta = self.config.get('train', {}).get('huber_delta', 1.0)
                criterions['regression'] = nn.HuberLoss(delta=delta)
            elif reg_loss_type == 'SmoothL1Loss':
                beta = self.config.get('train', {}).get('smooth_l1_beta', 1.0)
                criterions['regression'] = nn.SmoothL1Loss(beta=beta)
            elif reg_loss_type == 'LogCoshLoss':
                criterions['regression'] = LogCoshLoss()
            else:
                raise ValueError(f"Unknown regression loss: {reg_loss_type}")
        
        return criterions


class FocalLoss(nn.Module):
    """Focal Loss for imbalanced classification"""
    
    def __init__(self, alpha: float = 0.25, gamma: float = 2.0):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
    
    def forward(self, inputs, targets):
        bce_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction='none')
        pt = torch.exp(-bce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * bce_loss
        return focal_loss.mean()


class LabelSmoothingLoss(nn.Module):
    """Label Smoothing Loss"""
    
    def __init__(self, smoothing: float = 0.1):
        super(LabelSmoothingLoss, self).__init__()
        self.smoothing = smoothing
    
    def forward(self, inputs, targets):
        # BCE with logits 적용
        log_probs = F.logsigmoid(inputs)
        smooth_targets = targets * (1 - self.smoothing) + 0.5 * self.smoothing
        loss = -(smooth_targets * log_probs + (1 - smooth_targets) * F.logsigmoid(-inputs))
        return loss.mean()


class DiceLoss(nn.Module):
    """Dice Loss for better segmentation-like tasks"""
    
    def __init__(self, smooth: float = 1e-6):
        super(DiceLoss, self).__init__()
        self.smooth = smooth
    
    def forward(self, inputs, targets):
        inputs = torch.sigmoid(inputs)
        
        # Flatten
        inputs = inputs.view(-1)
        targets = targets.view(-1)
        
        intersection = (inputs * targets).sum()
        dice = (2. * intersection + self.smooth) / (inputs.sum() + targets.sum() + self.smooth)
        
        return 1 - dice


class LogCoshLoss(nn.Module):
    """Log-Cosh Loss for regression (smooth version of MAE)"""
    
    def __init__(self):
        super(LogCoshLoss, self).__init__()
    
    def forward(self, inputs, targets):
        diff = inputs - targets
        return torch.mean(torch.log(torch.cosh(diff + 1e-8)))
    
    def _setup_loss_wrapper(self) -> MultiTaskLossWrapper:
        """MultiTaskLossWrapper를 설정합니다."""
        train_config = self.config.get('train', {})
        loss_fn = train_config.get('loss_fn', 'uncertainty')
        
        # 태스크 수 계산 (분류 + 회귀)
        task_num = 0
        if self.cls_indices:
            task_num += 1
        if self.reg_indices:
            task_num += 1
        
        if task_num == 0:
            raise ValueError("No tasks defined (classification or regression)")
        
        return MultiTaskLossWrapper(task_num=task_num, loss_fn=loss_fn)
    
    def _update_metrics(self, outputs: torch.Tensor, targets: torch.Tensor):
        """
        배치별 메트릭을 업데이트합니다.
        """
        # 분류 메트릭 업데이트
        if self.cls_indices:
            cls_outputs = outputs[:, self.cls_indices]
            cls_targets = targets[:, self.cls_indices].long()
            
            probs = torch.sigmoid(cls_outputs)
            predictions = (probs > 0.5).float()
            
            # Multilabel 메트릭은 전체 배치에 대해 한 번에 업데이트
            self.metrics['cls_f1'].update(predictions, cls_targets)
            self.metrics['cls_precision'].update(predictions, cls_targets)
            self.metrics['cls_recall'].update(predictions, cls_targets)
            self.metrics['cls_auc'].update(probs, cls_targets)
        
        # 회귀 메트릭 업데이트
        if self.reg_indices:
            reg_outputs = outputs[:, self.reg_indices]
            reg_targets = targets[:, self.reg_indices]
            
            for i in range(reg_outputs.shape[1]):
                self.metrics['reg_mse'].update(reg_outputs[:, i], reg_targets[:, i])
                self.metrics['reg_mae'].update(reg_outputs[:, i], reg_targets[:, i])
                self.metrics['reg_r2'].update(reg_outputs[:, i], reg_targets[:, i])
    
    def _compute_metrics(self) -> Dict[str, float]:
        """누적된 메트릭을 계산합니다."""
        metrics = {}
        # 분류 메트릭 계산
        if self.cls_indices:
            metrics.update({
                'cls_f1_score': self.metrics['cls_f1'].compute().item(),
                'cls_precision': self.metrics['cls_precision'].compute().item(),
                'cls_recall': self.metrics['cls_recall'].compute().item(),
                'cls_auc': self.metrics['cls_auc'].compute().item()
            })
        # 회귀 메트릭 계산
        if self.reg_indices:
            r2 = self.metrics['reg_r2'].compute().item()
            metrics.update({
                'reg_mse': self.metrics['reg_mse'].compute().item(),
                'reg_mae': self.metrics['reg_mae'].compute().item(),
                'reg_r2': r2
            })
        # 전체 메트릭 (가중 평균)
        if self.cls_indices and self.reg_indices:
            total_f1 = metrics.get('cls_f1_score', 0)
            total_r2 = metrics.get('reg_r2', 0)
            total_r2 = max(0, total_r2)  # R2 음수 클리핑
            metrics['combined_score'] = (total_f1 + total_r2) / 2
        elif self.cls_indices:
            metrics['combined_score'] = metrics.get('cls_f1_score', 0)
        elif self.reg_indices:
            total_r2 = metrics.get('reg_r2', 0)
            total_r2 = max(0, total_r2)
            metrics['combined_score'] = total_r2
        return metrics
    
    def _setup_metrics(self):
        """TorchMetrics를 설정합니다."""
        self.metrics = {}
        
        # 분류 메트릭 설정
        if self.cls_indices:
            num_classes = len(self.cls_indices)
            self.metrics['cls_f1'] = MultilabelF1Score(num_labels=num_classes, average="macro").to(self.device)
            self.metrics['cls_precision'] = MultilabelPrecision(num_labels=num_classes, average="macro").to(self.device)
            self.metrics['cls_recall'] = MultilabelRecall(num_labels=num_classes, average="macro").to(self.device)
            self.metrics['cls_auc'] = MultilabelAUROC(num_labels=num_classes, average="macro").to(self.device)
        
        # 회귀 메트릭 설정
        if self.reg_indices:
            self.metrics['reg_mse'] = MeanSquaredError().to(self.device)
            self.metrics['reg_mae'] = MeanAbsoluteError().to(self.device)
            self.metrics['reg_r2'] = R2Score().to(self.device)
    
    def _calculate_loss(self, outputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """멀티태스크 손실을 계산합니다."""
        losses = []
        loss_components = {}
        
        # 분류 손실 계산
        if self.cls_indices and 'classification' in self.criterions:
            cls_outputs = outputs[:, self.cls_indices]
            cls_targets = targets[:, self.cls_indices]
            cls_loss = self.criterions['classification'](cls_outputs, cls_targets)
            losses.append(cls_loss)
            loss_components['classification_loss'] = cls_loss.item()
        
        # 회귀 손실 계산
        if self.reg_indices and 'regression' in self.criterions:
            reg_outputs = outputs[:, self.reg_indices]
            reg_targets = targets[:, self.reg_indices]
            reg_loss = self.criterions['regression'](reg_outputs, reg_targets)
            losses.append(reg_loss)
            loss_components['regression_loss'] = reg_loss.item()
        
        # MultiTaskLossWrapper로 손실 결합
        if len(losses) > 0:
            total_loss = self.loss_wrapper(losses)
        else:
            total_loss = torch.tensor(0.0, device=outputs.device)
        
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
            metric.reset()
        
        pbar = tqdm(train_loader, desc="Training")
        for batch_idx, batch in enumerate(pbar):
            if batch is None or len(batch) == 0 or batch[0].numel() == 0:
                continue
            images, targets, _ = batch
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
            metric.reset()
        
        with torch.no_grad():
            pbar = tqdm(val_loader, desc="Validation")
            for batch_idx, batch in enumerate(pbar):
                if batch is None or len(batch) == 0 or batch[0].numel() == 0:
                    continue
                images, targets, _ = batch
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
            
            if self.cls_indices:
                print(f"Train F1: {train_epoch_metrics.get('cls_f1_score', 0):.4f}, Val F1: {val_epoch_metrics.get('cls_f1_score', 0):.4f}")
                print(f"Train AUC: {train_epoch_metrics.get('cls_auc', 0):.4f}, Val AUC: {val_epoch_metrics.get('cls_auc', 0):.4f}")
            
            if self.reg_indices:
                print(f"Train R2: {train_epoch_metrics.get('reg_r2', 0):.4f}, Val R2: {val_epoch_metrics.get('reg_r2', 0):.4f}")
                print(f"Train MSE: {train_epoch_metrics.get('reg_mse', 0):.4f}, Val MSE: {val_epoch_metrics.get('reg_mse', 0):.4f}")
            
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
        
        if self.cls_indices:
            print(f"Best validation F1: {self.best_val_metrics.get('cls_f1_score', 0):.4f}")
            print(f"Best validation AUC: {self.best_val_metrics.get('cls_auc', 0):.4f}")
        
        if self.reg_indices:
            print(f"Best validation R2: {self.best_val_metrics.get('reg_r2', 0):.4f}")
            print(f"Best validation MSE: {self.best_val_metrics.get('reg_mse', 0):.4f}")
        
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
        
        if self.cls_indices:
            print(f"Test F1: {test_metrics.get('cls_f1_score', 0):.4f}")
            print(f"Test AUC: {test_metrics.get('cls_auc', 0):.4f}")
        
        if self.reg_indices:
            print(f"Test R2: {test_metrics.get('reg_r2', 0):.4f}")
            print(f"Test MSE: {test_metrics.get('reg_mse', 0):.4f}")
        
        print(f"Test combined score: {test_metrics.get('combined_score', 0):.4f}")
        
        return test_metrics 