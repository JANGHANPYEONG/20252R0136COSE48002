import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error

class RandomFrogModel:
    def __init__(self, config):
        train_config = config.get("training", config)
        self.n_iterations = train_config.get('n_iter', 1000)
        self.Q = train_config.get('n_subset', 6)
        self.resample_factor = train_config.get('resample_factor', 10)
        self.pls_n_components = train_config.get('pls_n_components', 4)
        self.topk = train_config.get('target_bands', 10)
        self.seed = train_config.get('seed', 42)
        np.random.seed(self.seed)

    def select_bands_with_scores(self, spectral_data, labels, pre_selected_bands, target_bands):
        """
        spectral_data: (N, D)
        labels: (N, )
        pre_selected_bands: 전처리된 feature 인덱스 or None
        target_bands: 최종 선택할 밴드 개수(Top-K)
        """
        X = spectral_data
        y = labels
        if pre_selected_bands is not None and len(pre_selected_bands) > 0:
            X = X[:, pre_selected_bands]
        else:
            pre_selected_bands = list(range(X.shape[1]))
        
        n_features = X.shape[1]
        feature_count = np.zeros(n_features, dtype=int)
        
        for _ in range(self.n_iterations):
            feature_list = []
            for _ in range(self.Q):
                cnt = np.random.randint(4, 6)
                current_subset = np.random.choice(n_features, cnt, replace=False)
                for _ in range(self.resample_factor):
                    new_subset = self.replace_factors(current_subset, n_features, n_keep=3)
                    if self.pls_rmse(X[:, new_subset], y) < self.pls_rmse(X[:, current_subset], y):
                        current_subset = new_subset
                feature_list += current_subset.tolist()
            feature_list = list(set(feature_list))
            for idx in feature_list:
                feature_count[idx] += 1

        # 선택 비율, 상위 target_bands만 선택
        selection_ratio = feature_count / self.n_iterations
        top_indices = np.argsort(selection_ratio)[-target_bands:][::-1]  # 내림차순
        # 파이프라인 요구에 따라 반드시 "원본 feature 인덱스"로 변환
        selected_bands = [pre_selected_bands[i] for i in top_indices]
        selected_scores = selection_ratio[top_indices]
        return selected_bands, selected_scores.tolist()

    @staticmethod
    def replace_factors(subset, n_features, n_keep=3):
        subset = np.array(subset)
        k = len(subset)
        keep_indices = np.random.choice(subset, n_keep, replace=False)
        available_indices = list(set(range(n_features)) - set(keep_indices))
        n_replace = k - n_keep
        new_indices = np.random.choice(available_indices, n_replace, replace=False)
        return np.concatenate((keep_indices, new_indices))

    def pls_rmse(self, X, y):
        # RMSE 계산 (적절한 n_components)
        n_comp = min(self.pls_n_components, X.shape[1], X.shape[0]-1)
        pls = PLSRegression(n_components=n_comp)
        pls.fit(X, y)
        y_pred = pls.predict(X)
        return np.sqrt(mean_squared_error(y, y_pred))

def create_model(model_name, config):
    if model_name == "random_frog":
        return RandomFrogModel(config)
    else:
        raise ValueError(f"Unknown model: {model_name}")
