from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    RapidOcrOptions,
    PictureDescriptionApiOptions
)

# picture_desc = PictureDescriptionApiOptions( model_name="smolvlm" )
# ========================
# 1. Pipeline options - BẬT VISION
# ========================
pipeline_options = PdfPipelineOptions(
    generate_page_images=True,
    images_scale=2.0,
    do_ocr=True,
    do_picture_description=True,
    picture_description_options=PictureDescriptionApiOptions(
        model_name="SmolVLM-Instruct",
        api_base="http://localhost:8000/v1"
    ),
    enable_remote_services=True
)

# ========================
# 2. Converter
# ========================
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)

# ========================
# 3. Convert
# ========================
source = r"D:\FlowAssist-Chatbot\data\pdf\DSGV.pdf"
print("🔄 Đang convert PDF (có thể mất vài phút vì xử lý ảnh)...")
doc = converter.convert(source)
print("✅ Convert xong!")

# ========================
# 4. Export markdown với mô tả ảnh
# ========================
md_text = doc.document.export_to_markdown()

with open("output.md", "w", encoding="utf-8") as f:
    f.write(md_text)

print("✅ DONE – Đã xuất markdown có mô tả ảnh")