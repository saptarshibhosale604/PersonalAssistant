import os
from typing import Annotated
from langchain.tools import tool

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None

try:
    import openpyxl
except ImportError:
    openpyxl = None

try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None


@tool
def convert_pdf_to_text_python(
    file_path: Annotated[str, "Absolute or relative path to the PDF file."]
) -> str:
    """Extract all text content from a PDF file using pypdf."""
    if not pypdf:
        return "[ERROR] pypdf library is not installed."
    if not os.path.exists(file_path):
        return f"[ERROR] File not found: {file_path}"
    
    try:
        reader = pypdf.PdfReader(file_path)
        extracted_text = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_text.append(f"--- Page {idx + 1} ---\n{text}")
        return "\n\n".join(extracted_text) if extracted_text else "[WARNING] No text extracted from PDF."
    except Exception as e:
        return f"[ERROR] Failed to parse PDF: {str(e)}"


@tool
def convert_docx_to_text_python(
    file_path: Annotated[str, "Absolute or relative path to the Word (.docx) file."]
) -> str:
    """Extract all text paragraphs and tables from a Word (.docx) document."""
    if not docx:
        return "[ERROR] python-docx library is not installed."
    if not os.path.exists(file_path):
        return f"[ERROR] File not found: {file_path}"
    
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells]
                full_text.append(" | ".join(row_text))
        return "\n".join(full_text) if full_text else "[WARNING] No text found in Word document."
    except Exception as e:
        return f"[ERROR] Failed to parse Word document: {str(e)}"


@tool
def convert_xlsx_to_text_python(
    file_path: Annotated[str, "Absolute or relative path to the Excel (.xlsx/.xls) file."]
) -> str:
    """Extract spreadsheet cell contents into formatted CSV/tabular text using openpyxl."""
    if not openpyxl:
        return "[ERROR] openpyxl library is not installed."
    if not os.path.exists(file_path):
        return f"[ERROR] File not found: {file_path}"
    
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheets_output = []
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            sheets_output.append(f"=== Sheet: {sheet_name} ===")
            for row in sheet.iter_rows(values_only=True):
                row_vals = [str(cell) if cell is not None else "" for cell in row]
                if any(row_vals):
                    sheets_output.append(",".join(row_vals))
        return "\n".join(sheets_output) if sheets_output else "[WARNING] Excel workbook is empty."
    except Exception as e:
        return f"[ERROR] Failed to parse Excel spreadsheet: {str(e)}"


@tool
def convert_image_to_text_python(
    file_path: Annotated[str, "Absolute or relative path to the image file (.png, .jpg, .jpeg, etc.)."]
) -> str:
    """Extract text from an image using Tesseract OCR (pytesseract and Pillow)."""
    if not Image or not pytesseract:
        return "[ERROR] Pillow and/or pytesseract libraries are not installed."
    if not os.path.exists(file_path):
        return f"[ERROR] File not found: {file_path}"
    
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip() if text.strip() else "[WARNING] No text detected in image via OCR."
    except Exception as e:
        return f"[ERROR] OCR image processing failed: {str(e)}"


@tool
def convert_document_universal_python(
    file_path: Annotated[str, "Absolute or relative path to any supported file (.pdf, .docx, .xlsx, .png, .jpg)."]
) -> str:
    """Auto-detects file type by extension and executes the appropriate Python-based text extraction tool."""
    if not os.path.exists(file_path):
        return f"[ERROR] File not found: {file_path}"
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return convert_pdf_to_text_python(file_path)
    elif ext in [".docx", ".doc"]:
        return convert_docx_to_text_python(file_path)
    elif ext in [".xlsx", ".xls"]:
        return convert_xlsx_to_text_python(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        return convert_image_to_text_python(file_path)
    else:
        return f"[ERROR] Unsupported file extension '{ext}' for universal conversion."
