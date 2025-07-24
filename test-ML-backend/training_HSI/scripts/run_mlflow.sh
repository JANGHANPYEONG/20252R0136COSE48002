#!/bin/bash

# mlflow_config.json에서 backend-store-uri와 default-artifact-root 읽기
dirname=$(dirname "$0")
CONFIG_PATH="$dirname/../configs/mlflow_config.json"

BACKEND_STORE_URI=$(jq -r '."backend-store-uri"' "$CONFIG_PATH")
DEFAULT_ARTIFACT_ROOT=$(jq -r '."default-artifact-root"' "$CONFIG_PATH")

# 환경 변수로 오버라이드 가능
BACKEND_STORE_URI=${MLFLOW_BACKEND_STORE_URI:-$BACKEND_STORE_URI}
DEFAULT_ARTIFACT_ROOT=${MLFLOW_DEFAULT_ARTIFACT_ROOT:-$DEFAULT_ARTIFACT_ROOT}

# jq가 없으면 에러
if ! command -v jq &> /dev/null; then
  echo "jq is required but not installed. Please install jq."
  exit 1
fi

# mlflow가 없으면 에러
if ! command -v mlflow &> /dev/null; then
  echo "mlflow is required but not installed. Please install mlflow."
  exit 1
fi

mlflow server \  
  --backend-store-uri "$BACKEND_STORE_URI" \  
  --default-artifact-root "$DEFAULT_ARTIFACT_ROOT" \  
  --host 0.0.0.0 \  
  --port 5000 