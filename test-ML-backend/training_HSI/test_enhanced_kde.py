#!/usr/bin/env python3
"""
개선된 KDE 특성 테스트 스크립트
"""

import sys
sys.path.append('.')

import numpy as np
import pandas as pd
from utils.dataset_hsi import HSIDataset
from sklearn.model_selection import train_test_split

def test_enhanced_kde():
    """개선된 KDE 특성 테스트"""
    print("=" * 60)
    print("개선된 KDE 특성 테스트")
    print("=" * 60)
    
    # 데이터 로드 및 분할
    csv_path = "../../../dataset/label_with_paths_3dim+rgb.csv"
    column_config_path = "configs/column_config.json"
    
    # 임시로 전체 데이터 로드하여 인덱스 분할
    temp_data = pd.read_csv(csv_path)
    indices = list(range(len(temp_data)))
    train_indices, temp_indices = train_test_split(
        indices, test_size=0.3, random_state=42
    )
    val_indices, test_indices = train_test_split(
        temp_indices, test_size=0.5, random_state=42
    )
    
    print(f"Data split: Train={len(train_indices)}, Val={len(val_indices)}, Test={len(test_indices)}")
    
    # KDE 특성이 있는 데이터셋 생성
    dataset = HSIDataset(
        csv_path=csv_path,
        column_config_path=column_config_path,
        fit_scaler=True,
        scaler_mode="normalized",
        use_kde=True,
        train_indices=train_indices
    )
    
    # 특성 분석
    print("\n" + "=" * 40)
    print("KDE 특성 분석 결과")
    print("=" * 40)
    
    kde_array = np.array(dataset.kde_features)
    print(f"KDE 특성 배열 크기: {kde_array.shape}")
    
    # 샘플별 차이 확인
    variances = np.var(kde_array, axis=0)
    variable_features = np.sum(variances > 1e-6)
    fixed_features = np.sum(variances <= 1e-6)
    
    print(f"변동하는 특성 (샘플별 다름): {variable_features}")
    print(f"고정된 특성 (모든 샘플 동일): {fixed_features}")
    print(f"총 특성 수: {kde_array.shape[1]}")
    
    # 샘플별 차이 시각화
    print("\n샘플 간 KDE 특성 차이:")
    for i in range(min(5, len(dataset))):
        kde_sample = dataset.kde_features[i]
        # 상대적 위치 특성만 출력 (40~65번째 특성)
        relative_features = kde_sample[40:65]
        print(f"  샘플 {i}: 상대적 위치 특성 예시 = {relative_features[:5].round(3)}")
    
    # 특성 범위 확인
    print(f"\n특성 값 범위:")
    print(f"  최소값: {kde_array.min():.3f}")
    print(f"  최대값: {kde_array.max():.3f}")
    print(f"  평균: {kde_array.mean():.3f}")
    print(f"  표준편차: {kde_array.std():.3f}")
    
    # 성공 메시지
    if variable_features > 0:
        print("\n✅ 성공: 개선된 KDE가 샘플별로 다른 특성을 생성합니다!")
        print("   이제 각 샘플의 라벨이 전체 분포에서 어느 위치에 있는지")
        print("   모델이 이해할 수 있습니다.")
    else:
        print("\n❌ 실패: 여전히 모든 샘플이 동일한 특성을 가집니다.")
    
    return dataset

if __name__ == "__main__":
    try:
        dataset = test_enhanced_kde()
        print("\n" + "=" * 60)
        print("개선된 KDE 테스트 완료")
        print("=" * 60)
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()