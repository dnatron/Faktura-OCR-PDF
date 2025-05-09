# Soubor pro konfiguraci a práci s databází

# Import potřebných knihoven
from sqlmodel import SQLModel, Session, create_engine  # SQLModel pro práci s databází
from pathlib import Path  # Pro práci s cestami k souborům

# Vytvoření adresáře pro databázi, pokud neexistuje
DB_DIR = Path("db")  # Cesta k adresáři s databází
DB_DIR.mkdir(exist_ok=True)  # Vytvoření adresáře (pokud již existuje, nic se nestane)

# URL pro připojení k databázi (SQLite)
DATABASE_URL = f"sqlite:///{DB_DIR}/invoice_parser.db"  # Používáme SQLite databázi v souboru

# Vytvoření databázového engine
# echo=False - nevypisuje SQL dotazy do konzole
# connect_args={"check_same_thread": False} - umožňuje přístup z různých vláken (potřebné pro FastAPI)
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Vytvoří databázi a tabulky podle definovaných modelů
    
    Tato funkce se volá při startu aplikace a zajistí, že všechny potřebné tabulky existují.
    """
    SQLModel.metadata.create_all(engine)  # Vytvoří všechny tabulky definované v modelech

def get_session():
    """Získá databázovou session pro práci s databází
    
    Používá se jako závislost v FastAPI endpointech pro přístup k databázi.
    Funkce je generator, který automaticky uzavře session po dokončení požadavku.
    """
    with Session(engine) as session:  # Automaticky uzavře session po dokončení bloku
        yield session  # Vrátí session a čeká na dokončení požadavku
