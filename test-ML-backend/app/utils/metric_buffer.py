"""
인메모리 메트릭 버퍼(간이 큐) 구현

- 목적: 학습(ML 서버)에서 매 에폭마다 생성되는 메트릭을
        잠시 메모리에 쌓아두고, 프론트가 폴링으로 가져가게 하기 위함
- 영속성 없음: 서버 재시작 시 데이터 유실(실시간 표시용이라 괜찮음)
- 단일 프로세스/단일 인스턴스 기준. 수평 확장 필요해지면 Redis 같은 외부 버퍼로 교체 가능
"""

import time
from collections import deque
from typing import Dict, Any, Deque


class InMemoryMetricBuffer:
    """
    run_id 별로 고정 길이의 deque(링버퍼)를 갖고, (seq, ts, payload)를 저장한다.
    - seq: 1부터 시작하는 증가 번호(커서 역할). 프론트는 마지막 받은 seq를 after로 보내 다음 것부터 받는다.
    - ts : 서버 수신 시각(초 단위)
    - payload: 학습 코드에서 전달한 임의의 메트릭 딕셔너리
    """

    def __init__(self, maxlen: int = 1000, ttl_sec: int = 3600 * 5):
        """
        Args:
            maxlen   : 각 run_id 버퍼에 보관할 최대 메세지 수(넘치면 가장 오래된것부터 자동 삭제)
            ttl_sec  : 이 run_id 데이터 구조를 얼마 동안 유지할지(최근 접근/갱신 기준)
        """
        self.store: Dict[str, Deque[Dict[str, Any]]] = {}     # 각 훈련 세션(run_id)별로 메트릭을 deque에 저장
        self.done: set[str] = set() # 완료된 훈련 세션 ID들을 set으로 관리
        self.touched: Dict[str, float] = {}         # 각 세션의 마지막 접근 시간을 추적
        self.maxlen = maxlen    # 각 세션당 최대 1000개의 메트릭 저장
        self.ttl = ttl_sec  # 5시간 후 자동 정리

    def _gc(self) -> None:
        """
        가비지 컬렉션(GC):
        - 마지막 접근/갱신 후 ttl_sec가 지난 run_id는 메모리에서 정리
        - 무한 증식을 막기 위한 가벼운 청소 로직
        """
        now = time.time()
        dead_ids = [rid for rid, ts in self.touched.items() if now - ts > self.ttl]
        for rid in dead_ids:
            self.store.pop(rid, None)
            self.done.discard(rid)
            self.touched.pop(rid, None)

    def publish(self, run_id: str, payload: Dict[str, Any]) -> int:
        """
        학습 루프에서 매 에폭마다 호출.
        새 메트릭(payload)을 run_id 버퍼에 추가하고, 증가 seq를 부여한다.

        Returns:
            부여된 seq (프론트는 이 값을 after 커서로 사용할 수 있다)
        """
        self._gc()

        # run_id에 해당하는 deque를 가져오거나 없으면 새로 만들기
        q = self.store.setdefault(run_id, deque(maxlen=self.maxlen))

        # 다음 seq 계산(비어있으면 1부터)
        seq = (q[-1]["seq"] + 1) if q else 1

        # 표준화된 아이템 구조(필수 필드: seq, ts)
        item = {
            "seq": seq,           # 커서 역할
            "ts": time.time(),    # 서버 수신 시각
            **payload             # 사용자가 넘긴 임의의 지표들(type, epoch, loss 등)
        }

        # 오른쪽에 추가(링버퍼 maxlen 초과 시 가장 오래된 항목 자동 제거)
        q.append(item)

        # 마지막 접근 갱신(가비지 컬렉션용)
        self.touched[run_id] = time.time()
        return seq

    def read(self, run_id: str, after: int, limit: int = 100) -> Dict[str, Any]:
        """
        프론트가 호출: after(마지막으로 받은 seq)보다 큰 항목만 최대 limit개 반환.
        커서 기반 페이징으로 중복 수신 없이 이어서 받기 쉬움.

        Returns:
            {
              "items": [ {seq, ts, ...payload}, ... ],
              "next": <다음 호출 때 after로 쓸 커서(마지막 반환된 seq 또는 기존 after)>,
              "status": "running" | "done"
            }
        """
        self._gc()

        q = self.store.get(run_id, deque())

        # after보다 큰(seq가 더 큰) 아이템들만 반환
        items = [it for it in q if it["seq"] > after][:limit]

        # 다음 커서(next): 반환 아이템이 있으면 마지막 seq, 없으면 기존 after 유지
        next_cursor = items[-1]["seq"] if items else after

        # 완료 여부(학습 종료 시 mark_done에서 표기)
        status = "done" if run_id in self.done else "running"

        self.touched[run_id] = time.time()
        return {"items": items, "next": next_cursor, "status": status}

    def mark_done(self, run_id: str) -> None:
        """
        해당 run_id 학습 종료 표시. read() 결과의 status가 'done'으로 바뀐다.
        (데이터 자체는 ttl_sec 동안 유지되므로 프론트가 마지막으로 긁어갈 시간 여유 있음)
        """
        self.done.add(run_id)
        self.touched[run_id] = time.time()

    def status(self, run_id: str) -> str:
        """
        현재 상태 문자열 반환: 'running' 또는 'done'
        """
        return "done" if run_id in self.done else "running"


def get_metric_buffer() -> InMemoryMetricBuffer:
    """
    의존성 주입용 팩토리 함수.
    - 지금은 인메모리 구현만 반환
    - 나중에 환경변수 보고 Redis/SQLite 등으로 바꿔치기 가능(인터페이스 동일)
    """
    return InMemoryMetricBuffer(maxlen=1000, ttl_sec=3600)