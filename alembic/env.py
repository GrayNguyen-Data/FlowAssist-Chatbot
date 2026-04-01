from logging.config import fileConfig
from urllib.parse import quote_plus
import certifi

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.db.base import Base
import app.db.models  # noqa


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def build_sync_database_url() -> str:
    user = quote_plus(settings.TIDB_USER)
    password = quote_plus(settings.TIDB_PASSWORD)
    host = settings.TIDB_HOST
    port = settings.TIDB_PORT
    database = settings.TIDB_DATABASE

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


def get_connect_args():
    ca_path = settings.TIDB_CA_PATH or certifi.where()
    return {
        "ssl": {
            "ca": ca_path,
        }
    }


def run_migrations_offline() -> None:
    url = build_sync_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = build_sync_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=get_connect_args(),
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()