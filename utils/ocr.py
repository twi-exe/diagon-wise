import fitz  # PyMuPDF
from PIL import Image
import pytesseract

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = "\n".join([page.get_text() for page in doc])
    return text

def extract_text_from_image(path):
    image = Image.open(path)
    return pytesseract.image_to_string(image)
