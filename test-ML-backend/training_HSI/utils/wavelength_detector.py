"""
Dynamic Wavelength Detection System for HSI Dataset
모든 파장대를 자동으로 검출하고 유연하게 처리하는 시스템
"""

import os
import glob
import re
from collections import Counter, defaultdict
from typing import List, Dict, Set, Tuple, Optional
import numpy as np


class WavelengthDetector:
    """데이터셋의 파장을 동적으로 검출하고 관리하는 클래스"""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.all_wavelengths: Set[str] = set()
        self.wavelength_counts: Dict[str, int] = {}
        self.sample_wavelengths: Dict[str, Set[str]] = defaultdict(set)
        self.wavelength_combinations: Dict[Tuple[str, ...], int] = {}
        self._scan_wavelengths()

    def _scan_wavelengths(self):
        """데이터셋 전체를 스캔하여 파장 정보 수집"""
        print(f"Scanning wavelengths in {self.root_dir}...")

        # 모든 PNG 파일 찾기
        png_files = glob.glob(os.path.join(self.root_dir, '**', '*.png'), recursive=True)

        # 파장 패턴: _430nm, _540nm, _580nm, _430, _540, _580 등
        wavelength_pattern = re.compile(r'_([0-9]+)(?:nm)?[_.]')

        for png_file in png_files:
            # RGB 파일은 스킵
            if 'rgb' in png_file.lower():
                continue

            # 파장 추출
            match = wavelength_pattern.search(png_file)
            if match:
                wavelength = match.group(1) + 'nm'
                self.all_wavelengths.add(wavelength)
                self.wavelength_counts[wavelength] = self.wavelength_counts.get(wavelength, 0) + 1

                # 샘플별 파장 추적
                sample_key = self._extract_sample_key(png_file)
                if sample_key:
                    self.sample_wavelengths[sample_key].add(wavelength)

        # 파장 조합 계산
        combination_counts = Counter()
        for sample, wavelengths in self.sample_wavelengths.items():
            combo = tuple(sorted(wavelengths, key=lambda x: int(x[:-2])))
            combination_counts[combo] += 1

        self.wavelength_combinations = dict(combination_counts)

        print(f"Found wavelengths: {sorted(self.all_wavelengths, key=lambda x: int(x[:-2]))}")
        print(f"Total samples: {len(self.sample_wavelengths)}")

    def _extract_sample_key(self, png_file: str) -> Optional[str]:
        """PNG 파일 경로에서 샘플 키 추출"""
        parts = png_file.replace('\\', '/').split('/')
        if len(parts) >= 6:
            folder = parts[-4]  # 폴더명
            sample = parts[-2]  # 샘플명 (s1, s2 등)
            return f"{folder}/{sample}"
        return None

    def get_optimal_wavelength_set(self, strategy: str = 'max_coverage') -> List[str]:
        """최적의 파장 세트를 반환

        Args:
            strategy: 'max_coverage' | 'common_only' | 'all_available'
        """
        if strategy == 'max_coverage':
            # 가장 많은 샘플에서 사용 가능한 파장들
            min_coverage = len(self.sample_wavelengths) * 0.8  # 80% 이상 커버리지
            return [wl for wl, count in self.wavelength_counts.items()
                   if count >= min_coverage]

        elif strategy == 'common_only':
            # 모든 샘플에 공통으로 있는 파장들만
            min_coverage = len(self.sample_wavelengths)
            return [wl for wl, count in self.wavelength_counts.items()
                   if count >= min_coverage]

        elif strategy == 'all_available':
            # 모든 파장 포함
            return sorted(self.all_wavelengths, key=lambda x: int(x[:-2]))

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def get_wavelength_statistics(self) -> Dict:
        """파장 통계 정보 반환"""
        total_samples = len(self.sample_wavelengths)

        stats = {
            'total_samples': total_samples,
            'available_wavelengths': sorted(self.all_wavelengths, key=lambda x: int(x[:-2])),
            'wavelength_coverage': {},
            'wavelength_combinations': {}
        }

        # 파장별 커버리지
        for wl in sorted(self.all_wavelengths, key=lambda x: int(x[:-2])):
            count = self.wavelength_counts[wl]
            coverage = count / total_samples * 100 if total_samples > 0 else 0
            stats['wavelength_coverage'][wl] = {
                'count': count,
                'coverage_percent': round(coverage, 1)
            }

        # 파장 조합별 분포
        for combo, count in sorted(self.wavelength_combinations.items(),
                                 key=lambda x: -x[1]):
            combo_str = '+'.join(combo)
            coverage = count / total_samples * 100 if total_samples > 0 else 0
            stats['wavelength_combinations'][combo_str] = {
                'count': count,
                'coverage_percent': round(coverage, 1)
            }

        return stats

    def print_statistics(self):
        """파장 통계 출력"""
        stats = self.get_wavelength_statistics()

        print("\n" + "="*60)
        print("WAVELENGTH DETECTION RESULTS")
        print("="*60)

        print(f"\nFound Wavelengths: {len(stats['available_wavelengths'])}")
        print(f"Total Samples: {stats['total_samples']}")

        print(f"\nWavelength Coverage:")
        for wl, info in stats['wavelength_coverage'].items():
            print(f"  {wl:>6}: {info['count']:>3} samples ({info['coverage_percent']:>5.1f}%)")

        print(f"\nWavelength Combinations:")
        for combo, info in stats['wavelength_combinations'].items():
            print(f"  {combo:<20}: {info['count']:>3} samples ({info['coverage_percent']:>5.1f}%)")

        print("\nRecommended Strategies:")

        # 전략별 추천
        try:
            max_coverage = self.get_optimal_wavelength_set('max_coverage')
            common_only = self.get_optimal_wavelength_set('common_only')
            all_available = self.get_optimal_wavelength_set('all_available')

            print(f"  Max Coverage (80%+): {max_coverage}")
            print(f"  Common Only (100%):  {common_only}")
            print(f"  All Available:       {all_available}")

        except Exception as e:
            print(f"  Error calculating strategies: {e}")


def detect_wavelengths(root_dir: str, verbose: bool = True) -> WavelengthDetector:
    """편의 함수: 파장 검출 및 결과 출력"""
    detector = WavelengthDetector(root_dir)
    if verbose:
        detector.print_statistics()
    return detector


if __name__ == "__main__":
    # 테스트
    root_dir = "C:/sanhak/manage-dataset/result"
    if os.path.exists(root_dir):
        detector = detect_wavelengths(root_dir)
    else:
        print(f"Path not found: {root_dir}")