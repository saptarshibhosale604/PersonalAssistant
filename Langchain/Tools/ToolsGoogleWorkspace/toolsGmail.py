"""
Tools Gmail Module

Integrates LangChain's prebuilt GmailToolkit from langchain_google_community.
Uses its own OAuth token file so its scope does not collide with Calendar.

--- Available Toolkit Tools (5 total):
    1. create_gmail_draft
    2. send_gmail_message
    3. search_gmail
    4. get_gmail_message
    5. get_gmail_thread

--- Selected Tools (4 total):
    - create_gmail_draft
    - search_gmail
    - get_gmail_message
    - get_gmail_thread
"""

from typing import List, Any
from langchain_google_community import GmailToolkit
from langchain_google_community._utils import get_google_credentials
from langchain_google_community.gmail.utils import build_gmail_service
from Log.log_utils import PrintFunctionName

GMAIL_SCOPES = ["https://mail.google.com/"]
GMAIL_TOKEN_FILE = "./token_gmail.json"

@PrintFunctionName
def ToolsList() -> List[Any]:
    """
    Initialize and return filtered tools from GmailToolkit.
    Selected tools only:
    - create_gmail_draft
    - search_gmail
    - get_gmail_message
    - get_gmail_thread
    """
    selected_tool_names = {
        "create_gmail_draft",
        "search_gmail",
        "get_gmail_message",
        "get_gmail_thread"
    }

    filtered_tools = []
    try:
        credentials = get_google_credentials(scopes=GMAIL_SCOPES, token_file=GMAIL_TOKEN_FILE)
        gmail_toolkit = GmailToolkit(api_resource=build_gmail_service(credentials=credentials))
        all_tools = gmail_toolkit.get_tools()
        print(f"[OK] Total Gmail toolkit tools found: {len(all_tools)}")

        for tool in all_tools:
            tool_name = getattr(tool, "name", "")
            if tool_name in selected_tool_names:
                filtered_tools.append(tool)
                print(f"  [SELECTED] {tool_name}")
            else:
                print(f"  [EXCLUDED] {tool_name}")

        print(f"[OK] Successfully loaded {len(filtered_tools)} selected Gmail tools.")

    except Exception as error:
        print(f"[ERROR] Failed to initialize Gmail toolkit: {str(error)}")
        print("  Ensure credentials.json is placed correctly and required packages are installed.")

    return filtered_tools
