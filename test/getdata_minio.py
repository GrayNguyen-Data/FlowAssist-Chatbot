import sys
from pathlib import Path

# thêm thư mục gốc dự án vào sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from storage.getdata_from_minio import download_raw_data

download_raw_data()
