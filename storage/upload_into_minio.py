from minio import Minio
from pathlib import Path
from datetime import datetime
import mimetypes

from core.setting_loader import load_settings

# ===== Load settings =====
settings = load_settings()

# ===== Paths =====
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / settings["data"]["raw_dir"]

# ===== MinIO config =====
minio_cfg = settings["minio"]
MINIO_BUCKET_NAME = minio_cfg["minio_bucket_name"]

# ===== Create MinIO Client =====
def create_minio_client() -> Minio:
    return Minio(
        minio_cfg["minio_endpoint"],
        access_key=minio_cfg["minio_username"],
        secret_key=minio_cfg["minio_password"],
        secure=False,
    )

# ===== Check bucket =====
def check_bucket(client: Minio, bucket_name: str):
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Created bucket: {bucket_name}")

# ===== Upload raw data =====
def upload_raw_data(client: Minio, base_dir: Path):
    if not base_dir.exists():
        raise FileNotFoundError(f"Directory not found: {base_dir}")

    for file_path in base_dir.rglob("*"):
        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(base_dir)
        object_name = f"raw_data/{relative_path}".replace("\\", "/")

        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or "application/octet-stream"

        metadata = {
            "source": "internal",
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_type": file_path.suffix.lstrip("."),
        }

        client.fput_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=object_name,
            file_path=str(file_path),
            content_type=content_type,
            metadata=metadata,
        )

        print(f"Uploaded: {object_name}")

# # ===== Entry point =====
# def main():
#     client = create_minio_client()
#     check_bucket(client, MINIO_BUCKET_NAME)
#     upload_raw_data(client, RAW_DATA_DIR)
#     print("✅ Upload raw_data hoàn tất")
