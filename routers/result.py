# Router pro zpracování a zobrazení výsledků faktur

# Import potřebných knihoven
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks  # Základní FastAPI komponenty
from fastapi.responses import HTMLResponse  # Pro vrácení HTML odpovědí
from fastapi.templating import Jinja2Templates  # Pro práci s šablonami
from sqlmodel import Session, select  # Pro práci s databází
from typing import Optional  # Pro volitelné parametry
import os  # Pro práci se soubory

# Import modelů a funkcí
from models.upload import Upload  # Model pro nahrané soubory
from models.result import InvoiceResult  # Model pro výsledky zpracování
from database import get_session  # Funkce pro získání databázové session
from utils import process_invoice  # Funkce pro zpracování faktur

# Vytvoření routeru a šablon
router = APIRouter()  # Router pro registraci endpointů
templates = Jinja2Templates(directory="templates")  # Šablony z adresáře templates

@router.get("/result/{upload_id}", response_class=HTMLResponse)
async def get_result(
    request: Request,  # Požadavek od klienta
    upload_id: int,  # ID nahraného souboru z URL
    session: Session = Depends(get_session)  # Databázová session (automaticky získána)
):
    """Získá a zobrazí výsledek zpracování faktury
    
    Tento endpoint zobrazuje buď výsledek zpracování faktury, pokud je již k dispozici,
    nebo stránku s informací o probíhajícím zpracování.
    """
    # Získání informací o nahraném souboru
    upload = session.get(Upload, upload_id)  # Nahrání záznamu podle ID
    if not upload:
        # Pokud soubor neexistuje, vrátíme chybu 404
        raise HTTPException(status_code=404, detail="Soubor nebyl nalezen")
    
    # Kontrola, zda existuje výsledek zpracování
    result = session.exec(
        select(InvoiceResult).where(InvoiceResult.upload_id == upload_id)  # Vyhledání podle upload_id
    ).first()  # Získání prvního (a jediného) výsledku
    
    # Vrácení odpovídající šablony podle stavu zpracování
    if result:
        # Pokud výsledek existuje, zobrazíme ho
        return templates.TemplateResponse(
            "result.html",  # Použitá šablona
            {
                "request": request,  # Požadavek (vyžadováno Jinja2)
                "upload": upload,  # Informace o nahraném souboru
                "result": result,  # Výsledek zpracování
                "processing": False  # Indikace, že zpracování je dokončeno
            }
        )
    else:
        # Pokud výsledek ještě neexistuje, zobrazíme stránku s informací o zpracování
        return templates.TemplateResponse(
            "result.html",  # Použitá šablona
            {
                "request": request,  # Požadavek (vyžadováno Jinja2)
                "upload": upload,  # Informace o nahraném souboru
                "processing": True  # Indikace, že zpracování stále probíhá
            }
        )

@router.post("/process/{upload_id}")
async def process_upload(
    upload_id: int,  # ID nahraného souboru z URL
    background_tasks: BackgroundTasks,  # Pro spuštění úloh na pozadí
    model: Optional[str] = "llama3",  # Volitelný parametr pro výběr AI modelu
    session: Session = Depends(get_session)  # Databázová session (automaticky získána)
):
    """Zpracuje nahraný soubor na pozadí pomocí OCR a AI
    
    Tento endpoint spouští zpracování faktury jako úlohu na pozadí,
    takže uživatel nemusí čekat na dokončení zpracování.
    """
    # Získání informací o nahraném souboru
    upload = session.get(Upload, upload_id)  # Nahrání záznamu podle ID
    if not upload:
        # Pokud soubor neexistuje, vrátíme chybu 404
        raise HTTPException(status_code=404, detail="Soubor nebyl nalezen")
    
    # Kontrola, zda soubor fyzicky existuje na disku
    if not os.path.exists(upload.file_path):
        # Pokud soubor neexistuje na disku, vrátíme chybu 404
        raise HTTPException(status_code=404, detail="Soubor nebyl nalezen na disku")
    
    # Přidání úlohy zpracování na pozadí
    background_tasks.add_task(
        process_invoice,  # Funkce, která bude spuštěna na pozadí
        upload_id=upload_id,  # ID nahraného souboru
        file_path=upload.file_path,  # Cesta k souboru
        model=model  # Použitý AI model
    )
    
    # Vrácení informace o zahájení zpracování
    return {"status": "processing", "upload_id": upload_id}

@router.get("/api/result/{upload_id}")
async def get_result_api(
    upload_id: int,  # ID nahraného souboru z URL
    session: Session = Depends(get_session)  # Databázová session (automaticky získána)
):
    """API endpoint pro získání výsledku zpracování
    
    Tento endpoint vrací výsledek zpracování faktury ve formátu JSON.
    Používá se pro AJAX požadavky z frontendu pro kontrolu stavu zpracování.
    """
    # Získání informací o nahraném souboru
    upload = session.get(Upload, upload_id)  # Nahrání záznamu podle ID
    if not upload:
        # Pokud soubor neexistuje, vrátíme chybu 404
        raise HTTPException(status_code=404, detail="Soubor nebyl nalezen")
    
    # Kontrola, zda existuje výsledek zpracování
    result = session.exec(
        select(InvoiceResult).where(InvoiceResult.upload_id == upload_id)  # Vyhledání podle upload_id
    ).first()  # Získání prvního (a jediného) výsledku
    
    if result:
        # Pokud výsledek existuje, převedeme ho na slovník a vrátíme
        result_dict = {
            "id": result.id,  # ID výsledku
            "upload_id": result.upload_id,  # ID nahraného souboru
            "invoice_number": result.invoice_number,  # Číslo faktury
            "invoice_date": result.invoice_date.isoformat() if result.invoice_date else None,  # Datum vystavení
            "due_date": result.due_date.isoformat() if result.due_date else None,  # Datum splatnosti
            "total_amount": result.total_amount,  # Celková částka
            "vat_amount": result.vat_amount,  # Částka DPH
            "currency": result.currency,  # Měna
            "supplier_name": result.supplier_name,  # Název dodavatele
            "supplier_tax_id": result.supplier_tax_id,  # IČO dodavatele
            "supplier_vat_id": result.supplier_vat_id,  # DIČ dodavatele
            "customer_name": result.customer_name,  # Název odběratele
            "customer_tax_id": result.customer_tax_id,  # IČO odběratele
            "customer_vat_id": result.customer_vat_id,  # DIČ odběratele
            "processed_date": result.processed_date.isoformat(),  # Datum zpracování
            "confidence_score": result.confidence_score,  # Skóre spolehlivosti
            "llm_model_used": result.llm_model_used  # Použitý AI model
        }
        return result_dict  # Vrácení výsledku jako JSON
    else:
        # Pokud výsledek ještě neexistuje, vrátíme informaci o zpracování
        return {"status": "processing", "upload_id": upload_id}
