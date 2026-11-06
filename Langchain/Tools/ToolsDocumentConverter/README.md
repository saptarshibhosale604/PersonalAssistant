# ToolsDocumentConverter Module

## Overview
This module provides comprehensive document, spreadsheet, PDF, and image conversion tools to extract clean text formats for the RPI / JARVIS AI assistant.

It is split into two tactical approaches:
1. **Python-Based (`toolsDocumentConverterPythonBased.py`)**: Fast, programmatic, zero-cost library extraction using `pypdf`, `python-docx`, `openpyxl`, and `pytesseract` (OCR).
2. **LLM-Based (`toolsDocumentConverterLLMBased.py`)**: Intelligent, vision-augmented extraction for complex layouts, scanned documents, handwritten notes, and unstructured data using cloud LLM capabilities.

## System Dependencies
For OCR image extraction in the Python-based module, ensure Tesseract OCR is installed on the host/container:
```bash
apt-get update && apt-get install -y tesseract-ocr
```
