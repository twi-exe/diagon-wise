import fitz  # PyMuPDF
from PIL import Image
import pytesseract

# Configure tesseract path for pytesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = "\n".join([page.get_text() for page in doc])
    return text

def extract_text_from_image(path):
    image = Image.open(path)
    # Resize if too large to speed up OCR
    max_size = (2000, 2000)
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return pytesseract.image_to_string(image, timeout=60)
