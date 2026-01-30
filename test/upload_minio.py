import sys
from pathlib import Path

# thêm thư mục gốc dự án vào sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from storage import upload_into_minio

upload_into_minio.main()
