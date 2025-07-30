import os
import numpy as np
import pandas as pd
import cv2
from typing import Dict, List
from tqdm import tqdm
from joblib import Parallel, delayed
import multiprocessing

import torch
from torchvision import transforms
from transformers import ViTModel, ViTImageProcessor
import xgboost as xgb
from sklearn.multioutput import MultiOutputClassifier
from sklearn.decomposition import PCA

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class HybridModel:
    def __init__(self, config):
        self.config = config
        
        self.n_jobs = config.get("train", {}).get("n_jobs", 1)
        self.mlflow_info = config.get("mlflow_info", {})
        self.n_estimators = config.get("parameters", {}).get("n_estimators", 1)
        self.max_depth = config.get("parameters", {}).get("max_depth", None)
        self.min_samples_split = config.get("parameters", {}).get("min_samples_split", 2)
        self.random_state = config.get("parameters", {}).get("random_state", None)
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

        # Feature Extractor Backbone
        self.processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224-in21k')

        self.TS_path = config.get("TS_path", None)
        self.VS_path = config.get("VS_path", None)
        self.TS_label = config.get("TS_label", None)
        self.VS_label = config.get("VS_label", None)

        self.model = xgb.XGBClassifier(
            objective='binary:logistic',
            max_depth=6,
            learning_rate=0.1,
            n_estimators=100,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss',
            n_jobs=-1
        )
        self.model = MultiOutputClassifier(self.model)

        self.vit = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k").to(DEVICE)
        self.vit.eval()
    # 하나의 폴더 내에 _P로 시작하는 이미지들 path 불러온 뒤 여러 파장대들 묶어 하나의 tensor로 반환
    def load_stack(self, id_folder):
        band_files = sorted(os.listdir(id_folder), key=lambda x: int(x.split('_P')[-1].split('.')[0]))
        bands = []
        for f in band_files:
            img = cv2.imread(os.path.join(id_folder, f), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                bands.append(img.astype(np.float32))
        return np.stack(bands, axis=-1)  # (H, W, C)

    # 차원 축소 n -> 3(RGB)
    def apply_pca(self, stack_img):
        H, W, C = stack_img.shape
        flat = stack_img.reshape(-1, C)

        pca = PCA(n_components=3)
        reduced = pca.fit_transform(flat).reshape(H, W, 3)

        # 0 ~ 255 정규화
        reduced = (reduced - reduced.min()) / (reduced.max() - reduced.min() + 1e-6)
        return (reduced * 255).astype(np.uint8)

    def process_one(self, dir):
        stack = self.load_stack(dir)
        pca_img = self.apply_pca(stack)
        tensor = self.transform(pca_img)
        return tensor

    def process_all(self, dir : str) -> List[torch.Tensor]:
        folders = [os.path.join(dir, d) for d in sorted(os.listdir(dir)) if os.path.isdir(os.path.join(dir, d))]

        results = Parallel(n_jobs=self.n_jobs, prefer="threads")(delayed(self.process_one)(f) for f in folders)
        return results
    
    
    # 이미지 추출
    def extract_features(self, model, images):
        np_imgs = [img.mul(255).byte().permute(1, 2, 0).cpu().numpy()
                for img in images]

        # 2) processor 가 resize/normalize 까지 수행, 배치 텐서 반환
        inputs = self.processor(images=np_imgs, return_tensors="pt")
        pixel_values = inputs["pixel_values"].to(DEVICE)   # (N,3,224,224)

        # 3) ViT 추론 (batch 처리)
        with torch.no_grad():
            cls = self.vit(pixel_values=pixel_values).last_hidden_state[:, 0, :]  # (N,D)

        return cls.cpu().numpy()

    def load_labels(self, csv_path : str) -> np.ndarray:
        df = pd.read_csv(csv_path)
        label_cols = [c for c in df.columns if c.startswith("disease_")]
        return df[label_cols].values    # shape = (N, L)

    def fit(self, X, y):
        train_list = self.process_all(self.TS_path)
        #val_list = self.process_all(self.VS_path)
        vit_features_train = self.extract_features(self.vit, train_list)
        #vit_features_val = self.extract_features(self.vit, val_list)

        X_train = vit_features_train
        y_train = np.array(self.load_labels(self.TS_label))
        return self.model.fit(X_train, y_train)

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

    def predict(self, X):
        return self.model.predict(X)

def create_model(config: Dict):
    """RandomForest 모델 생성 함수"""
    return HybridModel(config)