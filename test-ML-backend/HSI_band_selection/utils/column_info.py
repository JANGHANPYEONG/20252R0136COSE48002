import json
import os

# CSV 컬럼 순서 정보
# 첫 번째 컬럼: 개체 ID
# 2~k번째 컬럼: 정답 라벨들
# k+1번째 컬럼부터: 반사율 벡터 데이터
# 마지막: 이미지 경로들

def load_column_config():
    """컬럼 설정을 JSON 파일에서 로드합니다."""
    config_path = "../training_HSI/configs/column_config.json"
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Column config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config

def get_spectral_columns():
    """반사율 벡터 컬럼명들을 column_config.json에서 로드합니다."""
    try:
        column_config = load_column_config()
        wavelengths = column_config["wavelengths"]
        return [f"band_{wavelength}" for wavelength in wavelengths]
    except (FileNotFoundError, KeyError) as e:
        print(f"Warning: Error loading wavelengths from column_config.json: {e}")
        # 기본값 (600nm부터 730nm까지 10nm 간격)
        wavelengths = list(range(600, 731, 10))
        return [f"reflectance_{wavelength}" for wavelength in wavelengths]

def get_image_path_columns():
    """이미지 경로 컬럼명들을 column_config.json에서 로드합니다."""
    try:
        column_config = load_column_config()
        wavelengths = column_config["wavelengths"]
        return [f"band_{wavelength}_path" for wavelength in wavelengths]
    except (FileNotFoundError, KeyError) as e:
        print(f"Warning: Error loading image path columns from column_config.json: {e}")
        return []

def get_csv_structure():
    """CSV의 전체 컬럼 구조를 반환합니다."""
    column_config = load_column_config()
    spectral_cols = get_spectral_columns()
    image_path_cols = get_image_path_columns()
    
    structure = {
        "id_column_index": column_config["column_order"]["id_column_index"],
        "label_start_index": column_config["column_order"]["label_start_index"],
        "vector_start_index": column_config["column_order"]["vector_start_index"],
        "image_path_start_index": column_config["column_order"]["image_path_start_index"],
        "label_columns": column_config["label_columns"],
        "spectral_columns": spectral_cols,
        "image_path_columns": image_path_cols,
        "total_columns": ["id"] + column_config["label_columns"] + spectral_cols + image_path_cols
    }
    
    # 이미지 크기 정보 추가
    if "image_size" in column_config:
        structure["image_size"] = column_config["image_size"]
    
    return structure

def get_column_by_index(data, index):
    """인덱스로 컬럼 데이터를 가져옵니다."""
    return data.iloc[:, index]

def get_id_column(data):
    """ID 컬럼을 가져옵니다."""
    column_config = load_column_config()
    return get_column_by_index(data, column_config["column_order"]["id_column_index"])

def get_label_columns(data):
    """라벨 컬럼들을 가져옵니다."""
    column_config = load_column_config()
    start_idx = column_config["column_order"]["label_start_index"]
    end_idx = column_config["column_order"]["vector_start_index"]
    return data.iloc[:, start_idx:end_idx]

def get_vector_columns(data):
    """반사율 벡터 컬럼들을 가져옵니다."""
    column_config = load_column_config()
    start_idx = column_config["column_order"]["vector_start_index"]
    end_idx = column_config["column_order"]["image_path_start_index"]
    return data.iloc[:, start_idx:end_idx]

def get_image_path_columns_data(data):
    """이미지 경로 컬럼들을 가져옵니다."""
    column_config = load_column_config()
    start_idx = column_config["column_order"]["image_path_start_index"]
    return data.iloc[:, start_idx:]

# 설정 정보 출력
if __name__ == "__main__":
    structure = get_csv_structure()
    print("CSV Structure:")
    print(f"ID Column Index: {structure['id_column_index']}")
    print(f"Label Columns: {structure['label_columns']}")
    print(f"Label Start Index: {structure['label_start_index']}")
    print(f"Vector Start Index: {structure['vector_start_index']}")
    print(f"Image Path Start Index: {structure['image_path_start_index']}")
    print(f"Number of spectral bands: {len(structure['spectral_columns'])}")
    print(f"Number of image path columns: {len(structure['image_path_columns'])}")
    
    if "image_size" in structure:
        print(f"Image Size: {structure['image_size']}")
    
    print(f"Total columns: {len(structure['total_columns'])}") 