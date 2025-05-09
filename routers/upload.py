from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pathlib import Path
import os
import shutil
import uuid
from datetime import datetime

from models.upload import Upload
from database import get_session

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    """Render the upload form"""
    return templates.TemplateResponse("upload.html", {"request": request})

@router.post("/upload", response_class=HTMLResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Handle file upload and store in database"""
    # Validate file type
    content_type = file.content_type
    if not content_type.startswith("application/pdf") and not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only PDF and image files are allowed")
    
    # Create unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create database record
    upload = Upload(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=content_type,
        upload_date=datetime.now(),
        processed=False
    )
    
    session.add(upload)
    session.commit()
    session.refresh(upload)
    
    # Redirect to processing page
    return templates.TemplateResponse(
        "result.html", 
        {
            "request": request, 
            "upload": upload,
            "processing": True
        }
    )

@router.get("/uploads", response_class=HTMLResponse)
async def list_uploads(request: Request, session: Session = Depends(get_session)):
    """List all uploaded files"""
    uploads = session.exec(select(Upload).order_by(Upload.upload_date.desc())).all()
    return templates.TemplateResponse(
        "upload.html", 
        {
            "request": request,
            "uploads": uploads
        }
    )
