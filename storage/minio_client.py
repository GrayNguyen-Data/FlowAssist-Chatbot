from minio import Minio
from core.setting_loader import load_settings

def get_minio():
    settings = load_settings()["minio"]
    return Minio(
        settings["minio_endpoint"],
        access_key=settings["minio_username"],
        secret_key=settings["minio_password"],
        secure=False,
    )
