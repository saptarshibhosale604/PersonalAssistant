"""
Tools Excel Module

Provides LangChain tools for reading, writing, and modifying Excel (.xlsx) files
using pandas and openpyxl, integrated following the project's architecture standards.
"""

import os
import json
from typing import Optional, List, Dict, Any, Annotated
from langchain.tools import tool
import pandas as pd
import openpyxl
from Log.log_utils import PrintFunctionName

@tool("read_excel_file", description="Read data, sheet names, and preview rows from an Excel (.xlsx or .xls) file.")
@PrintFunctionName
def ReadExcelFile(
    file_path: Annotated[str, "Path to the Excel file (.xlsx or .xls)"],
    sheet_name: Annotated[Optional[str], "Specific sheet name to read. If None, reads the active/first sheet and lists all sheets."] = None,
    nrows: Annotated[int, "Number of preview rows to return"] = 10
) -> str:
    """Read data and metadata from an Excel file."""
    try:
        if not os.path.exists(file_path):
            return f"Error: Excel file not found at {file_path}"
        
        # Load workbook sheet names using openpyxl
        wb = openpyxl.load_workbook(file_path, read_only=True)
        sheets = wb.sheetnames
        wb.close()
        
        # Read with pandas
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=nrows)
            summary = f"--- Sheet: {sheet_name} (Preview {nrows} rows) ---\n" + df.to_markdown(index=False)
        else:
            df = pd.read_excel(file_path, nrows=nrows)
            summary = f"Available Sheets in Workbook: {sheets}\n\n--- First Sheet Preview ---\n" + df.to_markdown(index=False)
            
        return f"Successfully read {file_path}.\n{summary}"
    except Exception as e:
        return f"Error reading Excel file: {str(e)}"

@tool("write_excel_file", description="Create or write structured tabular data (JSON list of dicts) into an Excel file (.xlsx).")
@PrintFunctionName
def WriteExcelFile(
    file_path: Annotated[str, "Path where the Excel file should be saved"],
    data_json: Annotated[str, "JSON formatted list of dictionaries or tabular records to write into the Excel file"],
    sheet_name: Annotated[str, "Target sheet name"] = "Sheet1",
    mode: Annotated[str, "Writing mode: 'overwrite' or 'append' to existing file"] = "overwrite"
) -> str:
    """Create or write data into an Excel file."""
    try:
        data = json.loads(data_json)
        df = pd.DataFrame(data)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)) or '.', exist_ok=True)
        
        if mode.lower() == "append" and os.path.exists(file_path):
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
        return f"Successfully wrote {len(df)} rows to {file_path} (Sheet: {sheet_name}, Mode: {mode})."
    except Exception as e:
        return f"Error writing Excel file: {str(e)}"

@tool("inspect_excel_sheets", description="List all sheet names and basic info (row/column counts) for an Excel file.")
@PrintFunctionName
def InspectExcelSheets(
    file_path: Annotated[str, "Path to the Excel file (.xlsx or .xls)"]
) -> str:
    """Inspect all sheets in an Excel workbook."""
    try:
        if not os.path.exists(file_path):
            return f"Error: Excel file not found at {file_path}"
            
        excel_file = pd.ExcelFile(file_path)
        sheet_info = []
        for sheet in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet, nrows=5)
            sheet_info.append(f"- Sheet '{sheet}': {df.shape[1]} columns, sample columns: {list(df.columns)}")
            
        return f"Workbook: {file_path}\nTotal Sheets: {len(excel_file.sheet_names)}\n" + "\n".join(sheet_info)
    except Exception as e:
        return f"Error inspecting Excel file: {str(e)}"


# Export list of tools for toolsManager integration
toolsExcel = [
    ReadExcelFile,
    WriteExcelFile,
    InspectExcelSheets
]

def ToolsList():
    global toolsExcel
    return toolsExcel
