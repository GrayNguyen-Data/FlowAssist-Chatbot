from minio import Minio
from pathlib import Path
from datetime import datetime
import mimetypes

from core.setting_loader import load_settings


class MinIORawUploader:

    def __init__(self):
        # ===== Load settings =====
        self.settings = load_settings()

        # ===== Paths =====
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.RAW_DATA_DIR = self.BASE_DIR / self.settings["data"]["raw_dir"]

        # ===== MinIO config =====
        self.minio_cfg = self.settings["minio"]
        self.MINIO_BUCKET_NAME = self.minio_cfg["minio_bucket_name"]

        # ===== Create MinIO client =====
        self.client = self.create_minio_client()

    # ===== Create MinIO Client =====
    def create_minio_client(self) -> Minio:
        return Minio(
            self.minio_cfg["minio_endpoint"],
            access_key=self.minio_cfg["minio_username"],
            secret_key=self.minio_cfg["minio_password"],
            secure=False,
        )

    # ===== Check bucket =====
    def check_bucket(self):
        if not self.client.bucket_exists(self.MINIO_BUCKET_NAME):
            self.client.make_bucket(self.MINIO_BUCKET_NAME)
            print(f"Created bucket: {self.MINIO_BUCKET_NAME}")

    # ===== Upload raw data =====
    def upload_raw_data(self, base_dir: Path = None):
        base_dir = base_dir or self.RAW_DATA_DIR

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

            self.client.fput_object(
                bucket_name=self.MINIO_BUCKET_NAME,
                object_name=object_name,
                file_path=str(file_path),
                content_type=content_type,
                metadata=metadata,
            )

            print(f"Uploaded: {object_name}")


if __name__ == "__main__":
    uploader = MinIORawUploader()
    uploader.check_bucket()
    uploader.upload_raw_data()
