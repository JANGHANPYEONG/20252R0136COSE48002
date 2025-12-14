#!/usr/bin/env python3
"""
마스크 사전계산 도구

이 스크립트는 RGB 이미지에서 세그멘테이션 마스크를 생성하고 저장합니다.
생성된 마스크는 PNG 파일로 저장되며, CSV 파일에 마스크 경로가 추가됩니다.

사용법:
    python tools/precompute_masks.py \
        --csv data/rgb/train.csv \
        --column-config configs/column_config.json \
        --out-csv data/rgb/train.masked.csv

"""

import os
import sys
import json
import argparse
import pandas as pd
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# (no online segmentation; dummy mask only)


def load_column_config(config_path: str) -> dict:
    """컬럼 설정 파일을 로드합니다."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Column config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)


def load_csv(csv_path: str) -> pd.DataFrame:
    """CSV 파일을 로드합니다."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    return pd.read_csv(csv_path)


def ensure_directory(directory: str):
    """디렉토리가 존재하지 않으면 생성합니다."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


def get_image_stem(image_path: str) -> str:
    """이미지 경로에서 파일명(확장자 제외)을 추출합니다."""
    return os.path.splitext(os.path.basename(image_path))[0]


def generate_mask_path(image_path: str, column_config: dict) -> str:
    """마스크 파일 경로를 생성합니다 (원본 하위 디렉토리 구조 항상 보존)."""
    base_img = column_config['base_dirs']['rgb_image_dir']
    base_mask = column_config['base_dirs']['rgb_mask_dir']
    
    # 항상 base_img 기준 상대 디렉토리를 구해 보존
    abs_img = image_path if os.path.isabs(image_path) else os.path.join(base_img, image_path)
    rel_dir = os.path.relpath(os.path.dirname(abs_img), base_img)
    # base_img 밖이면 안전하게 루트에 저장
    if rel_dir.startswith(os.pardir):  # '..'
        rel_dir = ""
    stem = get_image_stem(abs_img)
    
    mask_template = column_config.get('mask_template', '{stem}_mask.png')
    mask_filename = mask_template.format(stem=stem)
    return os.path.join(base_mask, rel_dir, mask_filename)


def create_dummy_mask(image_size: tuple, threshold: float = 0.5) -> np.ndarray:
    """
    더미 마스크를 생성합니다.
    
    Args:
        image_size: (width, height) 튜플
        threshold: 임계값
        
    Returns:
        np.ndarray: 더미 마스크 (0~1 범위)
    """
    mask = np.ones(image_size[::-1], dtype=np.float32)  # PIL은 (W, H), numpy는 (H, W)
    
    # 약간의 노이즈 추가 (실제 마스크와 비슷하게)
    noise = np.random.normal(0, 0.1, mask.shape)
    mask = np.clip(mask + noise, 0, 1)
    
    # 임계값 적용
    mask = (mask > threshold).astype(np.float32)
    
    return mask


def process_image(image_path: str, column_config: dict, 
                 seg_engine, threshold: float = 0.5, 
                 downscale: float = 1.0) -> tuple:
    """
    단일 이미지를 처리하여 마스크를 생성합니다.
    
    Args:
        image_path: 이미지 파일 경로
        column_config: 컬럼 설정
        seg_engine: 세그멘테이션 엔진
        threshold: 마스크 임계값
        downscale: 다운스케일 비율
        
    Returns:
        tuple: (마스크 경로, 마스크 생성 성공 여부)
    """
    try:
        # 이미지 로드
        if not os.path.exists(image_path):
            print(f"Warning: Image not found: {image_path}")
            return None, False
        
        image = Image.open(image_path).convert('RGB')
        
        # 다운스케일 적용
        if downscale != 1.0:
            new_size = (int(image.width * downscale), int(image.height * downscale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # 마스크 생성 (현재는 더미 마스크만 사용)
        mask = create_dummy_mask(image.size, threshold)
        
        # 마스크를 8bit PNG로 변환
        mask_8bit = (mask * 255).astype(np.uint8)
        mask_image = Image.fromarray(mask_8bit, mode='L')
        
        # 마스크 저장 경로 생성
        mask_path = generate_mask_path(image_path, column_config)
        
        # 디렉토리 생성
        mask_dir = os.path.dirname(mask_path)
        ensure_directory(mask_dir)
        
        # 마스크 저장
        mask_image.save(mask_path, 'PNG')
        
        # 상대경로로 반환
        base_dir = column_config['base_dirs']['rgb_mask_dir']
        relative_mask_path = os.path.relpath(mask_path, base_dir)
        
        return relative_mask_path, True
        
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None, False


def process_csv(csv_path: str, column_config: dict, out_csv: str = None,
                overwrite: bool = False, downscale: float = 1.0,
                threshold: float = 0.5) -> bool:
    """
    CSV 파일의 모든 이미지를 처리하여 마스크를 생성합니다.
    
    Args:
        csv_path: 입력 CSV 파일 경로
        column_config: 컬럼 설정
        out_csv: 출력 CSV 파일 경로 (None이면 입력 파일 덮어쓰기)
        overwrite: 기존 마스크 덮어쓰기 여부
        downscale: 다운스케일 비율
        threshold: 마스크 임계값
        
    Returns:
        bool: 성공 여부
    """
    print(f"Processing CSV: {csv_path}")
    print(f"Column config: {column_config}")
    print(f"Output CSV: {out_csv or csv_path}")
    print(f"Overwrite: {overwrite}")
    print(f"Downscale: {downscale}")
    print(f"Threshold: {threshold}")
    
    # CSV 로드
    df = load_csv(csv_path)
    print(f"Loaded {len(df)} rows from CSV")
    
    # 컬럼 인덱스 확인
    rgb_image_idx = column_config['column_order']['rgb_image_path_start_index']
    rgb_mask_idx = column_config['column_order']['rgb_mask_path_index']
    
    # 마스크 컬럼 보장 (안전한 인덱스 위치에 추가)
    if 'rgb_mask_path' not in df.columns:
        insert_at = min(rgb_mask_idx, len(df.columns))
        df.insert(insert_at, 'rgb_mask_path', '')
    
    # online segmentation 없음 (더미 마스크만 사용)
    seg_engine = None
    
    # RGB 이미지 기본 디렉토리
    rgb_base = column_config['base_dirs']['rgb_image_dir']
    
    # 각 이미지 처리
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"Processing {idx + 1}/{len(df)} images...")
        
        # 이미지 경로 처리 (상대경로를 절대경로로 변환)
        image_path = row.iloc[rgb_image_idx]
        if not os.path.isabs(image_path):
            image_path = os.path.join(rgb_base, image_path)
        
        current_mask_path = str(row['rgb_mask_path']) if 'rgb_mask_path' in df.columns else ''
        if current_mask_path and not overwrite:
            # 파일이 실제 존재할 때만 스킵
            abs_mask = current_mask_path if os.path.isabs(current_mask_path) \
                else os.path.join(column_config['base_dirs']['rgb_mask_dir'], current_mask_path)
            if os.path.isfile(abs_mask):
                skipped_count += 1
                continue
        
        # 마스크 생성
        mask_path, success = process_image(
            image_path, column_config, seg_engine, threshold, downscale
        )
        
        if success:
            df.at[idx, 'rgb_mask_path'] = mask_path
            processed_count += 1
        else:
            error_count += 1
    
    # 결과 출력
    print(f"\nProcessing completed:")
    print(f"  - Processed: {processed_count}")
    print(f"  - Skipped: {skipped_count}")
    print(f"  - Errors: {error_count}")
    
    # CSV 저장
    output_path = out_csv or csv_path
    df.to_csv(output_path, index=False)
    print(f"Updated CSV saved to: {output_path}")
    
    return True


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Precompute segmentation masks')
    parser.add_argument('--csv', type=str, required=True,
                       help='Input CSV file path')
    parser.add_argument('--column-config', type=str, required=True,
                       help='Column configuration file path')
    parser.add_argument('--out-csv', type=str, default=None,
                       help='Output CSV file path (default: overwrite input)')
    parser.add_argument('--overwrite', action='store_true',
                       help='Overwrite existing masks')
    parser.add_argument('--downscale', type=float, default=1.0,
                       help='Downscale factor for images (default: 1.0)')
    parser.add_argument('--threshold', type=float, default=0.5,
                       help='Mask threshold (default: 0.5)')
    
    args = parser.parse_args()
    
    try:
        # 컬럼 설정 로드
        column_config = load_column_config(args.column_config)
        
        # CSV 처리
        success = process_csv(
            csv_path=args.csv,
            column_config=column_config,
            out_csv=args.out_csv,
            overwrite=args.overwrite,
            downscale=args.downscale,
            threshold=args.threshold
        )
        
        if success:
            print("Mask precomputation completed successfully!")
        else:
            print("Mask precomputation failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
