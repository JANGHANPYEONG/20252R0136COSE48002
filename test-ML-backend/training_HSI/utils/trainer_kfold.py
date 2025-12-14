"""
K-Fold Cross Validation Trainer for HSI Regression
작은 데이터셋(159개)을 위한 K-Fold 교차 검증
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from typing import Dict, Any, List
import numpy as np
from sklearn.model_selection import KFold
from tqdm import tqdm
import time
import os
import tempfile

from .trainer_vit_regression import HSITrainer


class KFoldTrainer:
    """K-Fold 교차 검증을 위한 Trainer"""

    def __init__(self, config: Dict[str, Any], device: torch.device,
                 create_model_fn, dataset, pos_weight_info: Dict[str, Any] = None):
        """
        Args:
            config: 설정 딕셔너리
            device: 사용할 디바이스
            create_model_fn: 모델 생성 함수
            dataset: 전체 데이터셋
            pos_weight_info: 라벨 통계 정보
        """
        self.config = config
        self.device = device
        self.create_model_fn = create_model_fn
        self.dataset = dataset
        self.pos_weight_info = pos_weight_info

        # K-Fold 설정
        self.n_splits = config.get('kfold', {}).get('n_splits', 5)
        self.random_state = config.get('seed', 42)

        # 결과 저장
        self.fold_results = []

        print(f"K-Fold Cross Validation Setup:")
        print(f"  Total samples: {len(dataset)}")
        print(f"  Folds: {self.n_splits}")
        print(f"  Samples per fold: ~{len(dataset) // self.n_splits}")

    def train(self, logger=None) -> Dict[str, Any]:
        """K-Fold 교차 검증 수행"""
        print("\n" + "="*70)
        print(f"Starting {self.n_splits}-Fold Cross Validation")
        print("="*70)

        kfold = KFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)

        # 각 fold별 훈련
        for fold, (train_idx, val_idx) in enumerate(kfold.split(range(len(self.dataset)))):
            print(f"\n{'='*70}")
            print(f"FOLD {fold + 1}/{self.n_splits}")
            print(f"{'='*70}")
            print(f"Train samples: {len(train_idx)}, Val samples: {len(val_idx)}")

            # Fold별 데이터 로더 생성
            train_loader, val_loader = self._create_fold_loaders(train_idx, val_idx)

            # 새 모델 생성
            model = self.create_model_fn(self.config)
            model = model.to(self.device)

            # Trainer 생성
            trainer = HSITrainer(model, self.device, self.config, self.pos_weight_info)

            # 훈련
            start_time = time.time()
            training_results = trainer.train(
                train_loader=train_loader,
                val_loader=val_loader,
                num_epochs=self.config['train']['epochs'],
                logger=None  # Fold별 MLflow 로깅은 선택적
            )
            fold_time = time.time() - start_time

            # Fold 결과 저장
            fold_result = {
                'fold': fold + 1,
                'train_size': len(train_idx),
                'val_size': len(val_idx),
                'best_val_loss': trainer.best_val_loss,
                'best_val_metrics': trainer.best_val_metrics,
                'training_time': fold_time,
                'final_train_loss': training_results['train_losses'][-1] if training_results['train_losses'] else None,
                'final_val_loss': training_results['val_losses'][-1] if training_results['val_losses'] else None,
            }

            self.fold_results.append(fold_result)

            # Fold 결과 출력
            print(f"\nFold {fold + 1} Results:")
            print(f"  Best Val Loss: {trainer.best_val_loss:.4f}")
            print(f"  Best Val R²: {trainer.best_val_metrics.get('r2', 0):.4f}")
            print(f"  Best Val MSE: {trainer.best_val_metrics.get('mse', 0):.4f}")
            print(f"  Best Val MAE: {trainer.best_val_metrics.get('mae', 0):.4f}")
            print(f"  Training Time: {fold_time/60:.2f} minutes")

            # 모델 저장
            if self.config.get('kfold', {}).get('save_fold_models', True):
                self._save_fold_model(model, fold + 1, trainer.best_val_metrics)

        # 전체 결과 집계
        aggregated_results = self._aggregate_results()

        # 최종 결과 출력
        self._print_final_results(aggregated_results)

        # MLflow 로깅
        if logger is not None:
            self._log_kfold_results(logger, aggregated_results)

        return {
            'fold_results': self.fold_results,
            'aggregated_results': aggregated_results
        }

    def _create_fold_loaders(self, train_idx, val_idx):
        """Fold별 데이터 로더 생성"""
        batch_size = self.config['data']['batch_size']
        num_workers = self.config['data']['num_workers']

        # Subset 생성
        train_subset = Subset(self.dataset, train_idx)
        val_subset = Subset(self.dataset, val_idx)

        # DataLoader worker 시드 고정 함수
        def seed_worker(worker_id):
            import random
            worker_seed = self.random_state + worker_id
            np.random.seed(worker_seed)
            torch.manual_seed(worker_seed)
            random.seed(worker_seed)

        generator = torch.Generator()
        generator.manual_seed(self.random_state)

        # Collate 함수 import
        from .dataset_vit_regression import skip_invalid_collate

        # DataLoader 생성
        train_loader = DataLoader(
            train_subset, batch_size=batch_size, shuffle=True,
            num_workers=num_workers, pin_memory=True,
            worker_init_fn=seed_worker, generator=generator,
            collate_fn=skip_invalid_collate
        )

        val_loader = DataLoader(
            val_subset, batch_size=batch_size, shuffle=False,
            num_workers=num_workers, pin_memory=True,
            worker_init_fn=seed_worker, generator=generator,
            collate_fn=skip_invalid_collate
        )

        return train_loader, val_loader

    def _aggregate_results(self) -> Dict[str, Any]:
        """Fold 결과 집계"""
        metrics_keys = ['r2', 'mse', 'mae', 'combined_score']

        aggregated = {
            'n_folds': self.n_splits,
            'total_samples': len(self.dataset),
        }

        # 각 메트릭별 평균/표준편차
        for key in metrics_keys:
            values = [fold['best_val_metrics'].get(key, 0) for fold in self.fold_results]
            aggregated[f'{key}_mean'] = np.mean(values)
            aggregated[f'{key}_std'] = np.std(values)
            aggregated[f'{key}_min'] = np.min(values)
            aggregated[f'{key}_max'] = np.max(values)

        # 손실 평균/표준편차
        val_losses = [fold['best_val_loss'] for fold in self.fold_results]
        aggregated['val_loss_mean'] = np.mean(val_losses)
        aggregated['val_loss_std'] = np.std(val_losses)
        aggregated['val_loss_min'] = np.min(val_losses)
        aggregated['val_loss_max'] = np.max(val_losses)

        # 훈련 시간 합계
        total_time = sum(fold['training_time'] for fold in self.fold_results)
        aggregated['total_training_time'] = total_time

        return aggregated

    def _print_final_results(self, results: Dict[str, Any]):
        """최종 결과 출력"""
        print("\n" + "="*70)
        print(f"{results['n_folds']}-Fold Cross Validation Results")
        print("="*70)

        print(f"\nValidation Loss:")
        print(f"  Mean ± Std: {results['val_loss_mean']:.4f} ± {results['val_loss_std']:.4f}")
        print(f"  Range: [{results['val_loss_min']:.4f}, {results['val_loss_max']:.4f}]")

        print(f"\nR² Score:")
        print(f"  Mean ± Std: {results['r2_mean']:.4f} ± {results['r2_std']:.4f}")
        print(f"  Range: [{results['r2_min']:.4f}, {results['r2_max']:.4f}]")

        print(f"\nMSE:")
        print(f"  Mean ± Std: {results['mse_mean']:.4f} ± {results['mse_std']:.4f}")
        print(f"  Range: [{results['mse_min']:.4f}, {results['mse_max']:.4f}]")

        print(f"\nMAE:")
        print(f"  Mean ± Std: {results['mae_mean']:.4f} ± {results['mae_std']:.4f}")
        print(f"  Range: [{results['mae_min']:.4f}, {results['mae_max']:.4f}]")

        print(f"\nCombined Score:")
        print(f"  Mean ± Std: {results['combined_score_mean']:.4f} ± {results['combined_score_std']:.4f}")
        print(f"  Range: [{results['combined_score_min']:.4f}, {results['combined_score_max']:.4f}]")

        print(f"\nTotal Training Time: {results['total_training_time']/60:.2f} minutes")
        print("="*70)

    def _save_fold_model(self, model: nn.Module, fold: int, metrics: Dict[str, float]):
        """Fold별 모델 저장"""
        save_dir = os.path.join('checkpoints', self.config.get('experiment', 'default'), 'kfold')
        os.makedirs(save_dir, exist_ok=True)

        model_path = os.path.join(save_dir, f'fold_{fold}_model.pth')
        torch.save({
            'fold': fold,
            'model_state_dict': model.state_dict(),
            'metrics': metrics,
            'config': self.config
        }, model_path)

        print(f"  Saved fold {fold} model to: {model_path}")

    def _log_kfold_results(self, logger, results: Dict[str, Any]):
        """MLflow에 K-Fold 결과 로깅"""
        # 집계 메트릭 로깅
        metrics_to_log = {
            f'kfold_{k}': v for k, v in results.items()
            if isinstance(v, (int, float))
        }
        logger.log_metrics(metrics_to_log)

        # Fold별 결과 로깅
        for fold_result in self.fold_results:
            fold_num = fold_result['fold']
            fold_metrics = {
                f'fold_{fold_num}_val_loss': fold_result['best_val_loss'],
                f'fold_{fold_num}_r2': fold_result['best_val_metrics'].get('r2', 0),
                f'fold_{fold_num}_mse': fold_result['best_val_metrics'].get('mse', 0),
                f'fold_{fold_num}_mae': fold_result['best_val_metrics'].get('mae', 0),
            }
            logger.log_metrics(fold_metrics)

        print("K-Fold results logged to MLflow")
