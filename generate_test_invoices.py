import os
from fpdf import FPDF

os.makedirs("./invoices", exist_ok=True)

INVOICES = [
    {
        "filename": "invoice_001_techcorp.pdf",
        "content": """TECHCORP SOLUTIONS
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
    },
    {
        "filename": "invoice_002_design.pdf",
        "content": """PIXEL STUDIO
789 Creative Ave, Brooklyn, NY 11201

INVOICE #PS-2026-112
Date: 2026-06-22
Due: 2026-07-22

Client:
Acme Corp

Services:
- Logo Design: 1 x $800 = $800
- Brand Guidelines: 1 x $1200 = $1200
- Social Media Kit: 1 x $450 = $450

Subtotal: $2450
Tax: $0.00
Total: $2450
Currency: USD"""
    },
    {
        "filename": "invoice_003_cloud.pdf",
        "content": """AWS BILLING
Amazon Web Services, Inc.

Invoice #AWS-8842-A
Date: July 1, 2026

Payer Account:
DevTeam Inc.

Charges:
1. EC2 t3.medium 720 hrs @ $0.0416 = $29.95
2. S3 Standard 500 GB @ $0.023 = $11.50
3. RDS db.t3.micro 720 hrs @ $0.017 = $12.24
4. CloudFront 100 GB @ $0.085 = $8.50

Subtotal: $62.19
Tax (0%): $0.00
Total Due: $62.19
Currency: USD"""
    },
    {

        "filename": "invoice_004_freelance.pdf",
        "content": """FREELANCE DEV
John Developer
john@dev.io

Invoice #FL-99
Date: July 5, 2026

Project: Bug fixes for mobile app
Hours: 12
Rate: $85/hr
Total: $1020

No tax applied.
Currency: USD"""
    },
    {
        "filename": "invoice_005_euro.pdf",
        "content": """BERLIN TECH GMBH
Alexanderplatz 1, 10178 Berlin, Germany

RECHNUNG #BT-2026-445
Datum: 15.07.2026
Fällig: 14.08.2026

Kunde:
European Startup SAS

Positionen:
1. Software Development - 40 Stunden @ 90 EUR/Stunde = 3600 EUR
2. DevOps Setup - 1 Projekt @ 1500 EUR = 1500 EUR

Zwischensumme: 5100 EUR
MwSt (19%): 969 EUR
Gesamtbetrag: 6069 EUR
Währung: EUR"""
    }
]

def make_pdf(filename: str, text: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for line in text.split("\n"):
        pdf.cell(200, 8, txt=line, ln=True)
    path = F"./invoices/{filename}"
    pdf.output(path)
    print(f"Created {path}")


if __name__ == "__main__":
    for inv in INVOICES:
        make_pdf(inv["filename"], inv["content"])
    print(f"\n Done, {len(INVOICES)} invoices in ./invoices")
