from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from typing import Dict

class RandomForestWrapper:
    def __init__(self, config):
        self.config = config

        self.mlflow_info = config.get("mlflow_info", {})
        self.n_estimators = config.get("parameters", {}).get("n_estimators", 1)
        self.max_depth = config.get("parameters", {}).get("max_depth", None)
        self.min_samples_split = config.get("parameters", {}).get("min_samples_split", 2)
        self.random_state = config.get("parameters", {}).get("random_state", None)

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
        """sklearn 호환성을 위한 파라미터 반환"""
        return self.model.get_params(deep)

    def set_params(self, **params):
        """sklearn 호환성을 위한 파라미터 설정"""
        return self.model.set_params(**params)

def create_model(config: Dict):
    """RandomForest 모델 생성 함수"""
    return RandomForestWrapper(config)