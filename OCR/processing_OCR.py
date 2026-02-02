from pathlib import Path 

# thư viện để convert data
from docling.document_converter import DocumentConvert, PdfFormatOption

# xác định định dạng dữ liệu (pdf, txt, json,...)
from docling.datamodel.base_models import InputFormat

# import các cấu hình dành cho định dạng pdf
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions, # pipeline các bước xử lý
    RapidOcrOptions # enginee OCR -> sài RapidOcr
)

# import thư viện cho Al xửu lý vision 
from docling.datamodel.pipeline_options import PictureDescriptionApiOptions

picture_desc = PictureDescriptionApiOptions(
    model_name="smolvlm"
)

# ====== Pipeline options - Bật vision =======
pipeline_options = PdfPipelineOptions(
    generate_page_images = True, # mỗi trang sẽ chuyển thành ảnh
    image_scale=1.2, # phóng to ảnh được render từ pdf, scale càng lớn -> OCR càng tốt nhwung nặng
    do_ocr = True, # bật ocr -> cho phép đọc chữ trong ảnh
    do_picture_description = True, # bật vision cho phép mô tả ảnh
    picture_description_options=picture_desc,
    ocr_options = RapidOcrOptions(),
    enable_remote_services=True, # cho phép sử dụng api model
)



