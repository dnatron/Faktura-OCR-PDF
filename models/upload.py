# Model pro ukládání informací o nahraných souborech

# Import potřebných knihoven
from sqlmodel import Field, SQLModel  # SQLModel pro práci s databází
from typing import Optional  # Pro volitelné hodnoty
from datetime import datetime  # Pro práci s datem a časem

class Upload(SQLModel, table=True):
    """Model pro nahrané soubory faktur
    
    Ukládá informace o nahraných souborech, jako je název souboru,
    cesta k souboru, velikost, typ souboru a stav zpracování.
    """
    # Základní identifikátor (primární klíč)
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Název souboru v systému (unikátní UUID)
    filename: str
    
    # Původní název souboru, jak byl nahrán uživatelem
    original_filename: str
    
    # Cesta k souboru na disku
    file_path: str
    
    # Velikost souboru v bajtech
    file_size: int
    
    # MIME typ souboru (např. application/pdf, image/jpeg)
    mime_type: str
    
    # Datum a čas nahrání souboru (automaticky vyplněno)
    upload_date: datetime = Field(default_factory=datetime.now)
    
    # Indikace, zda byl soubor již zpracován
    processed: bool = Field(default=False)
    
    def __repr__(self):
        """Textová reprezentace objektu pro ladění"""
        return f"<Upload {self.id}: {self.original_filename}>"
