from minio import Minio # Client để kết nối với Minio
from io import BytesIO # tạo file ảo trong ram không cần ghi xuống disk
from typing import Iterator, Tuple 
from pathlib import Path

import sys
# Thêm thư mục gốc vào Python path
ROOT_DIR = Path(__file__).parent.parent.parent  # Lên 3 cấp từ loader.py
sys.path.insert(0, str(ROOT_DIR))
from core.setting_loader import load_settings
# Cấu hình minio từ settings
settings = load_settings()
minio_config = settings['minio']
bucket_name = minio_config['minio_bucket_name']

# Khởi tạo minio client

def create_minio_client() ->Minio:
    return Minio(
        minio_config['minio_endpoint'], # địa chỉ của minio server
        access_key = minio_config['minio_username'],
        secret_key = minio_config['minio_password'],
        secure=False # HTTP thay vì HTTPS
    )

# get data 
def get_data_from_minio(
        prefix: str = "raw_data/", # Thư mục logic trong bucket (pdf, jsson,...)
        stream_chunk_size: int = 64*1024, # 64KB -> đọc mỗi lần 64KB để tránh tràn ram
) -> Iterator[Tuple[str, BytesIO]]: # trả về tuple gồm tên file và nội dung dạng ByteIO
    
    # List objectr trong bucket (pdf, json,...)
    client = create_minio_client()
    objects = client.list_objects(
        bucket_name,
        prefix=prefix,
        recursive=True # đệ quy vào các thư mục con
    )

    # đọc từng object vào ram
    for obj in objects:
        response = client.get_object(bucket_name, obj.object_name)
        # streaming vào byteIO 
        try:
            buffer = BytesIO() # tạo file ảo trong ram
            # đọc từng chunk 64kb -> tránh tràn ram
            for data in response.stream(stream_chunk_size):
                buffer.write(data)
            
            buffer.seek(0) # reset con trở về đầu file
            yield obj.object_name, buffer
        finally:
            response.close() # đóng stream
            response.release_conn() # giải phóng connect pool
