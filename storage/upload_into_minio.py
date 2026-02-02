from minio import Minio, S3Error
from pathlib import Path 
from datetime import datetime
import dotenv
from dotenv import load_dotenv
import os
import mimetypes
load_dotenv()

# ====== Đường dẫn của dự án ======
from pathlib import Path

# BASE_DIR là thư mục gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent
# DATA_DIR là thư mục con "data" nằm trong dự án
DATA_DIR = BASE_DIR / "data"


# ===== Cấu hình MinIO =====
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USERNAME = os.getenv("MINIO_ROOT_USER")
MINIO_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")

# ===== Khởi tạo MinIO Client =====
def create_minio_client() -> Minio:
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_USERNAME,
        secret_key=MINIO_PASSWORD,
        secure=False)

# ===== Kiểm tra và tạo bucket nếu chưa tồn tại =====
def check_bucket(minio_client: Minio, bucket_name: str):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    else:
        print(f"Bucket '{bucket_name}' already exists.")

# ===== Tải tệp lên MinIO =====
def upload_raw_data_to_minio(client: Minio, base_dir: Path):
    if not base_dir.exists():
        raise FileNotFoundError(f"Directory {base_dir} does not exist.")

    for file_path in base_dir.rglob("*"):
        if file_path.is_file():
            # Lấy đường dẫn tương đối từ DATA_DIR
            relative_path = file_path.relative_to(base_dir)
            # Thêm prefix raw_data/
            object_name = f"raw_data/{relative_path}".replace("\\", "/")

            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or "application/octet-stream"

            metadata = {
                "source": "internal",
                "uploaded_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "file_type": file_path.suffix.replace(".", "")
            }

            client.fput_object(
                bucket_name=MINIO_BUCKET_NAME,
                object_name=object_name,
                file_path=str(file_path),
                content_type=content_type,
                metadata=metadata
            )

            print(f"Uploaded: {object_name}")


# =====================
# Main
# =====================
def main():
    client = create_minio_client()
    check_bucket(client, MINIO_BUCKET_NAME)
    upload_raw_data_to_minio(client, DATA_DIR)
    print("Upload toàn bộ thư mục hoàn tất!")


