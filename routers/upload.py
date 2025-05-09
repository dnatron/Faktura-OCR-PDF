# Router pro nahrávání a správu souborů faktur

# Import potřebných knihoven
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request  # Základní FastAPI komponenty
from fastapi.responses import HTMLResponse  # Pro vrácení HTML odpovědí
from fastapi.templating import Jinja2Templates  # Pro práci s šablonami
from sqlmodel import Session, select  # Pro práci s databází
from pathlib import Path  # Pro práci s cestami k souborům
import os  # Pro práci se soubory
import shutil  # Pro kopírování souborů
import uuid  # Pro generování unikátních ID
from datetime import datetime  # Pro práci s datem a časem

# Import modelů a funkcí
from models.upload import Upload  # Model pro nahrané soubory
from database import get_session  # Funkce pro získání databázové session

# Vytvoření routeru a šablon
router = APIRouter()  # Router pro registraci endpointů
templates = Jinja2Templates(directory="templates")  # Šablony z adresáře templates

# Adresář pro ukládání nahraných souborů
UPLOAD_DIR = Path("uploads")  # Cesta k adresáři
UPLOAD_DIR.mkdir(exist_ok=True)  # Vytvoření adresáře (pokud již existuje, nic se nestane)

@router.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    """Zobrazí formulář pro nahrání faktury
    
    Tento endpoint zobrazuje hlavní stránku aplikace s formulářem
    pro nahrání nové faktury a seznamem již nahraných faktur.
    """
    return templates.TemplateResponse("upload.html", {"request": request})  # Vrácení šablony upload.html

@router.post("/upload", response_class=HTMLResponse)
async def upload_file(
    request: Request,  # Požadavek od klienta
    file: UploadFile = File(...),  # Nahraný soubor (povinný parametr)
    session: Session = Depends(get_session)  # Databázová session (automaticky získána)
):
    """Zpracuje nahrání souboru faktury a uloží ho do databáze
    
    Tento endpoint přijímá nahraný soubor faktury (PDF nebo obrázek),
    uloží ho na disk a vytvoří záznam v databázi.
    """
    # Validace typu souboru (pouze PDF a obrázky)
    content_type = file.content_type  # Získání MIME typu souboru
    if not content_type.startswith("application/pdf") and not content_type.startswith("image/"):
        # Pokud není typ souboru povolen, vrátíme chybu 400
        raise HTTPException(status_code=400, detail="Jsou povoleny pouze soubory PDF a obrázky")
    
    # Vytvoření unikátního názvu souboru
    file_ext = os.path.splitext(file.filename)[1]  # Získání přípony souboru
    unique_filename = f"{uuid.uuid4()}{file_ext}"  # Generování unikátního názvu pomocí UUID
    file_path = UPLOAD_DIR / unique_filename  # Sestavení kompletní cesty k souboru
    
    # Uložení souboru na disk
    with open(file_path, "wb") as buffer:  # Otevření souboru pro zápis v binárním režimu
        shutil.copyfileobj(file.file, buffer)  # Kopírování obsahu souboru
    
    # Získání velikosti souboru v bajtech
    file_size = os.path.getsize(file_path)
    
    # Vytvoření záznamu v databázi
    upload = Upload(
        filename=unique_filename,  # Unikátní název souboru v systému
        original_filename=file.filename,  # Původní název souboru od uživatele
        file_path=str(file_path),  # Cesta k souboru na disku
        file_size=file_size,  # Velikost souboru v bajtech
        mime_type=content_type,  # MIME typ souboru
        upload_date=datetime.now(),  # Aktuální datum a čas
        processed=False  # Indikace, že soubor ještě nebyl zpracován
    )
    
    # Uložení záznamu do databáze
    session.add(upload)  # Přidání objektu do session
    session.commit()  # Potvrzení změn v databázi
    session.refresh(upload)  # Načtení aktualizovaného objektu (včetně ID)
    
    # Přesměrování na stránku zpracování
    return templates.TemplateResponse(
        "result.html",  # Použitá šablona
        {
            "request": request,  # Požadavek (vyžadováno Jinja2)
            "upload": upload,  # Informace o nahraném souboru
            "processing": True  # Indikace, že zpracování probíhá
        }
    )

@router.get("/uploads", response_class=HTMLResponse)
async def list_uploads(request: Request, session: Session = Depends(get_session)):
    """Zobrazí seznam všech nahraných souborů
    
    Tento endpoint zobrazuje stránku se seznamem všech nahraných faktur,
    seřazených od nejnovějších po nejstarší.
    """
    # Získání všech nahraných souborů seřazených podle data nahrání (sestupně)
    uploads = session.exec(select(Upload).order_by(Upload.upload_date.desc())).all()
    
    # Vrácení šablony s daty
    return templates.TemplateResponse(
        "upload.html",  # Použitá šablona
        {
            "request": request,  # Požadavek (vyžadováno Jinja2)
            "uploads": uploads  # Seznam nahraných souborů
        }
    )
