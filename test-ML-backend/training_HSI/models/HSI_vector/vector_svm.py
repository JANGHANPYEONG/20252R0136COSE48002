from sklearn.svm import SVR
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from typing import Dict


class SVMWrapper:
    def __init__(self, config):
        self.config = config

        self.kernel = self.config.get('kernel', 'rbf')
        self.C = self.config.get('C', 1.0)
        self.gamma = self.config.get('gamma', 'scale')
        self.degree = self.config.get('degree', 3)
        self.coef0 = self.config.get('coef0', 0.0)

        self.model = Pipeline([
            ('standardscaler', StandardScaler()),
            ('svm', MultiOutputRegressor(SVR(
                kernel=self.kernel,
                C=self.C,
                gamma=self.gamma,
                degree=self.degree,
                coef0=self.coef0
            )))
        ])

    def fit(self, X, y):
        return self.model.fit(X, y)

    def predict(self, X):
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
    return SVMWrapper(config)
