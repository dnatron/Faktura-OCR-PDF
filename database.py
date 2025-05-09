from sqlmodel import SQLModel, Session, create_engine
from pathlib import Path

# Create database directory if it doesn't exist
DB_DIR = Path("db")
DB_DIR.mkdir(exist_ok=True)

# Database URL
DATABASE_URL = f"sqlite:///{DB_DIR}/invoice_parser.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Create database and tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
