# Hlavní soubor aplikace pro zpracování faktur pomocí OCR a AI

# Import potřebných knihoven
from fastapi import FastAPI  # Framework pro vytvoření API
from fastapi.staticfiles import StaticFiles  # Pro obsluhu statických souborů (CSS, JS)
from fastapi.middleware.cors import CORSMiddleware  # Pro povolení CORS
import logging  # Pro logování událostí
from pathlib import Path  # Pro práci s cestami k souborům

# Import routerů (směrovačů) pro různé části aplikace
from routers import upload, result  # upload.py - nahrávání souborů, result.py - zpracování a výsledky

# Import funkcí pro práci s databází
from database import create_db_and_tables  # Funkce pro vytvoření databáze a tabulek

# Konfigurace logování - nastavení formátu a místa ukládání logů
logging.basicConfig(
    level=logging.INFO,  # Úroveň logování - INFO a vyšší
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Formát logů
    handlers=[
        logging.FileHandler("app.log"),  # Logy se ukládají do souboru app.log
        logging.StreamHandler()  # Logy se také vypisují do konzole
    ]
)
logger = logging.getLogger(__name__)  # Vytvoření loggeru pro tento soubor

# Vytvoření FastAPI aplikace s metadaty
app = FastAPI(
    title="Faktura OCR PDF",  # Název aplikace
    description="API pro zpracování faktur pomocí OCR a AI",  # Popis aplikace
    version="1.0.0"  # Verze aplikace
)

# Přidání CORS middleware - umožňuje přístup k API z jiných domén
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Povolení přístupu ze všech domén (v produkci by mělo být omezeno)
    allow_credentials=True,  # Povolení předávání cookies
    allow_methods=["*"],  # Povolení všech HTTP metod (GET, POST, atd.)
    allow_headers=["*"],  # Povolení všech HTTP hlaviček
)

# Připojení statických souborů (CSS, JS, obrázky) - budou dostupné na URL /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Připojení routerů (směrovačů) pro různé části aplikace
app.include_router(upload.router)  # Router pro nahrávání souborů
app.include_router(result.router)  # Router pro zpracování a výsledky

# Vytvoření adresáře pro nahrané soubory, pokud neexistuje
UPLOAD_DIR = Path("uploads")  # Cesta k adresáři
UPLOAD_DIR.mkdir(exist_ok=True)  # Vytvoření adresáře (pokud již existuje, nic se nestane)

# Vytvoření databáze a tabulek při startu aplikace
@app.on_event("startup")  # Dekorátor pro událost startu aplikace
def on_startup():
    create_db_and_tables()  # Vytvoření databáze a tabulek
    logger.info("Aplikace byla spuštěna")  # Záznam do logu

# Akce při vypnutí aplikace
@app.on_event("shutdown")  # Dekorátor pro událost vypnutí aplikace
def on_shutdown():
    logger.info("Aplikace byla vypnuta")  # Záznam do logu

# Endpoint pro kontrolu zdraví aplikace (healthcheck)
@app.get("/health")  # Dekorátor pro HTTP GET požadavek na URL /health
async def health_check():
    return {"status": "ok"}  # Vrátí JSON s informací o stavu aplikace
