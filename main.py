from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path

# Import routers
from routers import upload, result

# Import database
from database import create_db_and_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Faktura OCR PDF",
    description="API pro zpracování faktur pomocí OCR a AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(upload.router)
app.include_router(result.router)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create database and tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("Application started")

@app.on_event("shutdown")
def on_shutdown():
    logger.info("Application shutdown")

# Healthcheck endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
