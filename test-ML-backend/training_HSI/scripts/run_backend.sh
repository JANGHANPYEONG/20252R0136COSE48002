#!/bin/bash
# run_backend.sh

set -e

PROJECT_DIR=/home/ubuntu/2025-Deeplant-Dev/20252R0136COSE48002
BACKEND_DIR=$PROJECT_DIR/test-ML-backend
VENV=$PROJECT_DIR/venv/bin/activate
SESSION=deeplant

# 0) sanity check
if [ ! -d "$BACKEND_DIR/app" ]; then
  echo "[ERR] $BACKEND_DIR/app 디렉터리가 없습니다." >&2
  exit 1
fi
if [ ! -f "$BACKEND_DIR/app/__init__.py" ]; then
  echo "[INFO] app/__init__.py 생성"
  touch "$BACKEND_DIR/app/__init__.py"
fi

# 0-1) Redis 실행 확인 및 시작
if ! command -v redis-server &> /dev/null; then
  echo "[ERR] redis-server가 설치되어 있지 않습니다." >&2
  exit 1
fi

# Redis가 실행 중인지 확인
if ! redis-cli ping &> /dev/null; then
  echo "[INFO] Redis 서버 시작 중..."
  redis-server --daemonize yes
  sleep 1
  if redis-cli ping &> /dev/null; then
    echo "[INFO] Redis 서버가 성공적으로 시작되었습니다."
  else
    echo "[ERR] Redis 서버 시작 실패" >&2
    exit 1
  fi
else
  echo "[INFO] Redis 서버가 이미 실행 중입니다."
fi

# 1) 새 세션 만들기
tmux kill-session -t $SESSION 2>/dev/null || true
tmux new-session -d -s $SESSION

# 2) Pane 1: uvicorn
tmux send-keys -t $SESSION "cd $PROJECT_DIR" C-m
tmux send-keys -t $SESSION "source $VENV" C-m
tmux send-keys -t $SESSION "export PYTHONPATH=$BACKEND_DIR" C-m
tmux send-keys -t $SESSION "cd $BACKEND_DIR" C-m
tmux send-keys -t $SESSION "pip show websockets >/dev/null 2>&1 || pip install 'uvicorn[standard]' websockets" C-m
tmux send-keys -t $SESSION "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" C-m

# 3) Pane 2: celery
tmux split-window -v -t $SESSION
tmux send-keys -t $SESSION "cd $PROJECT_DIR" C-m
tmux send-keys -t $SESSION "source $VENV" C-m
tmux send-keys -t $SESSION "export PYTHONPATH=$BACKEND_DIR" C-m
tmux send-keys -t $SESSION "cd $BACKEND_DIR" C-m
tmux send-keys -t $SESSION "celery -A app.routers.hsi_train.celery_app worker --loglevel=info --pool=threads --concurrency=1" C-m

tmux attach -t $SESSION