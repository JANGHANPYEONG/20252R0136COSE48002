from typing import Dict, Any, Tuple, List
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score, accuracy_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold, StratifiedKFold
from collections import defaultdict
import time
from tqdm import tqdm


class vectorTrainer:
    """ML 모델 훈련을 위한 클래스"""

    def __init__(self, model, config: Dict[str, Any]):
        """
        Args:
            model: 훈련할 모델
            config: 설정 딕셔너리
        """
        self.model = model
        self.config = config

        # label info 불러오기
        self._setup_label_info()

        # 메트릭 설정
        self._setup_metrics()

        # 훈련 상태 초기화
        self.best_val_loss = float('inf')
        self.best_val_metrics = {}
        self.seed = config.get('seed', 42)


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

        
    def _setup_metrics(self):
        """TorchMetrics를 설정합니다."""
        self.metrics = {}
        
        # 분류 메트릭 설정
        if self.cls_indices:
            self.metrics['cls_f1'] = lambda y_true, y_pred: f1_score(y_true, y_pred, average='macro')
            self.metrics['cls_precision'] = lambda y_true, y_pred: precision_score(y_true, y_pred, average='macro')
            self.metrics['cls_recall'] = lambda y_true, y_pred: recall_score(y_true, y_pred, average='macro')
            self.metrics['cls_auc'] = lambda y_true, y_prob: roc_auc_score(y_true, y_prob, average='macro')
        
        # 회귀 메트릭 설정
        if self.reg_indices:
            self.metrics['reg_mse'] = lambda y_true, y_pred: mean_squared_error(y_true, y_pred)
            self.metrics['reg_mae'] = lambda y_true, y_pred: mean_absolute_error(y_true, y_pred)
            self.metrics['reg_r2'] = lambda y_true, y_pred: r2_score(y_true, y_pred)


    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    

    def _calculate_metrics(self, y_pred, y_test):
        """
        배치별 메트릭을 업데이트합니다.
        """
        results = {}
        # 분류 메트릭 업데이트
        if self.cls_indices:
            cls_outputs = y_pred[:, self.cls_indices]
            cls_targets = y_test[:, self.cls_indices]

            probs = self._sigmoid(cls_outputs)
            predictions = (probs > 0.5).astype(int)

            # Multilabel 메트릭은 전체 배치에 대해 한 번에 업데이트
            results['cls_f1'] = self.metrics['cls_f1'](cls_targets, predictions)
            results['cls_precision'] = self.metrics['cls_precision'](cls_targets, predictions)
            results['cls_recall'] = self.metrics['cls_recall'](cls_targets, predictions)
            results['cls_auc'] = self.metrics['cls_auc'](cls_targets, probs)

        # 회귀 메트릭 업데이트
        if self.reg_indices:
            reg_outputs = y_pred[:, self.reg_indices]
            reg_targets = y_test[:, self.reg_indices]

            results['reg_mse'] = self.metrics['reg_mse'](reg_targets, reg_outputs)
            results['reg_mae'] = self.metrics['reg_mae'](reg_targets, reg_outputs)
            results['reg_r2'] = self.metrics['reg_r2'](reg_targets, reg_outputs)

        # Combined 매트릭 업데이트
        if self.cls_indices and self.reg_indices:
            total_f1 = results.get('cls_f1_score', 0)
            total_r2 = results.get('reg_r2', 0)
            total_r2 = max(0, total_r2)  # R2 음수 클리핑
            results['combined_score'] = (total_f1 + total_r2) / 2
        elif self.cls_indices:
            results['combined_score'] = results.get('cls_f1', 0)
        elif self.reg_indices:
            total_r2 = results.get('reg_r2', 0)
            total_r2 = max(0, total_r2)
            results['combined_score'] = total_r2

        return results

    def train(self, X_train, y_train, K_fold=5, logger=None) -> Dict[str, List[float]]:
        """전체 훈련을 수행합니다."""

        # 훈련 기록
        train_losses_each_fold = []
        val_losses_each_fold = []
        train_metrics = {}
        val_metrics = {}

        # 훈련 시간 기록
        start_time = time.time()

        # K-fold 설정
        kf = KFold(n_splits=K_fold, shuffle=True, random_state=self.seed)

            # ────────────────── K‑fold 루프 ──────────────────
        for fold_idx, (tr_idx, val_idx) in enumerate(kf.split(X_train, y_train)):
            X_tr, X_val = X_train[tr_idx], X_train[val_idx]
            y_tr, y_val = y_train[tr_idx], y_train[val_idx]

            # 모델에서 scaler를 적용하지 않은 경우
            is_scaler = self.config.get('scaler', None)
            if is_scaler == None:
                scaler = StandardScaler()
                X_tr = scaler.fit_transform(X_tr)
                X_val = scaler.transform(X_val)

            # 모델 인스턴스 생성 & 학습
            self.model.fit(X_tr, y_tr)

            # 예측
            y_tr_pred = self.model.predict(X_tr)
            y_val_pred = self.model.predict(X_val)

            # 손실 계산
            cls_tr_loss, cls_val_loss, reg_tr_loss, reg_val_loss = 0.0, 0.0, 0.0, 0.0

            # 손실(회귀는 MSE, 분류는 1‑정확도) 계산
            if self.cls_indices:
                cls_tr_loss = 1.0 - accuracy_score(y_tr[:, self.cls_indices], y_tr_pred[:, self.cls_indices])
                cls_val_loss = 1.0 - accuracy_score(y_val[:, self.cls_indices], y_val_pred[:, self.cls_indices])
            if self.reg_indices:
                reg_tr_loss = mean_squared_error(y_tr[:, self.reg_indices], y_tr_pred[:, self.reg_indices])
                reg_val_loss = mean_squared_error(y_val[:, self.reg_indices], y_val_pred[:, self.reg_indices])

            cls_len, reg_len = len(self.cls_indices), len(self.reg_indices)
            if self.cls_indices and self.reg_indices:
                tr_loss = (cls_tr_loss * cls_len + reg_tr_loss * reg_len) / (cls_len + reg_len)
                val_loss = (cls_val_loss * cls_len + reg_val_loss * reg_len) / (cls_len + reg_len)
            elif self.cls_indices:
                tr_loss = cls_tr_loss
                val_loss = cls_val_loss
            elif self.reg_indices:
                tr_loss = reg_tr_loss
                val_loss = reg_val_loss
            else:
                raise ValueError("No task specified (classification or regression)")

            # 지표 계산 및 기록
            train_metrics[f'fold {fold_idx+1}'] = self._calculate_metrics(y_tr, y_tr_pred)
            val_metrics[f'fold {fold_idx+1}'] = self._calculate_metrics(y_val, y_val_pred)

            # loss 기록
            train_losses_each_fold.append(tr_loss)
            val_losses_each_fold.append(val_loss)

            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.best_val_metrics = val_metrics[f'fold {fold_idx+1}']
                
                # 모델 저장
                if logger is not None:
                    logger.log_model_ml(self.model, "best_model")
                    print("New best model saved!")

        # 결과 정리
        training_time = time.time() - start_time
        print(f"\n✅ Training done in {training_time/60:.2f} min")
        print(f"Best val loss: {self.best_val_loss:.4f}")
        print("Metrics for each fold:")
        for i in range(K_fold):
            print(f"  Fold {i+1}:")
            if self.cls_indices:
                print(f"   F1 Score: train set-{train_metrics[f'fold {i+1}']['cls_f1']:.4f}, validation set-{val_metrics[f'fold {i+1}']['cls_f1']:.4f}")
                print(f"    Precision: train set-{train_metrics[f'fold {i+1}']['cls_precision']:.4f}, validation set-{val_metrics[f'fold {i+1}']['cls_precision']:.4f}")
                print(f"    Recall: train set-{train_metrics[f'fold {i+1}']['cls_recall']:.4f}, validation set-{val_metrics[f'fold {i+1}']['cls_recall']:.4f}")
                print(f"    AUC: train set-{train_metrics[f'fold {i+1}']['cls_auc']:.4f}, validation set-{val_metrics[f'fold {i+1}']['cls_auc']:.4f}")
            if self.reg_indices:
                print(f"    MSE: train set-{train_metrics[f'fold {i+1}']['reg_mse']:.4f}, validation set-{val_metrics[f'fold {i+1}']['reg_mse']:.4f}")
                print(f"    MAE: train set-{train_metrics[f'fold {i+1}']['reg_mae']:.4f}, validation set-{val_metrics[f'fold {i+1}']['reg_mae']:.4f}")
                print(f"    R2: train set-{train_metrics[f'fold {i+1}']['reg_r2']:.4f}, validation set-{val_metrics[f'fold {i+1}']['reg_r2']:.4f}")

        return {
            'train_losses': train_losses_each_fold,
            'val_losses': val_losses_each_fold,
            'train_metrics': train_metrics,
            'val_metrics': val_metrics,
            'best_val_metrics': self.best_val_metrics,
            'training_time': training_time
        }


    def evaluate(self, X_test, y_test) -> Dict[str, float]:
        """테스트 데이터로 평가합니다."""
        y_pred = self.model.predict(X_test)
        metrics = {}

        # 손실(회귀는 MSE, 분류는 1‑정확도) 계산
        if self.cls_indices:
            cls_outputs = y_pred[:, self.cls_indices]
            cls_targets = y_test[:, self.cls_indices]

            probs = self._sigmoid(cls_outputs)
            predictions = (probs > 0.5).astype(int)
            loss = 1.0 - accuracy_score(cls_targets, predictions)

            metrics['cls_f1_score'] = self.metrics['cls_f1'](cls_targets, predictions)
            metrics['cls_precision'] = self.metrics['cls_precision'](cls_targets, predictions)
            metrics['cls_recall'] = self.metrics['cls_recall'](cls_targets, predictions)
            metrics['cls_auc'] = self.metrics['cls_auc'](cls_targets, probs)
        if self.reg_indices:
            reg_outputs = y_pred[:, self.reg_indices]
            reg_targets = y_test[:, self.reg_indices]

            loss = mean_squared_error(reg_targets, reg_outputs)

            metrics['reg_mse'] = self.metrics['reg_mse'](reg_targets, reg_outputs)
            metrics['reg_mae'] = self.metrics['reg_mae'](reg_targets, reg_outputs)
            metrics['reg_r2'] = self.metrics['reg_r2'](reg_targets, reg_outputs)

        # 결과 출력
        print(f"  Test Loss: {loss:.4f}")
        for metric_name, metric_value in metrics.items():
            print(f"    Test {metric_name}: {metric_value:.4f}")

        return {
            'loss': loss,
            **metrics
        }