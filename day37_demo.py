"""
Day 37 Demo: Real-world text extraction with error handling
"""
from text_extractor import extract_invoice, validate_invoice


# Test 1: Clean invoice
CLEAN = """
CloudOps Inc.
Invoice #INV-7791
Date: 2026-07-10

Services:
- Kubernetes cluster setup: 5 hrs @ $200/hr = $1000
- Monitoring dashboard: 1 project @ $300 = $300
Subtotal: $1300
Tax (10%): $130
Total: $1430 USD
"""

# Test 2: Messy OCR text
MESSY = """
AMAZ0N WEB SERV|CES
lnvoice #AWS-4421
Date: 2026-06-15

1. EC2  t3.medium  720 hrs  @ $0.0416  =  $29.95
2. S3  Standard  50 GB  @ $0.023  =  $1.15
Subtotal:  $31.10
Tax:  $0.00
Total Due:  $31.10
Currency: USD
"""

# Test 3: Partial invoice (missing tax, no due date)
PARTIAL = """
Freelance Dev
Invoice #FL-99
Date: July 5, 2026

Bug fix: 3 hours @ $75 = $225
Total: $225
"""


def run_test(name: str, text: str):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print("-" * 60)
    
    invoice = extract_invoice(text)
    
    if invoice is None:
        print("Result: FAILED EXTRACTION")
        return
    
    # Validate math
    report = validate_invoice(invoice)
    
    print(f"Invoice #:  {invoice.invoice_number}")
    print(f"Vendor:     {invoice.vendor_name}")
    print(f"Date:       {invoice.invoice_date}")
    print(f"Due:        {invoice.due_date or 'Not specified'}")
    print(f"Subtotal:   ${invoice.subtotal}")
    print(f"Tax:        ${invoice.tax_amount} ({invoice.tax_rate*100}%)")
    print(f"Total:      ${invoice.total_due}")
    print(f"Items:      {len(invoice.line_items)}")
    
    if report["valid"]:
        print("Validation: PASSED")
    else:
        print("Validation: ISSUES FOUND")
        for issue in report["issues"]:
            print(f"  - {issue}")


if __name__ == "__main__":
    print("=" * 60)
    print("DAY 37: EXTRACT FROM TEXT VIA INSTRUCTOR")
    print("=" * 60)
    
    run_test("Clean Invoice", CLEAN)
    run_test("Messy OCR", MESSY)
    run_test("Partial Invoice", PARTIAL)
    
    print(f"\n{'='*60}")
    print("Check extraction_failures.jsonl for any logged errors.")