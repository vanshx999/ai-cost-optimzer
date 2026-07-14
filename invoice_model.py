"""
Day 36: Instructor + Pydantic Invoice Model
Structured extraction with Groq (zero cost).
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class LineItem(BaseModel):
    """One line item on an invoice."""
    description: str = Field(
        description="What the product or service is"
    )
    quantity: int = Field(
        ge=1,
        description="Number of units purchased"
    )
    unit_price: float = Field(
        ge=0,
        description="Price per single unit"
    )
    total: float = Field(
        ge=0,
        description="Quantity * unit_price"
    )


class Invoice(BaseModel):
    """A complete invoice document."""
    invoice_number: str = Field(
        description="Unique identifier like INV-001 or #12345"
    )
    vendor_name: str = Field(
        description="Company or person issuing the invoice"
    )
    vendor_address: Optional[str] = Field(
        default=None,
        description="Full address of the vendor"
    )
    invoice_date: date = Field(
        description="Date the invoice was issued (YYYY-MM-DD)"
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Payment due date if specified"
    )
    line_items: List[LineItem] = Field(
        description="All products/services on this invoice"
    )
    subtotal: float = Field(
        ge=0,
        description="Sum of all line items before tax"
    )
    tax_rate: Optional[float] = Field(
        default=0.0,
        ge=0,
        le=1,
        description="Tax rate as decimal, e.g. 0.08 for 8%"
    )
    tax_amount: float = Field(
        default=0.0,
        ge=0,
        description="Total tax charged"
    )
    total_due: float = Field(
        ge=0,
        description="Final amount the customer must pay"
    )
    currency: str = Field(
        default="USD",
        pattern="^[A-Z]{3}$",
        description="ISO 4217 currency code: USD, EUR, GBP, etc."
    )