# 🔍 FIR OCR + IPC/BNS Section Recommender

A futuristic Flask-based web application that:

- Extracts text from FIR documents using Optical Character Recognition (OCR)
- Recommends relevant IPC & BNS sections using advanced NLP and semantic similarity

---

## ⚙️ System Requirements

- Python 3.8+
- pip
- Git (optional, for cloning)
- Internet connection (for downloading transformer models)

---

## 🧠 External Tools to Install (EXE Files)

These must be installed on your system for the project to function correctly:

### 1. Tesseract OCR

- 🔧 Used for reading text from images and PDFs.
- 📥 Download: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
- Install location: `C:\Program Files\Tesseract-OCR`
- Add this to your `ocr.py`:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

### 2. Poppler for Windows

- 📄 Used by `pdf2image` to convert PDF pages into images.
- 📥 Download: [https://github.com/oschwartz10612/poppler-windows/releases](https://github.com/oschwartz10612/poppler-windows/releases)
- Extract and add this folder to PATH:
  ```
  C:\Program Files\poppler-24.08.0\Library\bin
  ```

### 3. (Optional) wkhtmltopdf

- 📝 Used to convert HTML content into downloadable PDFs.
- 📥 Download: [https://wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html)
- Install location: `C:\Program Files\wkhtmltopdf\bin`

---

## 🐍 Python Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Pareekshith1/IPC_GPT.git
cd fir-section-recommender
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### `requirements.txt` should include:

```
Flask
pytesseract
pdf2image
pillow
sentence-transformers
torch
pandas
```

---

## 🗂 Project Structure

```
fir-section-recommender/
├── app.py                 # Main Flask app
├── ocr.py                 # OCR extraction logic
├── nlp.py                 # NLP section recommender
├── utils/
│   └── helper.py          # Text cleaner
├── templates/
│   └── index.html         # Upload UI
├── static/
│   ├── css/styles.css
│   ├── js/upload.js
│   └── images/loading.gif
├── ipc_ds.csv             # IPC dataset
├── bns_ds.csv             # BNS dataset
├── uploads/               # Uploaded files
├── README.md
└── requirements.txt
```

---

## 🚀 Running the Project

### 1. Start Flask Server

```bash
flask run
```

### 2. Open in Browser

```
http://127.0.0.1:5000
```

---

## 🔄 Workflow Overview

1. Upload FIR as image or PDF
2. OCR extracts text via Tesseract
3. NLP matches against IPC & BNS datasets
4. UI displays extracted text + top legal section suggestions

---

## ⚠️ Troubleshooting

| Issue                                     | Solution                                               |
| ----------------------------------------- | ------------------------------------------------------ |
| `OCR Error: Tesseract not found`          | Set path in `ocr.py` and ensure Tesseract is installed |
| `Unable to get page count (PDF)`          | Install Poppler and add to system PATH                 |
| `No module named 'sentence_transformers'` | Run `pip install -r requirements.txt`                  |
| `wkhtmltopdf not found`                   | Install it or remove PDF generation code               |

---

## 📄 License

MIT – Do whatever you'd like, just give credit if you're feeling kind 😉
