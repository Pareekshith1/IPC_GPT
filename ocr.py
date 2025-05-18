import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os

# Path to Tesseract OCR executable (Windows)
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    text = ""

    try:
        if ext == '.pdf':
            # Convert PDF pages to images (300 DPI) using poppler
            pages = convert_from_path(
                filepath, 
                dpi=300, 
                poppler_path="C:/Program Files/poppler-24.08.0/Library/bin"
            )
            # OCR each page and accumulate text
            for page in pages:
                page_text = pytesseract.image_to_string(page, lang='eng')
                text += page_text + "\n"
        else:
            # Open image file and extract text
            with Image.open(filepath) as image:
                text = pytesseract.image_to_string(image, lang='eng')

    except Exception as e:
        print("OCR Error:", e)
        return "OCR Failed"

    return text.strip()
