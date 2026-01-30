import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.setting_loader import load_settings

# Load settings from YAML with environment variables
settings = load_settings("config/settings.yaml")

print("Loading TiDB settings...")

# Extract TiDB configuration
tidb_config = settings["vector_store"]
tidb_host = tidb_config["host"]
tidb_port = int(tidb_config["port"])
tidb_user = tidb_config["user"]
tidb_password = tidb_config["password"]
tidb_database = tidb_config["database"]
tidb_timeout = int(tidb_config["timeout"])

print(f"TiDB Host: {tidb_host}")
print(f"TiDB Port: {tidb_port}")
print(f"TiDB Database: {tidb_database}")

# Build database URL
database_url = f"mysql+pymysql://{tidb_user}:{tidb_password}@{tidb_host}:{tidb_port}/{tidb_database}?ssl_verify_cert=false"

print("Connecting to TiDB...")

# Create engine
try:
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"read_timeout": tidb_timeout, "write_timeout": tidb_timeout}
    )
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"✓ CONNECT TiDB THÀNH CÔNG: {result.scalar()}")
        print(f"✓ Host: {tidb_host}:{tidb_port}")
        print(f"✓ Database: {tidb_database}")
except Exception as e:
    print(f"✗ CONNECT FAIL")
    print(f"Error: {e}")
