"""
Tools Google Workspace Module

Integrates LangChain's prebuilt GmailToolkit and CalendarToolkit 
from langchain_google_community to interact with Google Workspace APIs.
"""

from typing import List, Any
from langchain_google_community import GmailToolkit, CalendarToolkit
from Log.log_utils import PrintFunctionName

@PrintFunctionName
def ToolsList() -> List[Any]:
    """
    Initialize and return combined tools from GmailToolkit and CalendarToolkit.
    """
    combined_tools = []
    try:
        # Initialize Gmail Toolkit
        # Automatically looks for credentials.json / token.json
        gmail_toolkit = GmailToolkit()
        gmail_tools = gmail_toolkit.get_tools()
        combined_tools.extend(gmail_tools)
        print(f"[OK] Loaded GmailToolkit tools: {len(gmail_tools)}")

        # Initialize Calendar Toolkit
        calendar_toolkit = CalendarToolkit()
        calendar_tools = calendar_toolkit.get_tools()
        combined_tools.extend(calendar_tools)
        print(f"[OK] Loaded CalendarToolkit tools: {len(calendar_tools)}")

    except Exception as error:
        print(f"[ERROR] Failed to initialize Google Workspace toolkits: {str(error)}")
        print("  Ensure credentials.json is placed correctly and required packages are installed.")

    return combined_tools
