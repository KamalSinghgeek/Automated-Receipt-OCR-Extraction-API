from pdf2image import convert_from_path
import pytesseract
import re
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    # For Windows, specify poppler_path if needed:
    # images = convert_from_path(pdf_path, poppler_path=r'C:\Program Files\poppler-24.08.0\Library\bin')
    images = convert_from_path(pdf_path, poppler_path=r"C:\Program Files\poppler-24.08.0\Library\bin")
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text

def parse_receipt_text(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # --- Step 1: Extract Merchant (as before or skip for now) ---
    merchant_name = None
    for line in lines:
        if re.search(r"receipt|total|amount|thank|invoice|grand|date", line, re.I):
            continue
        merchant_name = line
        break

    # --- Step 2: BEST DATE EXTRACTION GOES HERE ---
    purchased_at = None
    date_candidates = []

    date_patterns = [
    r"(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?)",
    r"(\d{1,2}[-/\.][A-Za-z]{3,9}[-/\.]\d{2,4})",   # NEW: handles 03-June-2025
    r"(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?)",
    r"([A-Za-z]{3,9}\s+\d{1,2},?\s*\d{4})",
    r"(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})",
]
    for pat in date_patterns:
        matches = re.findall(pat, text)
        if matches:
            for dt_str in matches:
                date_candidates.append(dt_str.strip())

    dt_formats = [
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%Y/%m/%d %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d-%m-%Y %H:%M",
    "%m/%d/%Y %H:%M",
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d/%m/%y",
    "%B %d %Y",
    "%b %d %Y",
    "%d %B %Y",
    "%d %b %Y",
    "%d-%B-%Y",        # <<=== handles 03-June-2025
    "%d-%b-%Y"         # <<=== handles 03-Jun-2025
]
    for dt_str in date_candidates:
        for fmt in dt_formats:
            try:
                purchased_at = datetime.strptime(dt_str, fmt)
                break
            except Exception:
                continue
        if purchased_at:
            break

        for pat in date_patterns:
            m = re.search(pat, line)
            if m:
                dt_str = m.group(1).replace(",", "").strip()
                for fmt in (
                    "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y",
                    "%d-%m-%Y", "%d/%m/%y", "%B %d %Y", "%b %d %Y",
                    "%d %B %Y", "%d %b %Y"
                ):
                    try:
                        purchased_at = datetime.strptime(dt_str, fmt)
                        break
                    except Exception:
                        continue
                if purchased_at:
                    break
        if purchased_at:
            break

    # 3. TOTAL AMOUNT EXTRACTION (robust, multi-keyword, bottom-up)
    total_keywords = r"(total|amount due|amount|grand total|sum|balance due|paid|subtotal)"
    amount_pattern = r"([$\u20AC\u00A3]?\s?[\d,]+\.\d{2})"
    total_amount = None
    for line in reversed(lines):
        if re.search(total_keywords, line, re.I):
            m = re.search(amount_pattern, line)
            if m:
                val = m.group(1).replace("$", "").replace("€", "").replace("£", "").replace(",", "").strip()
                try:
                    total_amount = float(val)
                    break
                except Exception:
                    pass
    # Fallback: grab first occurrence of $xx.xx if all else fails
    if total_amount is None:
        m = re.search(amount_pattern, text)
        if m:
            val = m.group(1).replace("$", "").replace("€", "").replace("£", "").replace(",", "").strip()
            try:
                total_amount = float(val)
            except Exception:
                pass

    return {
        "merchant_name": merchant_name[:128] if merchant_name else None,
        "purchased_at": purchased_at,    # a datetime object or None
        "total_amount": total_amount     # a float or None
    }