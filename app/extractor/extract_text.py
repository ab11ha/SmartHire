import os
import tempfile
import fitz  # PyMuPDF
from docx import Document
from PIL import Image, UnidentifiedImageError
import pytesseract

def extract_text_from_file(file):
    if hasattr(file, "read"):
        suffix = os.path.splitext(file.name)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
    else:
        tmp_path = file

    ext = os.path.splitext(tmp_path)[1].lower()

    try:
        if ext == ".pdf":
            return extract_text_from_pdf(tmp_path).strip()
        elif ext == ".docx":
            return extract_text_from_docx(tmp_path).strip()
        elif ext == ".txt":
            with open(tmp_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        elif ext in [".png", ".jpg", ".jpeg"]:
            return extract_text_from_image(tmp_path).strip()
        else:
            return ""
    except Exception as e:
        print(f"[Error] while reading {tmp_path}: {e}")
        return ""
    finally:
        if hasattr(file, "read") and os.path.exists(tmp_path):
            os.remove(tmp_path)

def extract_text_from_pdf(filepath):
    text = ""
    doc = fitz.open(filepath)
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(filepath):
    try:
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"[Error] reading DOCX: {e}")
        return ""

def extract_text_from_image(filepath):
    try:
        image = Image.open(filepath)
        return pytesseract.image_to_string(image)
    except UnidentifiedImageError:
        return ""
