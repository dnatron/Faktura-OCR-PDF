from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

class Upload(SQLModel, table=True):
    """Model for uploaded invoice files"""
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    upload_date: datetime = Field(default_factory=datetime.now)
    processed: bool = Field(default=False)
    
    def __repr__(self):
        return f"<Upload {self.id}: {self.original_filename}>"
