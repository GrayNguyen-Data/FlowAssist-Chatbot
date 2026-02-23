import sys
from pathlib import Path
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.setting_loader import load_settings


class TiDBConnectionManager:

    def __init__(self):
        print("Loading TiDB settings...")

        settings = load_settings()
        tidb_config = settings["vector_store"]

        self.tidb_host = tidb_config["host"]
        self.tidb_port = int(tidb_config["port"])
        self.tidb_user = tidb_config["user"]
        self.tidb_password = tidb_config["password"]
        self.tidb_database = tidb_config["database"]
        self.tidb_timeout = int(tidb_config["timeout"])

        print(f"TiDB Host: {self.tidb_host}")
        print(f"TiDB Port: {self.tidb_port}")
        print(f"TiDB Database: {self.tidb_database}")

        # Build database URL
        self.database_url = (
            f"mysql+pymysql://{self.tidb_user}:{self.tidb_password}"
            f"@{self.tidb_host}:{self.tidb_port}/{self.tidb_database}"
            f"?ssl_verify_cert=false"
        )

    # DÙNG CHO VECTOR STORE
    def get_connection_string(self):
        return self.database_url

    # DÙNG CHO RAW SQL
    def get_engine(self):
        engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            connect_args={
                "read_timeout": self.tidb_timeout,
                "write_timeout": self.tidb_timeout
            }
        )
        return engine

    # TEST CONNECTION
    def connect(self):
        print("Connecting to TiDB...")
        try:
            engine = self.get_engine()

            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print(f"CONNECT TiDB THÀNH CÔNG: {result.scalar()}")
                print(f"Host: {self.tidb_host}:{self.tidb_port}")
                print(f"Database: {self.tidb_database}")

            return engine

        except Exception as e:
            print("CONNECT FAIL")
            print(f"Error: {e}")
            return None

_manager = TiDBConnectionManager()

def get_tidb_connection_string():
    return _manager.get_connection_string()


def get_tidb_engine():
    return _manager.get_engine()


def connect_tidb():
    return _manager.connect()
