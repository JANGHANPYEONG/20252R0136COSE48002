#!/usr/bin/env python3
"""
KDE 성능 저하 원인 분석 스크립트
"""

import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import json

def analyze_kde_effectiveness():
    """KDE 특성의 효과성 분석"""
    print("=" * 60)
    print("KDE 성능 저하 원인 분석")
    print("=" * 60)
    
    # 1. 고정 특성의 문제점 분석
    print("\n1. 고정 특성의 문제점:")
    print("   - 모든 샘플이 동일한 46차원 벡터를 받음")
    print("   - 개별 샘플의 특성을 구분할 수 없음")
    print("   - 단순히 상수(constant)가 모든 샘플에 더해지는 것과 동일")
    
    # 2. 차원 수 문제
    print("\n2. 차원 수 문제:")
    print("   - KDE 특성: 46차원")
    print("   - 이미지 특성: 256차원")
    print("   - 비율: 46/256 = 18%")
    print("   - 상대적으로 작은 KDE 정보가 큰 이미지 정보에 묻힐 가능성")
    
    # 3. 융합 방식 문제
    print("\n3. 융합 방식 문제:")
    print("   - 현재: 단순 concatenation 후 MLP")
    print("   - 문제: 이미지 특성이 KDE 특성을 압도할 수 있음")
    print("   - 대안: Attention-based fusion, Gating mechanism 등")
    
    return True

def analyze_data_characteristics():
    """데이터 특성 분석"""
    print("\n4. 데이터 특성 분석:")
    
    # CSV 파일 로드
    csv_path = "../../../dataset/label_with_paths_3dim+rgb.csv"
    try:
        data = pd.read_csv(csv_path)
        print(f"   - 전체 샘플 수: {len(data)}")
        print(f"   - 훈련 샘플 수: ~113 (71%)")
        
        # 라벨 분포 분석
        label_columns = ['Marbling', 'Meat Color', 'Texture', 'Surface Moisture', 'Total']
        
        print("\n   라벨 분포 특성:")
        for col in label_columns:
            if col in data.columns:
                values = pd.to_numeric(data[col], errors='coerce').dropna()
                print(f"   - {col}: 범위=[{values.min():.1f}, {values.max():.1f}], "
                      f"표준편차={values.std():.3f}, 변동계수={values.std()/values.mean():.3f}")
        
        # 분포의 다양성 확인
        print("\n   분포 다양성 분석:")
        all_values = []
        for col in label_columns:
            if col in data.columns:
                values = pd.to_numeric(data[col], errors='coerce').dropna()
                all_values.extend(values.tolist())
        
        if all_values:
            all_values = np.array(all_values)
            unique_ratio = len(np.unique(all_values)) / len(all_values)
            print(f"   - 전체 고유값 비율: {unique_ratio:.3f}")
            print(f"   - 정보 엔트로피가 {'높음' if unique_ratio > 0.5 else '낮음'}")
            
    except Exception as e:
        print(f"   데이터 로드 실패: {e}")

def identify_potential_solutions():
    """잠재적 해결책 제시"""
    print("\n5. 잠재적 해결책:")
    
    solutions = [
        {
            "문제": "고정 특성의 한계",
            "해결책": [
                "샘플별 상대적 위치 정보 추가 (예: 현재 샘플이 분포에서 어느 위치인지)",
                "라벨별 z-score 계산하여 개별 샘플 특성 반영",
                "현재 예측값과 분포 통계 간의 거리/유사도 계산"
            ]
        },
        {
            "문제": "차원 불균형",
            "해결책": [
                "KDE 특성 차원 확장 (46 → 128 또는 256)",
                "이미지 특성 압축 (256 → 128)",
                "가중치 기반 융합 (KDE에 더 큰 가중치)"
            ]
        },
        {
            "문제": "융합 방식의 한계",
            "해결책": [
                "Cross-attention 메커니즘 도입",
                "Gating network로 특성 중요도 학습",
                "FiLM (Feature-wise Linear Modulation) 적용"
            ]
        },
        {
            "문제": "정보 가치 부족",
            "해결책": [
                "더 의미있는 통계 특성 추가 (왜도, 첨도, 모드 등)",
                "라벨 간 상관관계 정보",
                "클러스터링 기반 그룹 정보"
            ]
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"\n   {i}) {solution['문제']}:")
        for j, sol in enumerate(solution['해결책'], 1):
            print(f"      {j}. {sol}")

def recommend_immediate_fixes():
    """즉시 적용 가능한 개선안"""
    print("\n" + "=" * 60)
    print("즉시 적용 가능한 개선안 (우선순위 순)")
    print("=" * 60)
    
    fixes = [
        {
            "제목": "1. 샘플별 상대적 위치 정보 추가",
            "설명": "고정 분포 통계 + 현재 샘플의 상대적 위치",
            "구현": "현재 라벨값을 분포 통계와 비교하여 z-score, percentile 등 계산",
            "예상효과": "높음 - 개별 샘플 구분 가능",
            "구현난이도": "낮음"
        },
        {
            "제목": "2. KDE 특성 차원 확장",
            "설명": "46차원 → 128차원으로 확장",
            "구현": "더 많은 통계 정보 추가 (왜도, 첨도, 다중 percentile 등)",
            "예상효과": "중간 - 이미지 특성과 균형",
            "구현난이도": "중간"
        },
        {
            "제목": "3. Gated Fusion 도입",
            "설명": "이미지와 KDE 특성의 가중치를 학습",
            "구현": "Gating network로 특성별 중요도 동적 조절",
            "예상효과": "중간 - 더 나은 융합",
            "구현난이도": "중간"
        },
        {
            "제목": "4. KDE 특성 정규화",
            "설명": "KDE 특성을 이미지 특성과 동일한 스케일로 정규화",
            "구현": "StandardScaler 또는 MinMaxScaler 적용",
            "예상효과": "낮음 - 스케일 문제 해결",
            "구현난이도": "낮음"
        }
    ]
    
    for fix in fixes:
        print(f"\n{fix['제목']}")
        print(f"   설명: {fix['설명']}")
        print(f"   구현: {fix['구현']}")
        print(f"   예상효과: {fix['예상효과']}")
        print(f"   구현난이도: {fix['구현난이도']}")

if __name__ == "__main__":
    analyze_kde_effectiveness()
    analyze_data_characteristics()
    identify_potential_solutions()
    recommend_immediate_fixes()
    
    print("\n" + "=" * 60)
    print("결론: KDE가 현재 성능 향상에 기여하지 못하는 주된 이유는")
    print("모든 샘플에 동일한 고정 특성을 제공하여 개별 샘플 구분이")
    print("불가능하기 때문입니다. 가장 효과적인 개선은 샘플별 상대적")
    print("위치 정보를 추가하는 것입니다.")
    print("=" * 60)