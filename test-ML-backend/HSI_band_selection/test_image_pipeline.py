#!/usr/bin/env python3
"""
HSI 이미지 파이프라인 테스트 스크립트
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from PIL import Image
import torch
from torch.utils.data import DataLoader

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.dataset import load_image_data, split_image_data
from utils.column_info import load_column_config, get_csv_structure
from models.training.hsi_cnn_model import create_model

def create_test_data():
    """테스트용 데이터를 생성합니다."""
    print("Creating test data...")
    
    # 테스트 디렉토리 생성
    test_dir = "test_data"
    image_dir = os.path.join(test_dir, "images")
    os.makedirs(image_dir, exist_ok=True)
    
    # 테스트 이미지 생성 (5개 밴드, 64x64 크기)
    num_samples = 10
    num_bands = 5
    image_size = (64, 64)
    
    # 각 밴드별로 테스트 이미지 생성
    for band_idx in range(num_bands):
        for sample_idx in range(num_samples):
            # 랜덤 그레이스케일 이미지 생성
            image_array = np.random.randint(0, 256, image_size, dtype=np.uint8)
            image = Image.fromarray(image_array, mode='L')
            
            # 이미지 저장
            image_path = os.path.join(image_dir, f"sample_{sample_idx:03d}_band_{band_idx}.png")
            image.save(image_path)
    
    # CSV 데이터 생성
    data = []
    for sample_idx in range(num_samples):
        row = [f"sample_{sample_idx:03d}"]  # ID
        
        # 라벨 (13개 클래스, 랜덤)
        labels = np.random.randint(0, 2, 13)
        row.extend(labels)
        
        # 벡터 데이터 (5개 밴드, 랜덤)
        vectors = np.random.uniform(100, 200, 5)
        row.extend(vectors)
        
        # 이미지 경로
        for band_idx in range(num_bands):
            image_path = os.path.join(image_dir, f"sample_{sample_idx:03d}_band_{band_idx}.png")
            row.append(image_path)
        
        data.append(row)
    
    # 컬럼명 생성
    columns = ["ID"]
    columns.extend([f"disease_{i+1}" for i in range(13)])
    columns.extend([f"band_{10 + i*10}" for i in range(5)])
    columns.extend([f"band_{10 + i*10}_path" for i in range(5)])
    
    # DataFrame 생성 및 저장
    df = pd.DataFrame(data, columns=columns)
    csv_path = os.path.join(test_dir, "test_label.csv")
    df.to_csv(csv_path, index=False)
    
    print(f"Test data created in {test_dir}/")
    print(f"CSV file: {csv_path}")
    print(f"Images: {image_dir}/")
    
    return csv_path

def test_column_config():
    """컬럼 설정을 테스트합니다."""
    print("\nTesting column configuration...")
    
    try:
        config = load_column_config()
        structure = get_csv_structure()
        
        print("Column config loaded successfully:")
        print(f"  ID column index: {structure['id_column_index']}")
        print(f"  Label columns: {len(structure['label_columns'])}")
        print(f"  Spectral bands: {len(structure['spectral_columns'])}")
        
        if "image_path_start_index" in structure:
            print(f"  Image path start index: {structure['image_path_start_index']}")
            print(f"  Image path columns: {len(structure['image_path_columns'])}")
        
        if "image_size" in structure:
            print(f"  Image size: {structure['image_size']}")
        
        return True
    except Exception as e:
        print(f"Error loading column config: {e}")
        return False

def test_dataset_loading(csv_path):
    """데이터셋 로딩을 테스트합니다."""
    print("\nTesting dataset loading...")
    
    try:
        # 설정 파일 생성
        config = {
            "wavelengths": [10, 20, 30, 40, 50],
            "label_columns": [f"disease_{i+1}" for i in range(13)],
            "image_size": [64, 64]
        }
        
        # 이미지 데이터셋 로드
        dataset = load_image_data(csv_path, config)
        
        print(f"Dataset loaded successfully:")
        print(f"  Number of samples: {len(dataset)}")
        print(f"  Number of bands: {len(dataset.image_paths[0]) if dataset.image_paths else 0}")
        print(f"  Number of labels: {len(dataset.labels[0]) if len(dataset.labels) > 0 else 0}")
        print(f"  Image size: {dataset.image_size}")
        
        # 첫 번째 샘플 로드 테스트
        if len(dataset) > 0:
            images, labels, sample_id = dataset[0]
            print(f"  First sample:")
            print(f"    Sample ID: {sample_id}")
            print(f"    Images shape: {images.shape}")
            print(f"    Labels shape: {labels.shape}")
            print(f"    Labels: {labels.numpy()}")
        
        return True
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return False

def test_model_creation():
    """모델 생성을 테스트합니다."""
    print("\nTesting model creation...")
    
    try:
        config = {
            "wavelengths": [10, 20, 30, 40, 50],
            "label_columns": [f"disease_{i+1}" for i in range(13)],
            "image_size": [64, 64]
        }
        
        # HSICNN 모델 생성
        model = create_model("hsi_cnn", config)
        
        print(f"Model created successfully:")
        print(f"  Model type: {type(model).__name__}")
        print(f"  Number of parameters: {sum(p.numel() for p in model.parameters())}")
        
        # 더미 입력으로 forward pass 테스트
        batch_size = 2
        num_bands = len(config["wavelengths"])
        image_size = config["image_size"]
        
        dummy_input = torch.randn(batch_size, num_bands, image_size[0], image_size[1])
        output = model(dummy_input)
        
        print(f"  Input shape: {dummy_input.shape}")
        print(f"  Output shape: {output.shape}")
        print(f"  Output range: [{output.min().item():.4f}, {output.max().item():.4f}]")
        
        return True
    except Exception as e:
        print(f"Error creating model: {e}")
        return False

def test_data_loader(csv_path):
    """데이터 로더를 테스트합니다."""
    print("\nTesting data loader...")
    
    try:
        config = {
            "wavelengths": [10, 20, 30, 40, 50],
            "label_columns": [f"disease_{i+1}" for i in range(13)],
            "image_size": [64, 64]
        }
        
        # 데이터셋 로드
        dataset = load_image_data(csv_path, config)
        
        # 데이터 로더 생성
        batch_size = 2
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        print(f"DataLoader created successfully:")
        print(f"  Number of batches: {len(dataloader)}")
        
        # 첫 번째 배치 로드
        for batch_idx, (images, labels, sample_ids) in enumerate(dataloader):
            print(f"  Batch {batch_idx}:")
            print(f"    Images shape: {images.shape}")
            print(f"    Labels shape: {labels.shape}")
            print(f"    Sample IDs: {sample_ids}")
            break
        
        return True
    except Exception as e:
        print(f"Error creating data loader: {e}")
        return False

def cleanup_test_data():
    """테스트 데이터를 정리합니다."""
    import shutil
    
    test_dir = "test_data"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"\nCleaned up test data: {test_dir}")

def main():
    """메인 테스트 함수"""
    print("HSI Image Pipeline Test")
    print("=" * 50)
    
    # 테스트 데이터 생성
    csv_path = create_test_data()
    
    # 각 테스트 실행
    tests = [
        ("Column Configuration", lambda: test_column_config()),
        ("Dataset Loading", lambda: test_dataset_loading(csv_path)),
        ("Model Creation", lambda: test_model_creation()),
        ("Data Loader", lambda: test_data_loader(csv_path))
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print(f"\n{'='*50}")
    print("Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    # 테스트 데이터 정리
    cleanup_test_data()
    
    if passed == len(results):
        print("\n🎉 All tests passed! The HSI image pipeline is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main()) 