import sys
from pathlib import Path

# thêm thư mục gốc dự án vào sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from rag.ingestion.loader import get_raw_data_from_minio

get_raw_data_from_minio()
