"""
벡터 기반 전통 ML 모델의 하이퍼파라미터 탐색과 평가 지표 계산을 담당하는 모듈.

Grid/Bayes/Random Search 래퍼와 멀티태스크 메트릭 유틸리티를 제공한다.
"""

import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score, accuracy_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, make_scorer
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from skopt import BayesSearchCV
from sklearn.base import BaseEstimator
import time
from tqdm import tqdm


class SearchHyperparameter(BaseEstimator):
    """
    search_type: 'grid' or 'bayes'
    For 'grid', provide param_grid (dict).
    For 'bayes', provide search_spaces (dict of skopt space tuples).
    Other args: cv, scoring, n_iter (for bayes), n_jobs, verbose, refit, random_state.
    """
    def __init__(self, config, estimator, pos_weight_info=None):   
        self.config = config
        self.estimator = estimator
        self.pos_weight_info = pos_weight_info

        self.method = self.config.get('train', {}).get('method', 'gridsearchcv')
        self.param_grid = self.config.get('train', {}).get('param_grid', {})
        self.cv = self.config.get('train', {}).get('cv', 5)
        self.scoring_method = self.config.get('train', {}).get('scoring', 'r2')
        self.n_iter = self.config.get('train', {}).get('n_iter', 20)
        self.n_jobs = self.config.get('train', {}).get('n_jobs', -1)
        self.verbose = self.config.get('train', {}).get('verboe', False)
        self.refit = self.config.get('train', {}).get('refit', True)
        self.random_state = self.config.get('seed', 42)

        self._setup_label_info()

        # scorer 설정
        if self.scoring_method == 'mt_scorer':
            self.scoring = make_scorer(self._mt_loss, greater_is_better=False)
        elif self.scoring_method == 'r2':
            self.scoring = 'r2'
        else:
            self.scoring = 'f1'

        # hyperparameter 튜닝 방식 설정
        if self.method == 'gridsearchcv':
            self.searcher = GridSearchCV(
                estimator=self.estimator,
                param_grid=self.param_grid,
                cv=self.cv,
                scoring=self.scoring,
                n_jobs=self.n_jobs,
                verbose=self.verbose,
                refit=self.refit
            )
        elif self.method == 'randomizedsearchcv':
            self.searcher = RandomizedSearchCV(
                estimator=self.estimator,
                param_distributions=self.param_grid,
                cv=self.cv,
                scoring=self.scoring,
                n_jobs=self.n_jobs,
                verbose=self.verbose,
                refit=self.refit
            )
        elif self.method == 'bayessearchcv':
            self.searcher = BayesSearchCV(
                estimator=self.estimator,
                search_spaces=self.param_grid,
                n_iter=self.n_iter,
                cv=self.cv,
                scoring=self.scoring,
                n_jobs=self.n_jobs,
                verbose=self.verbose,
                random_state=self.random_state,
                refit=self.refit
            )
        elif self.method == 'no':
            self.searcher = 'no'
        else:
            raise ValueError("search_type must be 'gridsearchcv', 'randomizedsearchcv' or 'bayessearchcv'")
        
        
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
        print(f"  Regression indices: {self.reg_indices}\n")


    def _mt_loss(self, y_test, y_pred):
        cls_loss, reg_loss, loss = 0.0, 0.0, 0.0

        if self.cls_indices:
            cls_outputs = y_pred[:, self.cls_indices]
            cls_targets = y_test[:, self.cls_indices]

            probs = self._sigmoid(cls_outputs)
            predictions = (probs > 0.5).astype(int)

            if self.pos_weight_info:
                # weight each label's F1 by provided pos weights
                weights = []
                f1s = []
                for idx in self.cls_indices:
                    label = self.label_columns[idx]
                    weight = self.pos_weight_info.get(label, 1.0)
                    weights.append(weight)
                    f1s.append(f1_score(cls_targets[:, len(f1s)], predictions[:, len(f1s)]))
                total_weight = sum(weights)
                cls_loss = sum(w * s for w, s in zip(weights, f1s)) / (total_weight if total_weight != 0 else 1)
            else:
                # default micro-averaged F1
                cls_loss = f1_score(cls_targets, predictions, average='micro')

        if self.reg_indices:
            reg_loss = r2_score(y_test[:, self.reg_indices], y_pred[:, self.reg_indices])
            reg_loss = (reg_loss + 1) / 2
            reg_loss = np.clip(reg_loss, 0, 1)

        if self.cls_indices and self.reg_indices:
            loss = (cls_loss + reg_loss) / 2
        elif self.cls_indices:
            loss = cls_loss
        else:
            loss = reg_loss
        return loss


    def calculate_metrics(self, y_test, y_pred):
        """
        각 label 별 metric을 계산
        """
        results = {}
        for idx in range(y_pred.shape[1]):
            col_name = self.label_columns[idx]
            results[col_name] = {}
            outputs = y_pred[:, idx]
            targets = y_test[:, idx]

            if idx in self.cls_indices:
                probs = self._sigmoid(outputs)
                predictions = (probs > 0.5).astype(int)

                results[col_name]['cls_f1'] = f1_score(y_true=targets, y_pred=predictions)
                results[col_name]['cls_precision'] = precision_score(y_true=targets, y_pred=predictions)
                results[col_name]['cls_recall'] = recall_score(y_true=targets, y_pred=predictions)
                results[col_name]['cls_auc'] = roc_auc_score(y_true=targets, y_score=probs)

            elif idx in self.reg_indices:
                results[col_name]['reg_mse'] = mean_squared_error(y_ture=targets, y_pred=outputs)
                results[col_name]['reg_mae'] = mean_absolute_error(y_true=targets, y_pred=outputs)
                results[col_name]['reg_r2'] = r2_score(y_true=targets, y_pred=outputs)


        # 분류 메트릭 업데이트
        if self.cls_indices:
            cls_outputs = y_pred[:, self.cls_indices]
            cls_targets = y_test[:, self.cls_indices]

            probs = self._sigmoid(cls_outputs)
            predictions = (probs > 0.5).astype(int)

            # Multilabel 메트릭은 전체 배치에 대해 한 번에 업데이트
            results['cls_f1'] = f1_score(y_true=cls_targets, y_pred=predictions, average='macro')

        # 회귀 메트릭 업데이트
        if self.reg_indices:
            reg_outputs = y_pred[:, self.reg_indices]
            reg_targets = y_test[:, self.reg_indices]

            results['reg_r2'] = self.metrics['reg_r2'](reg_targets, reg_outputs)

        # Combined 매트릭 업데이트
        if self.cls_indices and self.reg_indices:
            total_f1 = results.get('cls_f1', 0)
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
    
    
    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    

    def fit(self, X, y):
        if self.searcher == 'no': return self.estimator.fit(X, y)
        return self.searcher.fit(X, y)
    

    def predict(self, X):
        return self.searcher.predict(X)
    

    def predict_proba(self, X):
        return self.searcher.predict_proba(X)
    

    def score(self, X, y):
        return self.searcher.score(X, y)
    

    def get_params(self, deep=True):
        return {
            **self.__dict__
        }
    

    def set_params(self, **params):
        for key, val in params.items():
            setattr(self, key, val)
        return self
