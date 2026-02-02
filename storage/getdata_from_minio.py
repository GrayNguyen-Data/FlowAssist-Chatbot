from minio import Minio
from pathlib import Path

from core.setting_loader import load_settings

# ===== Load settings =====
settings = load_settings()

# ===== Paths =====
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

# ===== MinIO config =====
minio_cfg = settings["minio"]
BUCKET_NAME = minio_cfg["minio_bucket_name"]

# ===== Client =====
def create_minio_client() -> Minio:
    return Minio(
        minio_cfg["minio_endpoint"],
        access_key=minio_cfg["minio_username"],
        secret_key=minio_cfg["minio_password"],
        secure=False,
    )

# ===== Tránh trùng tên =====
def get_unique_filename(directory: Path, filename: str) -> Path:
    path = directory / filename
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    i = 1
    while True:
        new_path = directory / f"{stem}_{i}{suffix}"
        if not new_path.exists():
            return new_path
        i += 1

# ===== Public API =====
def download_raw_data(prefix: str = "raw_data/"):
    client = create_minio_client()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    objects = client.list_objects(
        BUCKET_NAME,
        prefix=prefix,
        recursive=True,
    )

    for obj in objects:
        filename = Path(obj.object_name).name
        local_path = get_unique_filename(OUTPUT_DIR, filename)

        client.fget_object(
            BUCKET_NAME,
            obj.object_name,
            str(local_path),
        )

        print(f"Downloaded: {local_path.name}")

    print("✅ Download xong – tất cả file nằm trong output/")
