"""
- S3 경로 형식 :
1) s3://bucket-name/prefix/sub/dir
2) bucket-name/prefix/sub/dir
3) s3://bucket-name
"""

from __future__ import annotations

import os
import sys
import logging
import mimetypes
from pathlib import Path
from typing import List, Tuple, Optional
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


# S3 경로 파싱 → (bucket, prefix)
def _parse_s3_path(s3_path: str) -> Tuple[str, str]:
    s = s3_path.strip()
    if s.startswith("s3://"):
        parsed = urlparse(s)
        return parsed.netloc, parsed.path.lstrip("/")
    parts = s.split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    return bucket, prefix


# 로컬 파일 나열 (단일 파일 또는 디렉터리)
def _iter_local_files(src_path: Path) -> List[Path]:
    if src_path.is_file():
        return [src_path]
    return [p for p in src_path.rglob("*") if p.is_file()]


# S3에 동일 키 존재 여부 (overwrite=False일 때 스킵)
def _s3_key_exists(s3_client, bucket: str, key: str) -> bool:
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if code in ("404", "NoSuchKey", "NotFound"):
            return False
        # 그 외 오류는 호출부에서 처리
        raise


# 단일 파일 업로드
def _upload_one(
    s3_client,
    bucket: str,
    prefix: str,
    base_root: Path,
    file_path: Path,
    overwrite: bool,
) -> Tuple[str, bool, Optional[str]]:
    try:
        rel = file_path.relative_to(base_root).as_posix()
        key = (prefix.rstrip("/") + "/" + rel) if prefix else rel

        if not overwrite:
            try:
                if _s3_key_exists(s3_client, bucket, key):
                    return key, False, None  # 스킵
            except ClientError as e:
                return key, False, str(e)

        ctype, _ = mimetypes.guess_type(file_path.name)
        extra = {"ContentType": ctype} if ctype else None

        if extra:
            s3_client.upload_file(Filename=str(file_path), Bucket=bucket, Key=key, ExtraArgs=extra)
        else:
            s3_client.upload_file(Filename=str(file_path), Bucket=bucket, Key=key)

        return key, True, None

    except (ClientError, BotoCoreError) as e:
        return key if "key" in locals() else file_path.name, False, str(e)
    except Exception as e:
        return key if "key" in locals() else file_path.name, False, str(e)


# 로컬 → S3 업로드
def upload_local_to_s3_prefix(
    local_path: str,
    s3_path: str,
    *,
    overwrite: bool = False,
    workers: int = 8,
) -> dict:
    """
    local_path(파일 또는 디렉터리) 하위 모든 파일을 s3_path(prefix)로 병렬 업로드한다.
    디렉터리 구조는 그대로 보존되어 S3 키에 반영된다.
    """
    src = Path(local_path).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"로컬 경로가 존재하지 않습니다: {src}")

    bucket, prefix = _parse_s3_path(s3_path)

    region = os.getenv("AWS_DEFAULT_REGION") or os.getenv("S3_REGION_NAME")
    s3 = boto3.client("s3", region_name=region) if region else boto3.client("s3")

    files: List[Path] = _iter_local_files(src)
    base_root = src if src.is_dir() else src.parent

    logger.info(f"업로드 대상: {len(files)}개 / 로컬 기준: {base_root}")
    logger.info(f"S3 버킷: {bucket} / 프리픽스: {prefix or '(루트)'}")

    if not files:
        return {
            "bucket": bucket,
            "prefix": prefix,
            "local_root": str(src),
            "total": 0,
            "uploaded": 0,
            "skipped": 0,
            "failed": 0,
            "errors": [],
        }

    uploaded = skipped = failed = 0
    errors: List[Tuple[str, str]] = []
    max_workers = min(workers, len(files))

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [
            ex.submit(_upload_one, s3, bucket, prefix, base_root, f, overwrite)
            for f in files
        ]
        for fut in as_completed(futures):
            key, ok, err = fut.result()
            if err is None:
                if ok:
                    uploaded += 1
                else:
                    skipped += 1
            else:
                failed += 1
                errors.append((key, err))

    return {
        "bucket": bucket,
        "prefix": prefix,
        "local_root": str(src),
        "total": len(files),
        "uploaded": uploaded,
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
    }


# CLI
if __name__ == "__main__":
    import argparse
    import json

    # 추가 .env 로드 시도(이미 로드돼도 무해)
    try:
        from dotenv import load_dotenv as _load2
        _load2()
    except Exception:
        pass

    # 리전 보정(중복 무해)
    if not os.getenv("AWS_DEFAULT_REGION") and os.getenv("S3_REGION_NAME"):
        os.environ["AWS_DEFAULT_REGION"] = os.environ["S3_REGION_NAME"]

    parser = argparse.ArgumentParser(description="로컬(파일/디렉터리) → S3 프리픽스 병렬 업로드")
    parser.add_argument("--src", required=True, help="로컬 경로(파일 또는 디렉터리)")
    parser.add_argument("--s3", required=True, help="S3 경로 (예: s3://bucket/prefix)")
    parser.add_argument("--overwrite", action="store_true", help="동일 키 존재 시 덮어쓰기")
    parser.add_argument("--workers", type=int, default=8, help="병렬 업로드 스레드 수 (기본 8)")
    args = parser.parse_args()

    summary = upload_local_to_s3_prefix(
        local_path=args.src,
        s3_path=args.s3,
        overwrite=args.overwrite,
        workers=args.workers,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))