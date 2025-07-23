import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_array
from typing import Dict
"""
    MSC (Multiplicative Scatter Correction) 전처리
    + PLSR (Partial Least Squares Regression)
"""

class PLSRWrapper:
    def __init__(self, config: Dict):
        self.config = config

        # PLSR 하이퍼파라미터
        self.n_components = config.get('n_components', 2)
        self.scale = config.get('scale', True)
        self.max_iter = config.get('max_iter', 500)
        self.tol = config.get('tol', 1e-06)
        self.copy = config.get('copy', True)

        self.model = Pipeline([
            ('msc', MultiplicativeScatterCorrection()),
            ('plsregression', PLSRegression(
                n_components=self.n_components,
                scale=self.scale,
                max_iter=self.max_iter,
                tol=self.tol,
                copy=self.copy
            ))
        ])

    def fit(self, X, y):
        """
        X: feature matrix, shape (n_samples, n_features)
        y: target matrix, shape (n_samples, n_targets)
        """
        return self.model.fit(X, y)

    def predict(self, X):
        """
        X: feature matrix, shape (n_samples, n_features)
        Returns: 예측값, shape (n_samples, n_targets)
        """
        return self.model.predict(X)
    

class MultiplicativeScatterCorrection(BaseEstimator, TransformerMixin):
    """
    Multiplicative Scatter Correction (MSC) transformer for spectral data.
    
    Parameters
    ----------
    reference : array-like of shape (n_features,), default=None
        Reference spectrum. If None, the mean spectrum of X (fitted data) is used.
    copy : bool, default=True
        If False, the input X may be modified in-place.
    """
    def __init__(self, reference=None, copy=True):
        self.reference = reference
        self.copy = copy

    def fit(self, X, y=None):
        """
        Fit the MSC transformer by setting the reference spectrum.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Spectral data to compute reference if not provided.
        y : None
            Ignored.
        """
        X = check_array(X, copy=self.copy)
        if self.reference is None:
            # Use mean spectrum of X as reference
            self.reference_ = np.mean(X, axis=0)
        else:
            # Use provided reference spectrum
            ref = np.asarray(self.reference)
            if ref.ndim != 1 or ref.shape[0] != X.shape[1]:
                raise ValueError("Reference spectrum must be 1D of length n_features.")
            self.reference_ = ref
        return self

    def transform(self, X):
        """
        Apply MSC to the data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Spectral data to correct.

        Returns
        -------
        X_corrected : ndarray of shape (n_samples, n_features)
            Corrected spectral data.
        """
        X = check_array(X, copy=self.copy)
        X_corrected = np.zeros_like(X)
        for i in range(X.shape[0]):
            # Fit linear model: spectrum = slope * reference + intercept
            slope, intercept = np.polyfit(self.reference_, X[i], 1)
            # Correct spectrum
            X_corrected[i] = (X[i] - intercept) / slope
        return X_corrected


def create_model(config: Dict):
    return PLSRWrapper(config)