from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

class InvoiceResult(SQLModel, table=True):
    """Model for storing invoice parsing results"""
    id: Optional[int] = Field(default=None, primary_key=True)
    upload_id: int = Field(foreign_key="upload.id")
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    total_amount: Optional[float] = None
    vat_amount: Optional[float] = None
    currency: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_tax_id: Optional[str] = None
    supplier_vat_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_tax_id: Optional[str] = None
    customer_vat_id: Optional[str] = None
    processed_date: datetime = Field(default_factory=datetime.now)
    raw_text: Optional[str] = None
    llm_model_used: Optional[str] = None
    confidence_score: Optional[float] = None
    
    def __repr__(self):
        return f"<InvoiceResult {self.id}: {self.invoice_number}>"
