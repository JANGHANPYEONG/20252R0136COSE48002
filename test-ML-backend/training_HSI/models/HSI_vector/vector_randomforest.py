from sklearn.ensemble import RandomForestRegressor
from typing import Dict

class RandomForestWrapper:
    def __init__(self, config):
        self.config = config

        self.n_estimators = self.config.get("train", {}).get("n_estimators", 100)
        self.max_depth = self.config.get("train", {}).get("max_depth", None)
        self.min_samples_split = self.config.get("train", {}).get("min_samples_split", 2)
        self.random_state = self.config.get("train", {}).get("random_state", None)

        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            random_state=self.random_state
        )

    def fit(self, X, y):
        """데이터 변환"""
        return self.model.fit(X, y)

    def predict(self, X):
        """MLflow 호환성을 위한 predict 메서드 (transform과 동일)"""
        return self.model.predict(X)
    
    def get_params(self, deep=True):
        params = {'config': self.config}
        if not deep:
            return params
        params.update(self.model.get_params(deep=True))
        return params

    def set_params(self, **params):
        if 'config' in params:
            self.config = params.pop('config')
        self.model.set_params(**params)
        return self


def create_model(config: Dict):
    """RandomForest 모델 생성 함수"""
    return RandomForestWrapper(config)