from typing import Dict, Any, Tuple, List
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import KFold, StratifiedKFold
import time
from tqdm import tqdm


class vectorTrainer:
    """ML 모델 훈련을 위한 클래스"""

    def __init__(self, model, task: str, config: Dict[str, Any]):
        """
        Args:
            model: 훈련할 모델
            config: 설정 딕셔너리
        """
        self.model = model
        self.task = task
        self.config = config

        # 메트릭 설정
        self._setup_metrics()

        # 훈련 상태 초기화
        self.best_val_loss = float('inf')
        self.best_val_metrics = {}
        self.seed = config.get('seed', 42)


    def _setup_metrics(self):
        """메트릭을 설정합니다."""
        self.metrics = {}

        # 분류 메트릭
        if self.task == "classification":
            self.metrics['cls_f1'] = []
            self.metrics['cls_precision'] = []
            self.metrics['cls_recall'] = []
            self.metrics['cls_auc'] = []

        # 회귀 메트릭
        elif self.task == "regression":
            self.metrics['reg_mse'] = []
            self.metrics['reg_mae'] = []
            self.metrics['reg_r2'] = []

        else:
            raise ValueError(f"Unknown task type: {self.task}")

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def _update_metrics(self, y_true, y_pred) -> Dict[str, float]:
        """메트릭을 업데이트합니다."""
        if self.task == "classification":
            probs = self._sigmoid(y_pred)
            y_pred_binary = (probs > 0.5).astype(int)
            scores = precision_recall_fscore_support(y_true, y_pred_binary, average='weighted')
            self.metrics['cls_f1'].append(scores[2])
            self.metrics['cls_precision'].append(scores[0])
            self.metrics['cls_recall'].append(scores[1])
            self.metrics['cls_auc'].append(roc_auc_score(y_true, probs, multi_class='ovr', average='weighted'))

        # 회귀 메트릭 업데이트
        else:
            self.metrics['reg_mse'].append(mean_squared_error(y_true, y_pred))
            self.metrics['reg_mae'].append(mean_absolute_error(y_true, y_pred))
            self.metrics['reg_r2'].append(r2_score(y_true, y_pred))

    def train(self, X_train, y_train, K_fold=5, logger=None) -> Dict[str, List[float]]:
        """전체 훈련을 수행합니다."""

        # 훈련 기록
        train_losses = []
        val_losses = []
        train_metrics = {}
        val_metrics = {}

        start_time = time.time()

        # 결과 저장용 컨테이너
        train_losses, val_losses = [], []
        train_metrics, val_metrics = [], []

        # K-fold 설정
        if self.task == "classification":
            kf = StratifiedKFold(n_splits=K_fold, shuffle=True, random_state=self.seed)
        elif self.task == "regression":
            kf = KFold(n_splits=K_fold, shuffle=True, random_state=self.seed)
        else:
            raise ValueError(f"Unknown task type: {self.task}")

            # ────────────────── K‑fold 루프 ──────────────────
        for fold_idx, (tr_idx, val_idx) in enumerate(kf.split(X_train, y_train)):
            X_tr, X_val = X_train[tr_idx], X_train[val_idx]
            y_tr, y_val = y_train[tr_idx], y_train[val_idx]

            # 모델 인스턴스 생성 & 학습
            self.model.fit(X_tr, y_tr)

            # 예측
            y_tr_pred = self.model.predict(X_tr)
            y_val_pred = self.model.predict(X_val)

            # 손실(회귀는 MSE, 분류는 1‑정확도) 계산
            if self.task == "classification":
                tr_loss = 1.0 - accuracy_score(y_tr, y_tr_pred)
                val_loss = 1.0 - accuracy_score(y_val, y_val_pred)
            else:
                tr_loss = mean_squared_error(y_tr, y_tr_pred)
                val_loss = mean_squared_error(y_val, y_val_pred)

            # 지표 계산
            self._update_metrics(y_tr, y_tr_pred)
            self._update_metrics(y_val, y_val_pred)

            # 기록
            train_losses.append(tr_loss)
            val_losses.append(val_loss)

            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.patience_counter = 0
                
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
            if self.task == "classification":
                print(f"    F1 Score: {self.metrics['cls_f1'][i]:.4f}")
                print(f"    Precision: {self.metrics['cls_precision'][i]:.4f}")
                print(f"    Recall: {self.metrics['cls_recall'][i]:.4f}")
                print(f"    AUC: {self.metrics['cls_auc'][i]:.4f}")
            else:
                print(f"    MSE: {self.metrics['reg_mse'][i]:.4f}")
                print(f"    MAE: {self.metrics['reg_mae'][i]:.4f}")
                print(f"    R2: {self.metrics['reg_r2'][i]:.4f}")

        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
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
        if self.task == "classification":
            probs = self._sigmoid(y_pred)
            y_pred_binary = (probs > 0.5).astype(int)
            loss = 1.0 - accuracy_score(y_test, y_pred_binary)

            metrics['cls_f1_score'] = precision_recall_fscore_support(y_test, y_pred_binary, average='weighted')[2]
            metrics['cls_precision'] = precision_recall_fscore_support(y_test, y_pred_binary, average='weighted')[0]
            metrics['cls_recall'] = precision_recall_fscore_support(y_test, y_pred_binary, average='weighted')[1]
            metrics['cls_auc'] = roc_auc_score(y_test, y_pred_binary, multi_class='ovr', average='weighted')
        else:
            loss = mean_squared_error(y_test, y_pred)

            metrics['reg_mse'] = mean_squared_error(y_test, y_pred)
            metrics['reg_mae'] = mean_absolute_error(y_test, y_pred)
            metrics['reg_r2'] = r2_score(y_test, y_pred)

        # 결과 출력
        print(f"  Test Loss: {loss:.4f}")
        for metric_name, metric_value in metrics.items():
            print(f"    Test {metric_name}: {metric_value:.4f}")

        return {
            'loss': loss,
            **metrics
        }