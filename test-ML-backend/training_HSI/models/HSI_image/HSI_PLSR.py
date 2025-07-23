from sklearn.metrics import r2_score, mean_squared_error
from sklearn.cross_decomposition import PLSRegression
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score
import joblib
import os
from PIL import Image
import pandas as pd

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
    # print("call extract_mean_spectrum")
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
    print("call image_to_tensor")
    X = []
    for sample_id in id_list:
        folder_path = os.path.join(folder_root, sample_id)
        spectrum = extract_mean_spectrum(folder_path)
        X.append(spectrum)
    return np.array(X)  # shape: (n_samples, B)

def HSI_PLSR(X_train, Y_train, n_components):
    """
    Perform Partial Least Squares Regression (PLSR) on hyperspectral data.

    Parameters:
    X : array-like, shape (n_samples, n_features)
        The input data (hyperspectral features).
    Y : array-like, shape (n_samples, n_targets)
        The target data.
    n_components : int
        The number of components to use in PLSR.

    Returns:
    pls_model : PLSRegression
        The fitted PLS regression model.
    """
    print("call HSI_PLSR")
    pls_model = PLSRegression(n_components=n_components)
    pls_model.fit(X_train, Y_train)
    return pls_model

# Function to optimize the number of components based on cross-validation
def optimize_n_components(X_train, Y_train, max_components=5):
    print("call optimize_n_components")
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
"""
def load_train_data():
    print("call load_train_data")
    folder_root = 'dataset/TS_image'
    label_path = 'dataset/2025/Training/TS_label.csv'

    df = pd.read_csv(label_path)
    # 라벨 데이터 로드
    Y_train = df.iloc[:, 1:].values  # 첫 번째 열은 ID, 나머지는 라벨

    # 폴더명 추출
    id_list = sorted(os.listdir(folder_root))  # ['0001_R01C1', '0002_R01C1', ...]
    X_train_vectorized = image_to_tensor(folder_root, id_list)

    return X_train_vectorized, Y_train
"""
def load_train_data():
    folder_root = 'dataset/TS_image'
    label_path = 'dataset/2025/Training/TS_label.csv'

    df = pd.read_csv(label_path)
    id_list = df.iloc[:, 0].tolist()  # CSV의 첫 번째 열 = sample ID
    Y_train = df.iloc[:, 1:14].values   # 라벨 부분만

    # 이미지 폴더 이름들과 CSV ID가 일치하는지 확인
    image_folders = set(os.listdir(folder_root))
    missing_folders = [id for id in id_list if id not in image_folders]
    if missing_folders:
        print("다음 ID에 해당하는 이미지 폴더가 없습니다:", missing_folders)

    # image_to_tensor 함수는 주어진 ID 순서대로 불러옴
    X_train_vectorized = image_to_tensor(folder_root, id_list)

    return X_train_vectorized, Y_train


def load_val_data():
    print("call load_val_data")
    folder_root = 'dataset/2025/Validation/VS_image/VS_image'
    label_path = 'dataset/2025/Validation/VS_label.csv'

    df = pd.read_csv(label_path)
    # 라벨 데이터 로드
    Y_val = df.iloc[:, 1:14].values  # 첫 번째 열은 ID, 나머지는 라벨

    id_list = sorted(os.listdir(folder_root))  # ['0001_R01C1', '0002_R01C1', ...]
    X_val_vectorized = image_to_tensor(folder_root, id_list)

    return X_val_vectorized, Y_val

# main function to run the PLSR model
def main():
    print("[main] model start")
    # 넙치 데이터
    """
    입력 넙치 데이터 수 -> 학습 3414개, 검증 427개
    input: 넙치의 분광 이미지, band수 5개
    output: 질병 label 13개에 대한 true, false 값
    """

    # load training and validation data
    print("[main] load data")
    X_train, Y_train = load_train_data()
    X_val, Y_val = load_val_data()

    # optimize the number of components and fit the PLSR model
    # default max_components is set to 5
    print("[main] optimize n_components")
    best_n_components = optimize_n_components(X_train, Y_train, max_components=5)
    pls_model = HSI_PLSR(X_train, Y_train, best_n_components)

    # Predict using the model
    print("[main] predict")
    Y_pred = pls_model.predict(X_val)

    # print the r2 score
    print("[main] evaluate model")
    r2_scores = r2_score(Y_val, Y_pred, multioutput='raw_values')
    for i, score in enumerate(r2_scores):
        print(f'Label {i} R² Score: {score:.4f}')


    # print mean squared error
    print("[main] evaluate model")
    mse = mean_squared_error(Y_val, Y_pred)
    print(f'Mean Squared Error: {mse:.4f}')

    # Plotting the results
    """
    print("[main] plot results")
    for i in range(Y_val.shape[1]):
        label_idx = i
        plt.scatter(Y_val[:, label_idx], Y_pred[:, label_idx], alpha=0.7)
        plt.plot([0, 1], [0, 1], 'r--')  # 대각선 기준선
        plt.xlabel(f'True Values (Label {label_idx})')
        plt.ylabel('Predicted Values')
        plt.title(f'PLSR Predictions vs True (Label {label_idx})')
        plt.grid(True)
        plt.show()
    """
    # Save the model
    # joblib.dump(pls_model, 'plsr_model.pkl')

    return pls_model

if __name__ == "__main__":
    main()