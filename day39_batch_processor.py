import json
from pathlib import Path
from datetime import datetime
from typing import Dict

from pdf_extractor import process_pdf


def categorize_error(error_msg: str) -> str:
    """Classify failures so we know what to fix."""
    msg = str(error_msg).lower()
    if "password" in msg or "read" in msg:
        return "PDF_READ_ERROR"
    if "extract" in msg or "instructor" in msg or "groq" in msg:
        return "EXTRACTION_ERROR"
    if "validation" in msg or "pydantic" in msg:
        return "VALIDATION_ERROR"
    if "timeout" in msg or "connection" in msg:
        return "TIMEOUT_ERROR"
    return "UNKNOWN_ERROR"


def batch_process(invoice_dir: str = "./invoices") -> Dict:
    """
    Pipeline: Read → Extract → Validate → Store → Report
    Each stage is isolated. Failure in one doesn't kill the batch.
    """
    pdf_files = sorted(Path(invoice_dir).glob("*.pdf"))
    
    results = {
        "processed_at": datetime.utcnow().isoformat(),
        "total_files": len(pdf_files),
        "successful": [],
        "failed": [],
        "summary": {
            "total_invoices": 0,
            "total_value_usd": 0.0,
            "errors_by_type": {}
        }
    }
    
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING: {len(pdf_files)} PDF(s)")
    print("=" * 60)
    
    for pdf_path in pdf_files:
        try:
            invoice = process_pdf(str(pdf_path))
            
            if invoice:
                # Stage: Store success
                record = {
                    "file": pdf_path.name,
                    "invoice_number": invoice.invoice_number,
                    "vendor": invoice.vendor_name,
                    "date": str(invoice.invoice_date),
                    "total_due": invoice.total_due,
                    "currency": invoice.currency,
                    "line_items": len(invoice.line_items)
                }
                results["successful"].append(record)
                
                # Rough EUR→USD for summary
                rate = 1.1 if invoice.currency == "EUR" else 1.0
                results["summary"]["total_value_usd"] += invoice.total_due * rate
                
            else:
                # Stage: Log extraction failure
                err = {
                    "file": pdf_path.name,
                    "error_type": "EXTRACTION_ERROR",
                    "error": "process_pdf returned None",
                    "stage": "extraction"
                }
                results["failed"].append(err)
                results["summary"]["errors_by_type"]["EXTRACTION_ERROR"] = \
                    results["summary"]["errors_by_type"].get("EXTRACTION_ERROR", 0) + 1
                
        except Exception as e:
            # Stage: Catch unexpected, categorize, continue
            error_type = categorize_error(e)
            err = {
                "file": pdf_path.name,
                "error_type": error_type,
                "error": str(e),
                "stage": "unknown"
            }
            results["failed"].append(err)
            results["summary"]["errors_by_type"][error_type] = \
                results["summary"]["errors_by_type"].get(error_type, 0) + 1
    
    # Finalize
    results["summary"]["total_invoices"] = len(results["successful"])
    
    # Persist results
    with open("batch_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    return results


def print_report(results: Dict):
    """Human-readable summary."""
    print(f"\n{'='*60}")
    print("BATCH REPORT")
    print("=" * 60)
    
    success = results["successful"]
    failed = results["failed"]
    
    print(f"\nTotal files:  {results['total_files']}")
    print(f"Successful:   {len(success)}")
    print(f"Failed:       {len(failed)}")
    
    if success:
        print(f"\n--- Successful ---")
        for r in success:
            print(f"  {r['invoice_number']} | {r['vendor'][:20]:20} | ${r['total_due']} {r['currency']}")
    
    if failed:
        print(f"\n--- Failures ---")
        for r in failed:
            print(f"  {r['file']} | {r['error_type']}")
    
    print(f"\nTotal value (USD approx): ${results['summary']['total_value_usd']:.2f}")
    print(f"Results saved to: batch_results.json")


if __name__ == "__main__":
    results = batch_process("./invoices")
    print_report(results)