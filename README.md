# Faktura OCR PDF

Aplikace pro automatické zpracování faktur pomocí OCR a AI. Umožňuje nahrát PDF faktury nebo obrázky faktur, extrahovat z nich text pomocí OCR a následně zpracovat data pomocí AI modelu pro získání strukturovaných informací a jejich uložení do databáze.

## Technologický stack

- **Backend**: FastAPI, SQLModel, Python 3.11+
- **Frontend**: Jinja2 šablony, HTMX, moderní CSS
- **Databáze**: SQLite (s možností snadné migrace na jiné databáze)
- **OCR**: Tesseract OCR, PyMuPDF
- **AI zpracování**: Ollama (LLM modely jako llama3, mistral)
- **Deployment**: Docker, Docker Compose

## Funkce aplikace

- Nahrávání PDF faktur a obrázků faktur
- OCR zpracování pro extrakci textu
- AI analýza pro extrakci strukturovaných dat:
  - Číslo faktury
  - Datum vystavení a splatnosti
  - Celková částka a DPH
  - Údaje o dodavateli a odběrateli
  - a další...
- Ukládání a správa zpracovaných faktur
- Responzivní uživatelské rozhraní

## Struktura projektu

```
├── models/             # SQLModel modely
│   ├── upload.py       # Model pro nahrané soubory
│   └── result.py       # Model pro výsledky zpracování
├── routers/            # FastAPI routery
│   ├── upload.py       # Endpointy pro nahrávání souborů
│   └── result.py       # Endpointy pro zpracování a výsledky
├── templates/          # Jinja2 šablony
│   ├── base.html       # Základní šablona
│   ├── upload.html     # Formulář pro nahrávání
│   └── result.html     # Zobrazení výsledků
├── static/             # Statické soubory
│   ├── css/            # CSS styly
│   └── js/             # JavaScript soubory
├── main.py             # Hlavní FastAPI aplikace
├── utils.py            # Pomocné funkce (OCR, AI)
├── database.py         # Konfigurace databáze
├── run.py              # Spouštěcí skript
├── docker-compose.yml  # Docker Compose konfigurace
├── Dockerfile          # Docker konfigurace
└── requirements.txt    # Python závislosti
```

## Instalace a spuštění

### Požadavky

- Python 3.11+
- Docker a Docker Compose (pro produkční nasazení)
- Tesseract OCR (pro lokální vývoj)

### Lokální vývoj (bez Dockeru)

1. Nainstalujte Tesseract OCR:
   ```bash
   # macOS
   brew install tesseract tesseract-lang
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-ces
   ```

2. Nainstalujte Python závislosti:
   ```bash
   pip install -r requirements.txt
   ```

3. Spusťte aplikaci:
   ```bash
   python3 run.py --reload
   ```

4. Otevřete aplikaci v prohlížeči: http://localhost:8000

**Poznámka**: Při lokálním spuštění nebudou fungovat funkce AI zpracování, protože ty vyžadují Ollama server.

### Produkční nasazení (s Dockerem)

1. Spusťte aplikaci pomocí Docker Compose:
   ```bash
   docker compose up -d
   ```

2. Stáhněte model pro Ollama:
   ```bash
   docker exec -it ollama ollama pull llama3
   # nebo
   docker exec -it ollama ollama pull mistral
   ```

3. Otevřete aplikaci v prohlížeči: http://localhost:8000

4. Sledujte logy:
   ```bash
   docker compose logs -f
   ```

### Aktualizace aplikace

Po změně kódu je potřeba restartovat kontejnery:

```bash
docker compose down
docker compose up --build -d
```

## Konfigurace

Aplikace používá standardní konfiguraci, kterou lze upravit v příslušných souborech:

- **Database**: Upravte `database.py` pro změnu databázového připojení
- **Ollama**: Upravte `docker-compose.yml` pro změnu konfigurace Ollama serveru
- **OCR**: Upravte `utils.py` pro změnu nastavení OCR

## Licence

Tento projekt je licencován pod MIT licencí.
