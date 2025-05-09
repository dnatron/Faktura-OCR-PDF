# Model pro ukládání výsledků zpracování faktur

# Import potřebných knihoven
from sqlmodel import Field, SQLModel  # SQLModel pro práci s databází
from typing import Optional  # Pro volitelné hodnoty
from datetime import datetime  # Pro práci s datem a časem

class InvoiceResult(SQLModel, table=True):
    """Model pro ukládání výsledků zpracování faktur
    
    Ukládá všechny extrahované informace z faktury po zpracování pomocí OCR a AI.
    Každý záznam je propojen s nahraným souborem pomocí upload_id.
    """
    # Základní identifikátor (primární klíč)
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Odkaz na nahraný soubor (cizí klíč)
    upload_id: int = Field(foreign_key="upload.id")
    
    # Číslo faktury
    invoice_number: Optional[str] = None
    
    # Datum vystavení faktury
    invoice_date: Optional[datetime] = None
    
    # Datum splatnosti faktury
    due_date: Optional[datetime] = None
    
    # Celková částka k úhradě
    total_amount: Optional[float] = None
    
    # Částka DPH
    vat_amount: Optional[float] = None
    
    # Měna (např. CZK, EUR, USD)
    currency: Optional[str] = None
    
    # Název dodavatele
    supplier_name: Optional[str] = None
    
    # IČO dodavatele
    supplier_tax_id: Optional[str] = None
    
    # DIČ dodavatele
    supplier_vat_id: Optional[str] = None
    
    # Název odběratele
    customer_name: Optional[str] = None
    
    # IČO odběratele
    customer_tax_id: Optional[str] = None
    
    # DIČ odběratele
    customer_vat_id: Optional[str] = None
    
    # Datum a čas zpracování faktury (automaticky vyplněno)
    processed_date: datetime = Field(default_factory=datetime.now)
    
    # Extrahovaný text z faktury (výstup OCR)
    raw_text: Optional[str] = None
    
    # Použitý AI model pro zpracování (např. llama3, mistral)
    llm_model_used: Optional[str] = None
    
    # Skóre spolehlivosti extrakce (0.0 až 1.0)
    confidence_score: Optional[float] = None
    
    def __repr__(self):
        """Textová reprezentace objektu pro ladění"""
        return f"<InvoiceResult {self.id}: {self.invoice_number}>"
