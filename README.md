```markdown
# 🧾 Automated Receipt OCR & Extraction API

## Overview

A FastAPI web application for automated receipt ingestion, OCR processing, and structured data extraction (total, date, merchant) from PDF files. Receipts and extracted info are stored in a local SQLite database, accessible via REST API.

---

## 🚀 Setup Instructions (Windows)

1. **Extract ZIP Archive**

   Unzip the project to a folder of your choice.

2. **(Optional) Create and Activate a Virtual Environment**

   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Python Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Install System Dependencies**

   - **Tesseract OCR**
     - [Download Installer](https://github.com/tesseract-ocr/tesseract)
     - Add the path to `tesseract.exe` (e.g. `C:\Program Files\Tesseract-OCR\`) to your Windows system PATH.
   - **Poppler for PDF-to-Image Conversion**
     - [Download Poppler for Windows](http://blog.alivate.com.au/poppler-windows/)
     - Extract and add the `/bin` folder to your system PATH.

---

## ▶️ Run the API Server

```sh
uvicorn app:app --reload
```

- Open your browser to: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API documentation.

---

## 🔌 API Endpoints

| Endpoint           | Method | Description                        |
|--------------------|--------|------------------------------------|
| `/upload`          | POST   | Upload a PDF receipt               |
| `/validate`        | POST   | Validate an uploaded PDF           |
| `/process`         | POST   | OCR & extract receipt fields       |
| `/receipts`        | GET    | List all extracted receipts        |
| `/receipts/{id}`   | GET    | Get a structured receipt by ID     |

---

## 🧪 Usage Examples

**Upload Receipt**
```sh
curl -F "file=@sample_receipts/receipt1.pdf" http://127.0.0.1:8000/upload
```

**Validate Uploaded PDF**
```sh
curl -X POST -H "Content-Type: application/json" -d "{\"file_name\":\"receipt1.pdf\"}" http://127.0.0.1:8000/validate
```

**Process Receipt (OCR + Extraction)**
```sh
curl -X POST -H "Content-Type: application/json" -d "{\"file_name\":\"receipt1.pdf\"}" http://127.0.0.1:8000/process
```

**List All Receipts**
```sh
curl http://127.0.0.1:8000/receipts
```

**Get Receipt by ID**
```sh
curl http://127.0.0.1:8000/receipts/1
```

---

## 📁 Project Structure

```
accounts-receipts-automation/
│
├── app.py
├── database.py
├── models.py
├── ocr_utils.py
├── requirements.txt
├── README.md
├── receipts.db
├── uploads/            # (stores uploaded PDFs)
└── sample_receipts/    # (varied PDFs for demo/testing)
```

---

## ⚙️ Developer & Execution Tips

- If Poppler is not in your PATH, specify `poppler_path` in `ocr_utils.py`.
- If you see a `database is locked` error, close other tools using `receipts.db`, delete it, and restart the app.
- Uploaded PDFs appear in `/uploads`. Tested sample receipts are in `/sample_receipts`.
- Edit and tune regexes for merchant/date/amount in `ocr_utils.py` for your data.

---

## 📦 Dependencies

- **Python 3.7+**
- **System Tools**
  - Tesseract OCR (Windows)
  - Poppler for Windows
- **Python Packages**
  - `fastapi`
  - `uvicorn`
  - `sqlalchemy`
  - `pydantic`
  - `python-multipart`
  - `pytesseract`
  - `pillow`
  - `pdf2image`
  - `PyPDF2`

---

## 👤 Author

**Kamal Singh**  
GitHub: [KamalSinghgeek](https://github.com/KamalSinghgeek/)  
LinkedIn: [Kamalsingh01](https://www.linkedin.com/in/kamalsingh01/)

---
```
