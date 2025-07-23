import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import pandas as pd
import numpy as np
import os
from torchvision import transforms
from typing import Dict
import cv2
from sklearn.decomposition import PCA
from tqdm import tqdm
import torch
from transformers import ViTModel, ViTFeatureExtractor
from joblib import Parallel, delayed
import multiprocessing

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class HybridModel:
    def __init__(self, config):
        self.config = config

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
        reduced = pca.fit_transform(flat)
        reduced_img = reduced.reshape(H, W, 3)
        reduced_img -= reduced_img.min()
        reduced_img /= reduced_img.max()
        reduced_img *= 255
        return reduced_img.astype(np.uint8)

    # 병렬화를 위한 작업 단일화
    def process_single_folder(self, folder_path):
        stack = self.load_stack(folder_path)
        pca_img = self.apply_pca(stack)
        tensor = self.transform(pca_img)
        return tensor

    def process_all(self, dir):
        tensor_list = []
        folder_paths = [os.path.join(dir, f) for f in sorted(os.listdir(dir)) if os.path.isdir(os.path.join(dir, f))]
        n_jobs = min(len(folder_paths), multiprocessing.cpu_count())
        tensor_list = Parallel(n_jobs=n_jobs)(
            delayed(self.process_single_folder)(folder_path) for folder_path in folder_paths
        )
        return tensor_list
    
    # 이미지 추출
    def extract_vit_features(model, images):
        features = []
        with torch.no.grad():
            for img in tqdm(images):
                img = img.unsqueeze(0).to(DEVICE)
                outputs = model(pixel_values=imag)['last_hidden_state'][:, 0, :]
                features.append(outputs.squeeze(0).cpu().numpy())
        return np.array(features)

    def load_labels(self, file_path):
        df_list = []
        df = pd.read_csv(file_path)
        label_cols = [col for col in df.columns if col.startswith('disease_')]
        for label in label_cols:
            df_list.append(df[label].values)
        return df_list

    def fit(self, X, y):
        train_list = self.process_all(self.TS_path)
        val_list = self.process_all(self.VS_path)
        vit_model = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k').to(DEVICE)
        vit_model.eval()
        vit_features_train = self.extract_vit_features(vit_model, train_list)
        vit_features_val = self.extract_vit_features(vit_model, val_list)

        X_train, X_test = vit_features_train, vit_features_val
        y_train = np.array(self.load_labels(slef.TS_label))
        return self.model.fit(X_train, y_train)
    
    def predict(self, X):
        return self.model.predict(X)

def create_model(config: Dict):
    """RandomForest 모델 생성 함수"""
    return HybridModel(config)