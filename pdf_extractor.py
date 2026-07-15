import pdfplumber
from pathlib import Path
from typing import Optional
from text_extractor import extract_invoice, validate_invoice
from invoice_model import Invoice

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    text_parts = []

    try: 
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_parts.append(f"--- Page {i} ---\n{text}")
                
        return "\n\n".join(text_parts) if  text_parts else None

    except Exception as e:
        print(f"[PDF ERROR] {pdf_path}: {e}")
        return None


def extract_tables_from_pdf(pdf_path: str) ->  list:
    tables = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                for table in page_tables:
                    tables.append(tables)
        return tables
    except Exception:
        return []


def process_pdf(pdf_path: str) -> Optional[Invoice]:
    print(f"\n Processing: {pdf_path}")

    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text:
        print(" No text extracted (Scanned image of PDF?)")
        return None

    print(f" Extracted {len(raw_text)} characters")

    invoice = extract_invoice(raw_text)
    if not invoice:
        print(" Extraction failed")
        return None

    report = validate_invoice(invoice)

    print(f"  Invoice #: {invoice.invoice_number}")
    print(f"  Vendor:    {invoice.vendor_name}")
    print(f"  Total:     ${invoice.total_due}")
    print(f"  Valid:     {'YES' if report['valid'] else 'NO'}")

    if not report ["valid"]:
        for issue in report["issue"]:
            print(f"   - {issue}")

    return invoice