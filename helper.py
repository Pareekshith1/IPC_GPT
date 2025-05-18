import re

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove newlines and multiple spaces
    return text.strip().lower()













