# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ✅ 프로젝트 모듈 import (경로는 프로젝트 구조에 맞춰 그대로 사용)
# DB URL 명칭이 프로젝트에 따라 다를 수 있어 try/except로 처리
from app.db.database import SQLALCHEMY_DATABASE_URL as DB_URL, Base

# 모델 등록을 위해 import (사이드 이펙트; 변수는 사용하지 않으므로 noqa)
import app.db.db_model as models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ autogenerate 기준 메타데이터
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    # alembic.ini의 sqlalchemy.url 대신, 코드에서 주입
    config.set_main_option("sqlalchemy.url", DB_URL)
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # alembic.ini의 [alembic] 섹션 복사 후 URL만 덮어쓰기
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = DB_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        render_as_batch = str(DB_URL).startswith("sqlite")
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=render_as_batch,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()