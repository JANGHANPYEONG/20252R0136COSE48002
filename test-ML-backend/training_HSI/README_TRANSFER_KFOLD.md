# Transfer Learning + K-Fold Cross Validation

작은 데이터셋(159개)을 위한 최적화된 학습 시스템

## 📁 새로 추가된 파일

```
training_HSI/
├── models/HSI_image/
│   └── hsi_vit_transfer.py           # Transfer Learning 모델
├── utils/
│   └── trainer_kfold.py              # K-Fold Trainer
├── configs/HSI_image/
│   └── hsi_vit_transfer_kfold.json   # Transfer + K-Fold 설정
└── train_vit_transfer_kfold.py       # 메인 실행 파일
```

---

## 🚀 실행 방법

### 1. 필수 패키지 설치

```bash
pip install timm  # PyTorch Image Models
```

### 2. 학습 실행

```bash
python train_vit_transfer_kfold.py --config configs/HSI_image/hsi_vit_transfer_kfold.json
```

### 3. MLflow 없이 실행

```bash
python train_vit_transfer_kfold.py --config configs/HSI_image/hsi_vit_transfer_kfold.json --no-mlflow
```

---

## 🎯 주요 특징

### 1. **Transfer Learning (ImageNet Pretrained)**

- **모델**: `vit_tiny_patch16_224` (Timm)
- **파라미터**: ~5.7M (Pretrained) + ~2K (Custom Head)
- **장점**:
  - ImageNet에서 학습된 low-level feature 재사용
  - 159개 샘플로도 충분한 성능
  - 빠른 수렴

**3채널 → 6채널 변환**:
```python
# 기존 3채널 가중치를 2번 반복 + 스케일링
new_weight = old_weight.repeat(1, 2, 1, 1) * 0.5
```

### 2. **5-Fold Cross Validation**

- **분할**: 159개 → 5 Folds
- **각 Fold**: Train ~127개 / Val ~32개
- **장점**:
  - 모든 샘플이 검증에 사용됨
  - 과적합 방지
  - 성능 평가의 신뢰도 ↑

**결과 집계**:
- Mean ± Std for R², MSE, MAE
- Min/Max 범위
- Fold별 모델 저장

### 3. **강력한 정규화**

```json
{
  "dropout": 0.3,              // 높은 Dropout
  "weight_decay": 0.01,        // L2 정규화
  "early_stopping_patience": 20
}
```

### 4. **RGB/파장 분리 정규화**

```python
# 파장 채널: 별도 StandardScaler
# RGB 채널: 별도 StandardScaler
# → 통계적 특성 차이 반영
```

---

## 📊 예상 결과

```
==================================================================
5-Fold Cross Validation Results
==================================================================

Validation Loss:
  Mean ± Std: 0.3500 ± 0.0800
  Range: [0.2700, 0.4500]

R² Score:
  Mean ± Std: 0.7200 ± 0.0600
  Range: [0.6500, 0.8000]

MSE:
  Mean ± Std: 0.4500 ± 0.1000
  Range: [0.3200, 0.5800]

MAE:
  Mean ± Std: 0.5200 ± 0.0900
  Range: [0.4000, 0.6500]

Combined Score:
  Mean ± Std: 0.6500 ± 0.0700
  Range: [0.5500, 0.7500]

Total Training Time: 45.30 minutes
==================================================================
```

---

## 🔧 설정 파일 설명

### `hsi_vit_transfer_kfold.json`

```json
{
  "model": {
    "timm_model_name": "vit_tiny_patch16_224",  // Timm 모델
    "pretrained": true,                         // ImageNet 가중치
    "freeze_backbone": false,                   // Backbone 학습 여부
    "dropout": 0.3
  },
  "kfold": {
    "n_splits": 5,                              // Fold 수
    "save_fold_models": true                    // Fold별 모델 저장
  },
  "train": {
    "epochs": 100,                              // Fold당 epoch
    "lr": 1e-4,                                 // 낮은 학습률
    "weight_decay": 0.01
  }
}
```

---

## 📈 모델 비교

| 모델 | 파라미터 | Pretrained | 예상 R² | 비고 |
|------|----------|------------|---------|------|
| 원본 ViT | ~138K | ❌ | 0.50 | Overfit 심함 |
| Tiny ViT | ~18K | ❌ | 0.60 | 여전히 부족 |
| **Transfer ViT** | **~5.7M** | **✅** | **0.72+** | **권장** |

---

## 🎨 고급 옵션

### Backbone 동결 (Fine-tuning)

```json
{
  "freeze_backbone": true,  // Backbone 고정, Head만 학습
  "lr": 1e-3               // 더 높은 학습률 가능
}
```

**언제 사용?**
- 데이터가 매우 적을 때 (100개 미만)
- 빠른 실험이 필요할 때

### 다른 Timm 모델

```json
{
  "timm_model_name": "vit_small_patch16_224"   // 더 큰 모델
  // or
  "timm_model_name": "vit_base_patch16_224"    // ImageNet-21k
}
```

---

## 📁 결과 파일

학습 완료 후 생성되는 파일:

```
checkpoints/hsi_vit_transfer_kfold/
├── kfold/
│   ├── fold_1_model.pth
│   ├── fold_2_model.pth
│   ├── fold_3_model.pth
│   ├── fold_4_model.pth
│   └── fold_5_model.pth
└── kfold_results.json      # 전체 결과 요약
```

### `kfold_results.json` 구조

```json
{
  "fold_results": [
    {
      "fold": 1,
      "train_size": 127,
      "val_size": 32,
      "best_val_loss": 0.35,
      "best_val_metrics": {
        "r2": 0.72,
        "mse": 0.45,
        "mae": 0.52
      }
    },
    ...
  ],
  "aggregated_results": {
    "r2_mean": 0.72,
    "r2_std": 0.06,
    "mse_mean": 0.45,
    ...
  }
}
```

---

## 🔍 트러블슈팅

### 1. Timm 설치 오류

```bash
pip install timm==0.9.12
```

### 2. CUDA Out of Memory

```json
{
  "data": {
    "batch_size": 4  // 8 → 4로 감소
  }
}
```

### 3. Fold별 학습 시간이 너무 길 때

```json
{
  "train": {
    "epochs": 50  // 100 → 50으로 감소
  }
}
```

### 4. 과적합이 심할 때

```json
{
  "model": {
    "freeze_backbone": true,  // Backbone 동결
    "dropout": 0.5            // Dropout 증가
  },
  "train": {
    "weight_decay": 0.05      // 정규화 강화
  }
}
```

---

## 💡 팁

1. **첫 실행**: `--no-mlflow`로 빠르게 테스트
2. **Fold 수 조정**: 데이터가 매우 적으면 `n_splits: 3`
3. **앙상블**: 5개 Fold 모델을 평균내어 최종 예측
4. **모니터링**: MLflow UI에서 Fold별 성능 비교

---

## 📞 문제 해결

학습 중 문제가 발생하면:

1. 로그 확인
2. `kfold_results.json` 확인
3. Fold별 Loss 그래프 비교 (MLflow)
4. Overfit 여부 확인: Train Loss << Val Loss

**좋은 학습 신호**:
- Fold간 성능 편차 < 10%
- Val Loss가 안정적으로 감소
- R² > 0.65

**나쁜 학습 신호**:
- Fold간 성능 편차 > 30%
- Val Loss 발산
- R² < 0.4
