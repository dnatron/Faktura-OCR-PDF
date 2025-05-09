from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional
import os

from models.upload import Upload
from models.result import InvoiceResult
from database import get_session
from utils import process_invoice

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/result/{upload_id}", response_class=HTMLResponse)
async def get_result(
    request: Request,
    upload_id: int,
    session: Session = Depends(get_session)
):
    """Get processing result for an upload"""
    # Get upload
    upload = session.get(Upload, upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Check if result exists
    result = session.exec(
        select(InvoiceResult).where(InvoiceResult.upload_id == upload_id)
    ).first()
    
    # Return appropriate template
    if result:
        return templates.TemplateResponse(
            "result.html", 
            {
                "request": request,
                "upload": upload,
                "result": result,
                "processing": False
            }
        )
    else:
        return templates.TemplateResponse(
            "result.html", 
            {
                "request": request,
                "upload": upload,
                "processing": True
            }
        )

@router.post("/process/{upload_id}")
async def process_upload(
    upload_id: int,
    background_tasks: BackgroundTasks,
    model: Optional[str] = "llama3",
    session: Session = Depends(get_session)
):
    """Process an uploaded file in the background"""
    # Get upload
    upload = session.get(Upload, upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Check if file exists
    if not os.path.exists(upload.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Add processing task to background
    background_tasks.add_task(
        process_invoice,
        upload_id=upload_id,
        file_path=upload.file_path,
        model=model
    )
    
    return {"status": "processing", "upload_id": upload_id}

@router.get("/api/result/{upload_id}")
async def get_result_api(
    upload_id: int,
    session: Session = Depends(get_session)
):
    """API endpoint to get processing result"""
    # Get upload
    upload = session.get(Upload, upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Check if result exists
    result = session.exec(
        select(InvoiceResult).where(InvoiceResult.upload_id == upload_id)
    ).first()
    
    if result:
        # Convert to dict and return
        result_dict = {
            "id": result.id,
            "upload_id": result.upload_id,
            "invoice_number": result.invoice_number,
            "invoice_date": result.invoice_date.isoformat() if result.invoice_date else None,
            "due_date": result.due_date.isoformat() if result.due_date else None,
            "total_amount": result.total_amount,
            "vat_amount": result.vat_amount,
            "currency": result.currency,
            "supplier_name": result.supplier_name,
            "supplier_tax_id": result.supplier_tax_id,
            "supplier_vat_id": result.supplier_vat_id,
            "customer_name": result.customer_name,
            "customer_tax_id": result.customer_tax_id,
            "customer_vat_id": result.customer_vat_id,
            "processed_date": result.processed_date.isoformat(),
            "confidence_score": result.confidence_score,
            "llm_model_used": result.llm_model_used
        }
        return result_dict
    else:
        return {"status": "processing", "upload_id": upload_id}
