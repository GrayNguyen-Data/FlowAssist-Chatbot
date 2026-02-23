from minio import Minio  # Client để kết nối với Minio
from io import BytesIO  # tạo file ảo trong ram không cần ghi xuống disk
from typing import Iterator, Tuple
from pathlib import Path
import sys

# Thêm thư mục gốc vào Python path
ROOT_DIR = Path(__file__).parent.parent.parent  # Lên 3 cấp từ loader.py
sys.path.insert(0, str(ROOT_DIR))

from core.setting_loader import load_settings


class MinIODataLoader:

    def __init__(self):
        # Cấu hình minio từ settings
        settings = load_settings()
        self.minio_config = settings['minio']
        self.bucket_name = self.minio_config['minio_bucket_name']

        # khởi tạo client
        self.client = self.create_minio_client()

    # Khởi tạo minio client
    def create_minio_client(self) -> Minio:
        return Minio(
            self.minio_config['minio_endpoint'],  # địa chỉ của minio server
            access_key=self.minio_config['minio_username'],
            secret_key=self.minio_config['minio_password'],
            secure=False  # HTTP thay vì HTTPS
        )

    # get data
    def get_data_from_minio(
        self,
        prefix: str = "raw_data/",  # Thư mục logic trong bucket (pdf, json,...)
        stream_chunk_size: int = 64 * 1024,  # 64KB -> đọc mỗi lần 64KB để tránh tràn ram
    ) -> Iterator[Tuple[str, BytesIO]]:

        # List objects trong bucket (pdf, json,...)
        objects = self.client.list_objects(
            self.bucket_name,
            prefix=prefix,
            recursive=True  # đệ quy vào các thư mục con
        )

        # đọc từng object vào ram
        for obj in objects:
            response = self.client.get_object(self.bucket_name, obj.object_name)

            try:
                buffer = BytesIO()  # tạo file ảo trong ram

                # đọc từng chunk 64kb -> tránh tràn ram
                for data in response.stream(stream_chunk_size):
                    buffer.write(data)

                buffer.seek(0)  # reset con trỏ về đầu file
                yield obj.object_name, buffer

            finally:
                response.close()  # đóng stream
                response.release_conn()  # giải phóng connect pool


if __name__ == "__main__":
    loader = MinIODataLoader()

    for name, file_buffer in loader.get_data_from_minio():
        print(name)
