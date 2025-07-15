import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error
from joblib import Parallel, delayed
from tqdm import tqdm

class RandomFrogModel:
    def __init__(self, config):
        train_config = config.get("training", config)
        self.n_iterations = train_config.get('n_iter', 1000)
        self.Q = train_config.get('n_subset', 6)
        self.resample_factor = train_config.get('resample_factor', 10)
        self.subset_size = train_config.get('subset_size', 4)
        self.pls_n_components = train_config.get('pls_n_components', 2)
        self.topk = train_config.get('target_bands', 10)
        self.seed = train_config.get('seed', 42)
        self.n_jobs = train_config.get('n_jobs', 1)
        np.random.seed(self.seed)
    
    def _resammple_subset(self, n_features):
        # generate a random subset of features
        return np.random.choice(n_features, size=self.subset_size, replace=False)
    
    def _evaluate_subset(self, X, y, selected_bands):
        # PLS 모델을 사용하여 RMSE 계산
        pls = PLSRegression(n_components=self.pls_n_components)
        X_sub = X[:, selected_bands]
        pls.fit(X_sub, y)
        y_pred = pls.predict(X_sub)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        return selected_bands, rmse

    def select_bands_with_scores(self, spectral_data, labels, pre_selected_bands, target_bands):
        """
        spectral_data: (N, D)
        labels: (N, )
        pre_selected_bands: 전처리된 feature 인덱스 or None
        target_bands: 최종 선택할 밴드 개수(Top-K)
        """
        X = spectral_data if pre_selected_bands is None else spectral_data[:, pre_selected_bands]
        y = labels
       
        n_samples, n_features = X.shape
        feature_count = np.zeros(n_features, dtype=int)


        # 반복 횟수만큼 서브셋을 생성하고 평가
        for _ in tqdm(range(self.n_iterations)):
            best_subset = [None for _ in range(self.Q)]
            best_rmse = [float('inf') for _ in range(self.Q)]    
            # Q frogs
            frog_subsets = [self._resammple_subset(n_features) for _ in range(self.Q)]
            # parallel evaluation
            results = Parallel(n_jobs=self.n_jobs)(
                delayed(self._evaluate_subset)(X, y, subset) for subset in frog_subsets)

            for i, (subset, rmse) in enumerate(results):
                if rmse < best_rmse[i] :
                    best_rmse[i] = rmse
                    best_subset[i] = subset
            # frequency accumulation
            included_mask = np.zeros(n_features, dtype=bool)

            for subset in best_subset:
                included_mask[subset] = True  # NumPy fancy indexing

            # Step 2: mask가 True인 항목만 count = 1, 나머지 0
            feature_count += included_mask.astype(int)

        # 선택 비율, 상위 target_bands만 선택
        selection_ratio = feature_count / self.n_iterations

        # Z-score 정규화
        mean = np.mean(selection_ratio)
        std = np.std(selection_ratio)
        if std > 0:
            selection_ratio_norm = (selection_ratio - mean) / std
        else:
            selection_ratio_norm = selection_ratio - mean

        top_indices = np.argsort(selection_ratio_norm)[-target_bands:][::-1]  # 내림차순
        # 파이프라인 요구에 따라 반드시 "원본 feature 인덱스"로 변환
        selected_bands = [pre_selected_bands[i] for i in top_indices]
        selected_scores = selection_ratio_norm[top_indices]
        return selected_bands, selected_scores.tolist()

def create_model(model_name, config):
    if model_name == "random_frog":
        return RandomFrogModel(config)
    else:
        raise ValueError(f"Unknown model: {model_name}")
