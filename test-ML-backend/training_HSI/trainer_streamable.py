"""
스트리밍 가능한 트레이너 데모 구현

- 실제 학습 코드는 각자 다르므로, '콜백' 인터페이스(on_epoch_end)를 통해
  에폭이 끝날 때마다 메트릭을 외부(버퍼)로 내보낼 수 있게 만든 가벼운 예시.
- 네가 기존에 쓰는 트레이너의 '에폭 루프 끝' 위치에
  self.on_epoch_end(epoch, metrics) 한 줄만 추가하면 같은 효과를 낼 수 있다.
"""

import time
from typing import Callable, Dict, Any


class StreamableTrainer:
    def __init__(self, epochs: int, on_epoch_end: Callable[[int, Dict[str, Any]], None]):
        """
        Args:
            epochs       : 총 학습 epoch 수
            on_epoch_end : 에폭 종료 시 호출할 콜백 함수
                           -> 시그니처: (epoch: int, metrics: dict) -> None
                           -> 이 콜백 내부에서 버퍼에 publish를 호출하게 된다.
        """
        self.epochs = epochs
        self.on_epoch_end = on_epoch_end

    def train(self, cfg: Dict[str, Any]):
        """
        학습 본문(데모):
        - 현 코드는 '동작 데모'를 위해 sleep과 가짜 지표를 생성.
        - 실제 프로젝트에서는 데이터 로더, 모델, 옵티마이저, 손실 계산 등
          네가 쓰는 기존 학습 루프를 그대로 사용하고, 에폭 마지막에 콜백만 호출하면 된다.
        """
        for epoch in range(1, self.epochs + 1):
            # --- 실제 학습 로직 ---
            # 1) 입력 배치 반복
            # 2) 순전파/역전파
            # 3) 옵티마이저 스텝
            # 4) 검증 등
            # ----------------------
            time.sleep(0.5)  # (데모용 딜레이, 실제 코드에서는 제거)

            # 프론트에 보여주고 싶은 메트릭을 딕셔너리로 구성
            metrics = {
                "epoch": epoch,
                "train_loss": 1.0 / epoch,
                "val_loss": 1.2 / epoch,
                "f1": epoch * 0.01,
                "lr": 3e-4,
            }

            # 핵심: 에폭 끝에서 콜백 호출(버퍼에 publish -> 프론트가 폴링으로 읽음)
            self.on_epoch_end(epoch, metrics)

        # 학습 전체가 끝난 뒤, 최종 결과(예: 베스트 점수/에폭 등)를 반환
        # 라우터에서 이 값을 'final' 타입으로 한 번 더 push해서 프론트가 마지막으로 받게 할 수 있음.
        return {"best_epoch": self.epochs, "best_f1": self.epochs * 0.01}