#!/bin/bash

PORT=5000
PIDS=$(lsof -ti :$PORT)

if [ -z "$PIDS" ]; then
  echo "포트 $PORT 를 사용하는 프로세스가 없습니다."
else
  echo "포트 $PORT 를 사용하는 PID: $PIDS"
  echo "프로세스를 종료합니다..."
  kill -9 $PIDS
  echo "종료 완료"
fi