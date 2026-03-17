from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


BASE_DIR = Path(__file__).resolve().parents[2]
CA_CERT_PATH = str(BASE_DIR / "certs" / "isrgrootx1.pem")


def build_db_credentials():
    return {
        "user": quote_plus(settings.TIDB_USER),
        "password": quote_plus(settings.TIDB_PASSWORD),
        "host": settings.TIDB_HOST,
        "port": settings.TIDB_PORT,
        "database": settings.TIDB_DATABASE,
    }


def build_async_database_url() -> str:
    db = build_db_credentials()
    return (
        f"mysql+asyncmy://{db['user']}:{db['password']}"
        f"@{db['host']}:{db['port']}/{db['database']}?charset=utf8mb4"
    )


def build_sync_database_url() -> str:
    db = build_db_credentials()
    return (
        f"mysql+pymysql://{db['user']}:{db['password']}"
        f"@{db['host']}:{db['port']}/{db['database']}?charset=utf8mb4"
    )


ASYNC_DATABASE_URL = build_async_database_url()
SYNC_DATABASE_URL = build_sync_database_url()

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={
        "ssl": {
            "ca": CA_CERT_PATH,
            "check_hostname": True,
        },
        "connect_timeout": 10,
    },
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_sync_engine():
    return create_engine(
        SYNC_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={
            "ssl": {
                "ca": CA_CERT_PATH,
                "check_hostname": True,
            },
            "connect_timeout": 10,
            "read_timeout": 10,
            "write_timeout": 10,
        },
    )


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session