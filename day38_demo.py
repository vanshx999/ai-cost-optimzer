from pathlib import Path
from pdf_extractor import process_pdf

if __name__ == "__main__":
    print("=" * 60)
    print("DAY 38: EXTRACT FROM PDF")
    print("=" * 60)
    
    test_files = list(Path("./invoices").glob("*.pdf"))
    print(f"Found {len(test_files)} PDF(s) in ./invoices/")
    
    if not test_files:
        print("No PDFs found. Exiting.")
        exit(0)
    
    results = {"success": 0, "failed": 0}
    
    for pdf_path in test_files:
        invoice = process_pdf(str(pdf_path))
        if invoice:
            results["success"] += 1
        else:
            results["failed"] += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {results['success']} OK, {results['failed']} failed")
    print(f"Total:   {len(test_files)} files")
