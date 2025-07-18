from sklearn.metrics import r2_score, mean_squared_error
from sklearn.cross_decomposition import PLSRegression
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score
import joblib
import os
from PIL import Image
import pandas as pd

# https://resonon.com/content/files/1416-4041-1-PB.pdf
# 실행: python HSI_PLSR.py

# 현재의 파이프라인에서는 실행 불가, 별도의 train 스크립트가 필요
# 논문의 mean_spectrum 구하는 함수
# 각 객체별 5개의 밴드 별 평균값을 구하는 함수
def extract_mean_spectrum(folder_path):
    """
    폴더 내의 모든 이미지 파일에서 밴드별 평균 스펙트럼을 계산합니다.
    
    Args:
        folder_path: 이미지 파일들이 있는 폴더 경로
    Returns:
        mean_spectrum: 각 밴드별 평균값을 담은 리스트
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    band_images = sorted([
        os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.png')
        ])
    band_arrays = []
    for img_path in band_images:
        img = Image.open(img_path).convert('L')  # 흑백 이미지로 변환
        band_arrays.append(np.array(img, dtype=np.float32))
    cube = np.stack(band_arrays, axis=-1)  # (H, W, num_bands)
    mean_spectrum = np.mean(cube, axis=(0, 1))  # 각 밴드별 평균값 계산
    return mean_spectrum

def image_to_tensor(folder_root, id_list):
    X = []
    for sample_id in id_list:
        folder_path = os.path.join(folder_root, sample_id)
        spectrum = extract_mean_spectrum(folder_path)
        X.append(spectrum)
    return np.array(X)  # shape: (n_samples, B)

def HSI_PLSR(X_train, Y_train, n_components):
    """
    Perform Partial Least Squares Regression (PLSR) on hyperspectral data.

    Returns:
    pls_model : PLSRegression
        The fitted PLS regression model.
    """
    pls_model = PLSRegression(n_components=n_components)
    pls_model.fit(X_train, Y_train)
    return pls_model

# Function to optimize the number of components based on cross-validation
def optimize_n_components(X_train, Y_train, max_components=6):
    best_score = -np.inf
    best_n_components = 1

    for n_components in range(1, max_components + 1):
        pls_model = HSI_PLSR(X_train, Y_train, n_components)
        scores = cross_val_score(pls_model, X_train, Y_train, cv=5, scoring='r2')
        mean_score = np.mean(scores)

        if mean_score > best_score:
            best_score = mean_score
            best_n_components = n_components

    print(f'Best number of components: {best_n_components}')
    return best_n_components

# data loading functions
# 파일 경로 수정 필요
# 현재는 감자 대가리 로컬 path 사용 중임
def load_train_data():
    folder_root = 'dataset/TS_image'
    label_path = 'dataset/2025_넙치/Training/TS_label.csv'

    df = pd.read_csv(label_path)
    # 라벨 데이터 로드
    Y_train = df.iloc[:, 1:].values  # 첫 번째 열은 ID, 나머지는 라벨

    # 폴더명 추출
    id_list = sorted(os.listdir(folder_root))  # ['0001_R01C1', '0002_R01C1', ...]
    X_train_vectorized = image_to_tensor(folder_root, id_list)

    return X_train_vectorized, Y_train

def load_val_data():
    folder_root = 'dataset/VS_image'
    label_path = 'dataset/2025_넙치/Validation/VS_label.csv'

    df = pd.read_csv(label_path)
    # 라벨 데이터 로드
    Y_val = df.iloc[:, 1:].values  # 첫 번째 열은 ID, 나머지는 라벨

    id_list = sorted(os.listdir(folder_root))  # ['0001_R01C1', '0002_R01C1', ...]
    X_val_vectorized = image_to_tensor(folder_root, id_list)

    return X_val_vectorized, Y_val

# main function to run the PLSR model
def main():
    # 넙치 데이터
    """
    입력 넙치 데이터 수 -> 학습 3414개, 검증 427개
    input: 넙치의 분광 이미지, band수 5개
    output: 질병 label 13개에 대한 true, false 값
    """

    # load training and validation data
    X_train, Y_train = load_train_data()
    X_val, Y_val = load_val_data()

    # optimize the number of components and fit the PLSR model
    # default max_components is set to 6
    best_n_components = optimize_n_components(X_train, Y_train, max_components=6)
    pls_model = HSI_PLSR(X_train, Y_train, best_n_components)

    # Predict using the model
    Y_pred = pls_model.predict(X_val)

    # print the r2 score
    r2_scores = r2_score(Y_val, Y_pred, multioutput='raw_values')
    for i, score in enumerate(r2_scores):
        print(f'Label {i} R² Score: {score:.4f}')
    print(f'Overall R² Score: {np.mean(r2_scores):.4f}')

    # print mean squared error
    mse = mean_squared_error(Y_val, Y_pred)
    print(f'Mean Squared Error: {mse:.4f}')

    # Plotting the results
    for i in range(Y_val.shape[1]):
        label_idx = i
        plt.scatter(Y_val[:, label_idx], Y_pred[:, label_idx], alpha=0.7)
        plt.plot([0, 1], [0, 1], 'r--')  # 대각선 기준선
        plt.xlabel(f'True Values (Label {label_idx})')
        plt.ylabel('Predicted Values')
        plt.title(f'PLSR Predictions vs True (Label {label_idx})')
        plt.grid(True)
        plt.show()

    # model 저장을 원할 경우 아래 코드 주석 해제후 사용
    # joblib.dump(pls_model, 'plsr_model.pkl')

if __name__ == "__main__":
    main()

# 만약 별도의 train 스크립트를 구성한다면, 아래와 같습니다.
# python train_PLSR.py --config configs/plsr_config.json

"""
import argparse
import json
import pandas as pd
import numpy as np
import os
from utils.plsr_utils import extract_mean_spectrum, image_to_tensor, optimize_n_components, HSI_PLSR
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt

