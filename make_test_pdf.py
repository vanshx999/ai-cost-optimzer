from fpdf import FPDF
import os

os.makedirs("./invoices", exist_ok=True)

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

text = """TECHCORP SOLUTIONS
456 Innovation Drive, Austin, TX 78701

INVOICE #TC-2026-007
Date: July 10, 2026
Due: August 10, 2026

Bill To:
StartupXYZ LLC

Line Items:
1. AI Consulting - 20 hours @ $250/hr = $5000
2. API Integration - 1 project @ $1200 = $1200
3. Code Review - 5 hours @ $150/hr = $750

Subtotal: $6950
Tax (8.25%): $573.38
Total Due: $7523.38
Currency: USD"""

for line in text.split('\n'):
    pdf.cell(200, 10, txt=line, ln=True)

pdf.output("./invoices/test_invoice.pdf")
print("Created ./invoices/test_invoice.pdf")
