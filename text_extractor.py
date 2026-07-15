"""
Day 37: Extract from Text via Instructor
Handles messy input, missing fields, and extraction failures.
"""
import os
import re
import json
from datetime import date
from typing import Optional

import instructor
from groq import Groq
from invoice_model import Invoice

client = instructor.from_groq(Groq(api_key=os.getenv("GROQ_API_KEY")))


def clean_text(raw: str) -> str:
    """
    Pre-process messy OCR or copy-pasted text.
    """
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', raw)
    
    # Fix common OCR errors
    replacements = {
        '|': 'I',      # pipe vs capital i
        '0': 'O',      # zero vs capital o (context-dependent, but safe for invoices)
        '$': '$',      # normalize currency
        '—': '-',      # em dash to hyphen
        '  ': ' ',     # double spaces
    }
    
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    
    return text.strip()


def extract_invoice(text: str) -> Optional[Invoice]:
    """
    Extract Invoice from raw text. Returns None if extraction fails.
    Logs failures for analysis.
    """
    cleaned = clean_text(text)
    
    try:
        invoice = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_model=Invoice,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert invoice parser. Extract ALL fields accurately. "
                        "If a field is missing, use reasonable defaults or null. "
                        "Dates: YYYY-MM-DD. Currency: 3-letter ISO code. "
                        "Calculate line_item totals and tax_amount correctly."
                    )
                },
                {
                    "role": "user",
                    "content": f"Extract this invoice:\n\n{cleaned}"
                }
            ],
            temperature=0.1,
            max_retries=2
        )
        return invoice
        
    except Exception as e:
        # Log failure for later analysis
        failure_log = {
            "timestamp": str(date.today()),
            "error": str(e),
            "input_preview": cleaned[:200],
            "status": "failed"
        }
        with open("extraction_failures.jsonl", "a") as f:
            f.write(json.dumps(failure_log) + "\n")
        
        print(f"[EXTRACTION FAILED] {e}")
        return None


def validate_invoice(invoice: Invoice) -> dict:
    """
    Post-extraction sanity checks. Returns validation report.
    """
    issues = []
    
    # Math check: subtotal + tax should equal total
    calculated_total = round(invoice.subtotal + invoice.tax_amount, 2)
    if abs(calculated_total - invoice.total_due) > 0.01:
        issues.append(
            f"Math error: {invoice.subtotal} + {invoice.tax_amount} "
            f"= {calculated_total}, but total_due is {invoice.total_due}"
        )
    
    # Line items check
    calculated_subtotal = sum(item.total for item in invoice.line_items)
    if abs(calculated_subtotal - invoice.subtotal) > 0.01:
        issues.append(
            f"Line items sum to {calculated_subtotal}, "
            f"but subtotal is {invoice.subtotal}"
        )
    
    # Date check
    if invoice.due_date and invoice.due_date < invoice.invoice_date:
        issues.append("Due date is before invoice date")
    
    return {
        "valid": len(issues) == 0,
        "invoice_number": invoice.invoice_number,
        "total_due": invoice.total_due,
        "issues": issues
    }
