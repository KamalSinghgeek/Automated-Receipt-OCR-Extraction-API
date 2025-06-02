from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from database import SessionLocal, init_db
from models import ReceiptFile, Receipt
from ocr_utils import extract_text_from_pdf, parse_receipt_text
import shutil, os
from datetime import datetime

app = FastAPI()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Upload endpoint
@app.post("/upload")
def upload_receipt(file: UploadFile = File(...)):
    # Check file extension
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db = next(get_db())
    # Check duplicate
    existing = db.query(ReceiptFile).filter_by(file_name=file.filename).first()
    if existing:
        existing.updated_at = datetime.utcnow()
        existing.file_path = file_path
        db.commit()
        return {"id": existing.id, "message": "File updated"}
    else:
        receipt_file = ReceiptFile(
            file_name=file.filename,
            file_path=file_path
        )
        db.add(receipt_file)
        db.commit()
        db.refresh(receipt_file)
        return {"id": receipt_file.id, "message": "File uploaded"}

# Validate endpoint
@app.post("/validate")
def validate_receipt(file_name: str):
    db = next(get_db())
    receipt_file = db.query(ReceiptFile).filter_by(file_name=file_name).first()
    if not receipt_file:
        raise HTTPException(status_code=404, detail="File not found")
    try:
        from PyPDF2 import PdfReader
        PdfReader(receipt_file.file_path)
        receipt_file.is_valid = True
        receipt_file.invalid_reason = None
    except Exception as e:
        receipt_file.is_valid = False
        receipt_file.invalid_reason = str(e)
    db.commit()
    return {
        "id": receipt_file.id,
        "is_valid": receipt_file.is_valid,
        "invalid_reason": receipt_file.invalid_reason
    }

# Process endpoint
@app.post("/process")
def process_receipt(file_name: str):
    db = next(get_db())
    receipt_file = db.query(ReceiptFile).filter_by(file_name=file_name).first()
    if not receipt_file:
        raise HTTPException(status_code=404, detail="File not found")
    if not receipt_file.is_valid:
        raise HTTPException(status_code=400, detail="PDF is not valid")
    
    text = extract_text_from_pdf(receipt_file.file_path)
    details = parse_receipt_text(text)

    receipt = db.query(Receipt).filter_by(file_path=receipt_file.file_path).first()
    if receipt:
        receipt.purchased_at = details["purchased_at"]
        receipt.merchant_name = details["merchant_name"]
        receipt.total_amount = details["total_amount"]
        receipt.updated_at = datetime.utcnow()
    else:
        receipt = Receipt(
            purchased_at=details["purchased_at"],
            merchant_name=details["merchant_name"],
            total_amount=details["total_amount"],
            file_path=receipt_file.file_path
        )
        db.add(receipt)
    receipt_file.is_processed = True
    db.commit()
    return {"message": "Receipt processed", "details": details}

# List receipts
@app.get("/receipts")
def list_receipts():
    db = next(get_db())
    receipts = db.query(Receipt).all()
    results = []
    for r in receipts:
        results.append({
            "id": r.id,
            "purchased_at": r.purchased_at,
            "merchant_name": r.merchant_name,
            "total_amount": r.total_amount,
            "file_path": r.file_path
        })
    return results

# Get receipt by id
@app.get("/receipts/{id}")
def get_receipt(id: int):
    db = next(get_db())
    receipt = db.query(Receipt).get(id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": receipt.id,
        "purchased_at": receipt.purchased_at,
        "merchant_name": receipt.merchant_name,
        "total_amount": receipt.total_amount,
        "file_path": receipt.file_path
    }