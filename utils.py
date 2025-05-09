import os
import json
import requests
from datetime import datetime
import tempfile
import mimetypes
import logging
from typing import Optional, Dict, Any, List
import re

# For PDF processing
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

# For database operations
from sqlmodel import Session
from models.upload import Upload
from models.result import InvoiceResult
from database import engine

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

# Ollama API settings
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_API_URL = f"{OLLAMA_HOST}/api/generate"

def get_mime_type(file_path: str) -> str:
    """Get MIME type of a file"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        text = ""
        # Open the PDF
        with fitz.open(pdf_path) as pdf_document:
            # Iterate through each page
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_image(image_path: str) -> str:
    """Extract text from image using Tesseract OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='ces+eng')
        return text
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        return ""

def extract_images_from_pdf(pdf_path: str) -> List[str]:
    """Extract images from PDF and save them to temporary files"""
    image_paths = []
    
    try:
        with fitz.open(pdf_path) as pdf_document:
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                
                # Get images from the page
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Save image to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                        temp_file.write(image_bytes)
                        image_paths.append(temp_file.name)
    
    except Exception as e:
        logger.error(f"Error extracting images from PDF: {e}")
    
    return image_paths

def process_invoice(upload_id: int, file_path: str, model: str = "llama3") -> None:
    """Process an invoice file using OCR and LLM"""
    try:
        # Get session
        with Session(engine) as session:
            # Get upload
            upload = session.get(Upload, upload_id)
            if not upload:
                logger.error(f"Upload {upload_id} not found")
                return
            
            # Extract text based on file type
            mime_type = get_mime_type(file_path)
            extracted_text = ""
            
            if mime_type.startswith("application/pdf"):
                # Extract text from PDF
                pdf_text = extract_text_from_pdf(file_path)
                extracted_text += pdf_text
                
                # If text is too short, try extracting from images in the PDF
                if len(pdf_text.strip()) < 100:
                    logger.info("PDF text is short, extracting images from PDF")
                    image_paths = extract_images_from_pdf(file_path)
                    
                    for img_path in image_paths:
                        img_text = extract_text_from_image(img_path)
                        extracted_text += f"\n\n{img_text}"
                        
                        # Clean up temporary image file
                        try:
                            os.unlink(img_path)
                        except Exception:
                            pass
            
            elif mime_type.startswith("image/"):
                # Extract text from image
                extracted_text = extract_text_from_image(file_path)
            
            # Process extracted text with LLM
            if extracted_text:
                invoice_data = process_text_with_llm(extracted_text, model)
                
                # Create result
                result = InvoiceResult(
                    upload_id=upload_id,
                    invoice_number=invoice_data.get("invoice_number"),
                    invoice_date=parse_date(invoice_data.get("invoice_date")),
                    due_date=parse_date(invoice_data.get("due_date")),
                    total_amount=parse_float(invoice_data.get("total_amount")),
                    vat_amount=parse_float(invoice_data.get("vat_amount")),
                    currency=invoice_data.get("currency"),
                    supplier_name=invoice_data.get("supplier_name"),
                    supplier_tax_id=invoice_data.get("supplier_tax_id"),
                    supplier_vat_id=invoice_data.get("supplier_vat_id"),
                    customer_name=invoice_data.get("customer_name"),
                    customer_tax_id=invoice_data.get("customer_tax_id"),
                    customer_vat_id=invoice_data.get("customer_vat_id"),
                    raw_text=extracted_text,
                    llm_model_used=model,
                    confidence_score=invoice_data.get("confidence_score", 0.7)
                )
                
                session.add(result)
                
                # Update upload status
                upload.processed = True
                session.add(upload)
                
                session.commit()
                logger.info(f"Invoice {upload_id} processed successfully")
            else:
                logger.error(f"No text extracted from file {file_path}")
    
    except Exception as e:
        logger.error(f"Error processing invoice: {e}")

def process_text_with_llm(text: str, model: str) -> Dict[str, Any]:
    """Process extracted text with LLM to extract invoice data"""
    try:
        # Prepare prompt for the LLM
        prompt = f"""
        Analyze the following invoice text and extract these fields in JSON format:
        - invoice_number: The invoice number/ID
        - invoice_date: The date when the invoice was issued (YYYY-MM-DD)
        - due_date: The payment due date (YYYY-MM-DD)
        - total_amount: The total amount to be paid (numeric value only)
        - vat_amount: The VAT/tax amount (numeric value only)
        - currency: The currency code (e.g., CZK, EUR, USD)
        - supplier_name: The name of the supplier/seller
        - supplier_tax_id: The tax ID of the supplier (IČO in Czech Republic)
        - supplier_vat_id: The VAT ID of the supplier (DIČ in Czech Republic)
        - customer_name: The name of the customer/buyer
        - customer_tax_id: The tax ID of the customer (IČO in Czech Republic)
        - customer_vat_id: The VAT ID of the customer (DIČ in Czech Republic)
        - confidence_score: Your confidence in the extraction (0.0 to 1.0)
        
        For each field, if you cannot find the information, set it to null.
        Return only valid JSON without any additional text.
        
        INVOICE TEXT:
        {text}
        """
        
        # Call Ollama API
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            response_data = response.json()
            llm_response = response_data.get("response", "")
            
            # Extract JSON from the response
            try:
                # Find JSON in the response (it might be surrounded by markdown code blocks or other text)
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```|^\s*(\{[\s\S]*\})\s*$', llm_response)
                
                if json_match:
                    json_str = json_match.group(1) or json_match.group(2)
                    invoice_data = json.loads(json_str)
                else:
                    # Try to parse the entire response as JSON
                    invoice_data = json.loads(llm_response)
                
                return invoice_data
            
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from LLM response: {llm_response}")
                return create_empty_invoice_data()
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return create_empty_invoice_data()
    
    except Exception as e:
        logger.error(f"Error processing text with LLM: {e}")
        return create_empty_invoice_data()

def create_empty_invoice_data() -> Dict[str, Any]:
    """Create empty invoice data structure"""
    return {
        "invoice_number": None,
        "invoice_date": None,
        "due_date": None,
        "total_amount": None,
        "vat_amount": None,
        "currency": None,
        "supplier_name": None,
        "supplier_tax_id": None,
        "supplier_vat_id": None,
        "customer_name": None,
        "customer_tax_id": None,
        "customer_vat_id": None,
        "confidence_score": 0.0
    }

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object"""
    if not date_str:
        return None
    
    try:
        # Try different date formats
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If all formats fail, return None
        return None
    
    except Exception:
        return None

def parse_float(value: Optional[str]) -> Optional[float]:
    """Parse string to float"""
    if value is None:
        return None
    
    try:
        # Convert to string if it's not already
        value_str = str(value)
        
        # Remove currency symbols and non-numeric characters except for decimal point/comma
        value_str = re.sub(r'[^\d.,]', '', value_str)
        
        # Replace comma with dot for decimal point
        value_str = value_str.replace(',', '.')
        
        # Convert to float
        return float(value_str)
    
    except (ValueError, TypeError):
        return None
