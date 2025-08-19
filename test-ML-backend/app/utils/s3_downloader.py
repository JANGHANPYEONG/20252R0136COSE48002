"""
- input S3 경로 형태:
1) s3://bucket-name/prefix/sub/dir
2) bucket-name/prefix/sub/dir
3) s3://bucket-name (버킷 루트 전체)
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# .env 로드
try:
    from pathlib import Path as _P
    from dotenv import load_dotenv as _load
    _ROOT = _P(__file__).resolve().parents[2]  # .../test-ML-backend
    _load(_ROOT / ".env")
except Exception:
    pass
if not os.getenv("AWS_DEFAULT_REGION") and os.getenv("S3_REGION_NAME"):
    os.environ["AWS_DEFAULT_REGION"] = os.environ["S3_REGION_NAME"]

import boto3
from botocore.exceptions import ClientError, BotoCoreError

# 로깅
logger = logging.getLogger(__name__)
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)

# S3 경로 파싱 : 's3://bucket/prefix' 또는 'bucket/prefix'
# return : (bucket, prefix)
def _parse_s3_path(s3_path: str):
    s = s3_path.strip()
    if s.startswith("s3://"):
        parsed = urlparse(s)
        return parsed.netloc, parsed.path.lstrip("/")
    parts = s.split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    return bucket, prefix

# S3 객체 나열 : 버킷과 prefix 주면 S3에서 그 아래 모든 파일 목록 하나씩 내보내기
def _iter_s3_objects(s3_client, bucket: str, prefix: str):
    # 너무 목록이 길면 나눠서 가져오게 함
    paginator = s3_client.get_paginator("list_objects_v2")

    # 어떤 버킷/경로를 볼지 지정
    params = {"Bucket": bucket}
    if prefix:
        params["Prefix"] = prefix

    # 각 page 예시: { "Contents": [ { "Key": "a/b/c.png", ... }, ... ], ... }
    for page in paginator.paginate(**params):
        for obj in (page.get("Contents") or []):  # obj는 "한 개 파일"의 메타데이터(dict)
            key = obj.get("Key", "")  # 파일 경로 문자열
            # S3는 폴더가 없지만 'a/b/'처럼 '/'로 끝나는 플레이스홀더 키가 있을 수 있음 → 건너뛰기
            if not key or key.endswith("/"):
                continue
            yield obj  # 실제 파일


"""
단일 파일 다운로드 함수.
- prefix 구조 유지하며 로컬에 저장
- overwrite=False면 존재 시 스킵, True면 덮어쓰기
return : (key, 성공 여부, error_message or None)
"""
def _download_one(
        s3_client,
        bucket: str,
        key: str,
        local_root: Path,
        base_prefix: str,
        overwrite: bool,
):
    try:
        # 로컬 상대경로 계산
        base = base_prefix.rstrip("/") if base_prefix else ""
        if base and key.startswith(base + "/"):
            rel = key[len(base) + 1 :]
        else:
            rel = key

        dst = local_root.joinpath(rel)
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists() and not overwrite:
            return key, False, None  # 스킵

        s3_client.download_file(Bucket=bucket, Key=key, Filename=str(dst))
        return key, True, None

    except (ClientError, BotoCoreError) as e:
        return key, False, str(e)
    except Exception as e:
        return key, False, str(e)
    

"""
prefix 전체 다운로드
- s3_path : 's3://bucket/prefix' 또는 'bucket/prefix'
- local_dir : EC2 로컬 저장 디렉
- overwrite : 존재하면 덮어쓸지 여부
- workers : 파일 단위 병렬 다운로드에 사용할 스레드 수

returns
dict
        요약 정보:
        {
          "bucket": str,
          "prefix": str,
          "local_dir": str,
          "total": int,
          "downloaded": int,
          "skipped": int,
          "failed": int,
          "errors": List[Tuple[str, str]],
        }

"""
def download_s3_prefix_to_local(
        s3_path: str,
        local_dir: str,
        *,
        overwrite: bool = False,
        workers: int = 8,
):
    # s3_path 파싱
    bucket, prefix = _parse_s3_path(s3_path)
    
    # 로컬 저장 디렉 준비
    local_root = Path(local_dir).expanduser().resolve()
    local_root.mkdir(parents=True, exist_ok=True)

    # S3 클라이언트 생성
    region = os.getenv("AWS_DEFAULT_REGION") or os.getenv("S3_REGION_NAME")
    s3 = boto3.client("s3", region_name=region) if region else boto3.client("s3")

    # 어떤 걸 받는지 로그로 확인
    logger.info(f"S3 버킷: {bucket} / 프리픽스: {prefix or '(루트)'}")
    logger.info(f"저장 경로: {local_root}")

    # 대상 키 수집 : bucket/prefix 아래의 '파일'만 모으기
    keys: List[str] = [obj["Key"] for obj in _iter_s3_objects(s3, bucket, prefix)]

    # 빈 경우 요약 리턴
    if not keys:
        return {
            "bucket": bucket,
            "prefix": prefix, 
            "local_dir": str(local_root),
            "total": 0,
            "downloaded": 0,
            "skipped": 0,
            "failed": 0,
            "errors": [],
        }
    
    max_workers = min(workers, len(keys))

    # 병렬 다운로드
    downloaded = skipped = failed = 0
    errors: List[Tuple[str, str]] = []
    base_prefix = prefix

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [
            ex.submit(_download_one, s3, bucket, key, local_root, base_prefix, overwrite)
            for key in keys
        ]
        for fut in as_completed(futures):
            key, ok, err = fut.result()
            if err is None:
                if ok: downloaded += 1
                else: skipped += 1
            else:
                failed += 1
                errors.append((key, err))

    return {
        "bucket": bucket,
        "prefix": prefix,
        "local_dir": str(local_root),
        "total": len(keys),
        "downloaded": downloaded,
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
    }

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="S3 prefix 하위 모든 파일을 EC2 디렉으로 병렬 다운로드")
    parser.add_argument("--s3", required=True, help="S3 경로")
    parser.add_argument("--to", required=True, help="로컬 저장 디렉")
    parser.add_argument("--overwrite", action="store_true", help="동일 경로 파일 있을 때 덮어쓰기")
    parser.add_argument("--workers", type=int, default=8, help="파일 단위 병렬 다운로드 스레드 수 (기본 8)")

    args = parser.parse_args()

    summary = download_s3_prefix_to_local(
        s3_path=args.s3,
        local_dir=args.to,
        overwrite=args.overwrite,
        workers=args.workers,
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))