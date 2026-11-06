import os
from typing import Annotated
from langchain.tools import tool
from LLM.llm import GetCloudLLM


@tool
def convert_document_or_image_llm(
    file_path: Annotated[str, "Absolute or relative path to the document, PDF page, or image file."],
    extraction_prompt: Annotated[str, "Instructions for what to extract or summarize from the file."] = "Extract all text, tables, and structured data accurately and present in clean Markdown format."
) -> str:
    """
    Leverages LLM vision and multimodal capabilities to read, transcribe, and structure content 
    from images, scanned documents, charts, or complex PDFs.
    """
    if not os.path.exists(file_path):
        return f"[ERROR] File not found: {file_path}"
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        llm = GetCloudLLM()
        
        # If it's an image, pass as multimodal input if supported, or read via PIL/bytes
        if ext in [".png", ".jpg", ".jpeg", ".webp"]:
            import base64
            with open(file_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            from langchain_core.messages import HumanMessage
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": extraction_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{ext.replace('.', '')};base64,{encoded_image}"}
                    }
                ]
            )
            response = llm.invoke([message])
            return response.content
            
        else:
            # For text documents or PDFs where Python extractor was insufficient
            # Fallback to reading raw bytes/text or utilizing helper extraction
            with open(file_path, "rb") as f:
                content_bytes = f.read()
            
            prompt = f"{extraction_prompt}\nFile: {file_path}\nContent (binary/raw representation or preview): {content_bytes[:2000]}"
            response = llm.invoke(prompt)
            return response.content
            
    except Exception as e:
        return f"[ERROR] LLM-based document conversion failed: {str(e)}"


@tool
def analyze_complex_form_or_invoice_llm(
    file_path: Annotated[str, "Path to invoice, receipt, or structured form image/PDF."],
) -> str:
    """Extract key-value pairs, line items, totals, and metadata from invoices, receipts, or forms using LLM reasoning."""
    prompt = (
        "Analyze this document/invoice/receipt thoroughly. Extract all key information "
        "including vendor details, date, invoice number, line items with prices, taxes, and total amount. "
        "Format the output clearly as structured Markdown."
    )
    return convert_document_or_image_llm.invoke({"file_path": file_path, "extraction_prompt": prompt})
