"""
Day 36 Demo: Extract structured invoice data with Instructor + Groq
"""
import os
import instructor
from groq import Groq
from invoice_model import Invoice
from datetime import date

# Patch Groq client with Instructor
client = instructor.from_groq(Groq(api_key=os.getenv("GROQ_API_KEY")))

# A messy, realistic invoice text
SAMPLE_INVOICE_TEXT = """
ACME Web Services
123 Cloud Lane, San Francisco, CA 94105

INVOICE #INV-2026-0042
Date: July 14, 2026
Due: August 14, 2026

Bill To:
DevStartup Inc.

Line Items:
1. LLM API Optimization Consulting - 10 hours @ $150/hr = $1500
2. Redis Cache Setup - 1 project @ $500 = $500
3. React Dashboard Development - 20 hours @ $120/hr = $2400

Subtotal: $4400
Tax (8.5%): $374
Total Due: $4774
Currency: USD
"""


def extract_invoice(text: str) -> Invoice:
    """
    Send unstructured text to Groq, get back a validated Invoice object.
    """
    print("Sending text to Groq + Instructor...")
    
    invoice = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Fast, free Groq tier
        response_model=Invoice,         # <-- THE MAGIC: forces structured output
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert invoice parser. Extract ALL fields. "
                    "If a field is missing, use null or 0. "
                    "Dates must be in YYYY-MM-DD format. "
                    "Calculate totals accurately."
                )
            },
            {
                "role": "user",
                "content": f"Extract this invoice:\n\n{text}"
            }
        ],
        temperature=0.1,  # Low temp = more deterministic extraction
        max_retries=2     # Instructor retries if validation fails
    )
    
    return invoice


if __name__ == "__main__":
    print("=" * 60)
    print("DAY 36: INSTRUCTOR + PYDANTIC INVOICE MODEL")
    print("=" * 60)
    
    # Extract
    result = extract_invoice(SAMPLE_INVOICE_TEXT)
    
    # Print structured result
    print(f"\nInvoice Number: {result.invoice_number}")
    print(f"Vendor:         {result.vendor_name}")
    print(f"Date:           {result.invoice_date}")
    print(f"Due Date:       {result.due_date}")
    print(f"Subtotal:       ${result.subtotal}")
    print(f"Tax Rate:       {result.tax_rate}")
    print(f"Tax Amount:     ${result.tax_amount}")
    print(f"Total Due:      ${result.total_due}")
    print(f"Currency:       {result.currency}")
    
    print(f"\n--- Line Items ({len(result.line_items)}) ---")
    for i, item in enumerate(result.line_items, 1):
        print(f"{i}. {item.description}")
        print(f"   Qty: {item.quantity} @ ${item.unit_price} = ${item.total}")
    
    # Prove it's a real Pydantic object
    print(f"\n--- Validation ---")
    print(f"Type: {type(result).__name__}")
    print(f"JSON: {result.model_dump_json(indent=2)[:200]}...")
    
    # Try to break it (this would crash with raw JSON)
    print(f"\n--- Type Safety ---")
    print(f"total_due is float: {isinstance(result.total_due, float)}")
    print(f"invoice_date is date: {isinstance(result.invoice_date, date)}")