def load_column_config(path):
    with open(path) as f:
        return json.load(f)

def load_data(image_dir, label_csv, column_config):
    df = pd.read_csv(label_csv)
    id_list = sorted(os.listdir(image_dir))
    label_columns = column_config["label_columns"]
    Y = df[label_columns].values
    X = image_to_tensor(image_dir, id_list)
    return X, Y

def main(config_path):
    with open(config_path) as f:
        config = json.load(f)

    data_cfg = config["data"]
    plsr_cfg = config["plsr"]
    column_config = load_column_config(data_cfg["column_config"])

    # Load data
    X_train, Y_train = load_data(data_cfg["train_image_dir"], data_cfg["train_label_csv"], column_config)
    X_val, Y_val = load_data(data_cfg["val_image_dir"], data_cfg["val_label_csv"], column_config)

    # Train
    best_n = optimize_n_components(X_train, Y_train, max_components=plsr_cfg["max_components"])
    model = HSI_PLSR(X_train, Y_train, best_n)
    Y_pred = model.predict(X_val)

    # Evaluate
    r2_scores = r2_score(Y_val, Y_pred, multioutput='raw_values')
    mse = mean_squared_error(Y_val, Y_pred)

    for i, score in enumerate(r2_scores):
        print(f"Label {i} R²: {score:.4f}")
    print(f"Overall R²: {np.mean(r2_scores):.4f}")
    print(f"MSE: {mse:.4f}")

    # Optional Save
    if "save_model_path" in plsr_cfg:
        import joblib
        os.makedirs(os.path.dirname(plsr_cfg["save_model_path"]), exist_ok=True)
        joblib.dump(model, plsr_cfg["save_model_path"])

    # Optional Visualization
    for i in range(Y_val.shape[1]):
        plt.scatter(Y_val[:, i], Y_pred[:, i], alpha=0.7)
        plt.plot([0, 1], [0, 1], 'r--')
        plt.xlabel(f'True Label {i}')
        plt.ylabel('Prediction')
        plt.title(f'PLSR Label {i}')
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    main(args.config)

"""