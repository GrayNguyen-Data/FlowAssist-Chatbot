from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

DATABASE_URL = os.getenv("TIDB_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Không tìm thấy TIDB_DATABASE_URL trong .env")

print("DATABASE_URL loaded")

# Tạo engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("CONNECT TiDB THÀNH CÔNG:", result.scalar())
except Exception as e:
    print("CONNECT FAIL")
    print(e)