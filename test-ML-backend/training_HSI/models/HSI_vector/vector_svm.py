from sklearn.svm import SVR
from sklearn.multioutput import MultiOutputRegressor
from typing import Dict


class SVMWrapper:
    def __init__(self, config):
        self.config = config

        self.kernel = self.config.get('kernel', 'rbf')
        self.C = self.config.get('C', 1.0)
        self.gamma = self.config.get('gamma', 'scale')
        self.degree = self.config.get('degree', 3)
        self.coef0 = self.config.get('coef0', 0.0)

        self.model = MultiOutputRegressor(SVR(
            kernel=self.kernel,
            C=self.C,
            gamma=self.gamma,
            degree=self.degree,
            coef0=self.coef0
        ))

    def fit(self, X, y):
        return self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)


def create_model(config: Dict):
    return SVMWrapper(config)
