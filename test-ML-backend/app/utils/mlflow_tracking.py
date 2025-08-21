# mlflow_progress.py
from typing import Dict, Optional, List
from mlflow.tracking import MlflowClient
import time
import math

client = MlflowClient()

def latest_metric(run_id: str, key: str):
    hist = client.get_metric_history(run_id, key)
    if not hist:
        return None
    return max(hist, key=lambda m: (m.step, m.timestamp))

def latest_metrics(run_id: str, keys: List[str]) -> Dict[str, Optional[float]]:
    out = {}
    for k in keys:
        m = latest_metric(run_id, k)
        out[k] = None if m is None else float(m.value)
    return out

def estimate_eta_seconds(run_id: str, window: int = 5) -> Optional[float]:
    """
    progress(%)의 최근 window개를 이용해서 남은 시간 ETA 추정
    """
    hist = client.get_metric_history(run_id, "progress")
    if not hist:
        return None
    # step/timestamp 기준 정렬
    hist = sorted(hist, key=lambda m: (m.step, m.timestamp))
    recent = hist[-window:]
    if len(recent) < 2:
        return None
    # 초 단위 시간/진척률
    times = [m.timestamp/1000.0 for m in recent]  # ms → s
    vals  = [m.value for m in recent]            # %
    dt = times[-1] - times[0]
    dv = vals[-1] - vals[0]
    if dt <= 0 or dv <= 0:
        return None
    speed = dv / dt  # % per second
    remaining = max(0.0, 100.0 - vals[-1])
    return remaining / speed  # seconds

def get_run_core(run_id: str) -> Dict:
    run = client.get_run(run_id)
    data = run.data
    info = run.info
    tags = data.tags
    params = {p.key: p.value for p in data.params}
    # 최신 메트릭
    m_progress = latest_metric(run_id, "progress")
    m_loss     = latest_metric(run_id, "loss")
    m_val_loss = latest_metric(run_id, "val_loss")

    eta_sec = estimate_eta_seconds(run_id)

    return {
        "run_id": info.run_id,
        "experiment_id": info.experiment_id,
        "status_tag": tags.get("status", "running"),
        "lifecycle_stage": info.lifecycle_stage,
        "run_name": run.info.run_name,  # 표시명 (없으면 None)
        "params": params,
        "metrics": {
            "progress": None if m_progress is None else float(m_progress.value),
            "loss": None if m_loss is None else float(m_loss.value),
            "val_loss": None if m_val_loss is None else float(m_val_loss.value),
            "epoch": None if m_progress is None else int(m_progress.step),
        },
        "eta_seconds": None if eta_sec is None else float(eta_sec),
        "start_time": info.start_time,  # ms
        "end_time": info.end_time,      # ms (진행 중이면 None)
    }