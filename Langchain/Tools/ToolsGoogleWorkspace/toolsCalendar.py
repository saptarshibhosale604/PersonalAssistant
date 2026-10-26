"""
Tools Calendar Module

Integrates LangChain's prebuilt CalendarToolkit from langchain_google_community.
Uses its own OAuth token file so its scope does not collide with Gmail.

--- Available Toolkit Tools (7 total):
    1. create_calendar_event
    2. search_events
    3. update_calendar_event
    4. get_calendars_info
    5. move_calendar_event
    6. delete_calendar_event
    7. get_current_datetime

--- Selected Tools (4 total):
    - create_calendar_event
    - search_events
    - get_calendars_info
    - get_current_datetime
"""

from typing import List, Any
from langchain_google_community import CalendarToolkit
from langchain_google_community._utils import get_google_credentials
from langchain_google_community.calendar.utils import build_calendar_service
from Log.log_utils import PrintFunctionName

CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_TOKEN_FILE = "./token_calendar.json"

@PrintFunctionName
def ToolsList() -> List[Any]:
    """
    Initialize and return filtered tools from CalendarToolkit.
    Selected tools only:
    - create_calendar_event
    - search_events
    - get_calendars_info
    - get_current_datetime
    """
    selected_tool_names = {
        "create_calendar_event",
        "search_events",
        "get_calendars_info",
        "get_current_datetime"
    }

    filtered_tools = []
    try:
        credentials = get_google_credentials(scopes=CALENDAR_SCOPES, token_file=CALENDAR_TOKEN_FILE)
        calendar_toolkit = CalendarToolkit(api_resource=build_calendar_service(credentials=credentials))
        all_tools = calendar_toolkit.get_tools()
        print(f"[OK] Total Calendar toolkit tools found: {len(all_tools)}")

        for tool in all_tools:
            tool_name = getattr(tool, "name", "")
            if tool_name in selected_tool_names:
                filtered_tools.append(tool)
                print(f"  [SELECTED] {tool_name}")
            else:
                print(f"  [EXCLUDED] {tool_name}")

        print(f"[OK] Successfully loaded {len(filtered_tools)} selected Calendar tools.")

    except Exception as error:
        print(f"[ERROR] Failed to initialize Calendar toolkit: {str(error)}")
        print("  Ensure credentials.json is placed correctly and required packages are installed.")

    return filtered_tools
