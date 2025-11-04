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
    return pytesseract.image_to_string(image)
    doc = fitz.open(path)
    text = "\n".join([page.get_text() for page in doc])
    return text

def extract_text_from_image(path):
    image = Image.open(path)
    return pytesseract.image_to_string(image)
