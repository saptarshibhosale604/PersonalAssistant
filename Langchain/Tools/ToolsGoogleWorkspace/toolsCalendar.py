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

from typing import List, Any, Optional, Dict, Union
from langchain_google_community import CalendarToolkit
from langchain_google_community._utils import get_google_credentials
from langchain_google_community.calendar.utils import build_calendar_service
from langchain_google_community.calendar.create_event import CalendarCreateEvent, CreateEventSchema
from langchain_google_community.calendar.current_datetime import GetCurrentDatetime, CurrentDatetimeSchema
from pydantic import Field
from Log.log_utils import PrintFunctionName

CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_TOKEN_FILE = "./token_calendar.json"

class PatchedCreateEventSchema(CreateEventSchema):
    timezone: str = "Asia/Kolkata"
    calendar_id: str = "saptarshibhosale604@gmail.com"

class PatchedCurrentDatetimeSchema(CurrentDatetimeSchema):
    calendar_id: str = Field(
        default="saptarshibhosale604@gmail.com", description="The calendar ID. Defaults to 'saptarshibhosale604@gmail.com'."
    )

class PatchedGetCurrentDatetime(GetCurrentDatetime):
    args_schema: type[CurrentDatetimeSchema] = PatchedCurrentDatetimeSchema

    def _run(
        self,
        calendar_id: Optional[str] = None,
        run_manager: Any = None,
    ) -> str:
        cal_id = calendar_id if calendar_id else "saptarshibhosale604@gmail.com"
        return super()._run(calendar_id=cal_id, run_manager=run_manager)

class PatchedCalendarCreateEvent(CalendarCreateEvent):
    args_schema: type[CreateEventSchema] = PatchedCreateEventSchema

    def _run(
        self,
        summary: str,
        start_datetime: str,
        end_datetime: str,
        timezone: Optional[str] = None,
        calendar_id: Optional[str] = None,
        recurrence: Optional[Dict[str, Any]] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        reminders: Union[None, bool, List[Dict[str, Any]]] = None,
        conference_data: Optional[bool] = None,
        color_id: Optional[str] = None,
        transparency: Optional[str] = None,
        run_manager: Any = None,
    ) -> str:
        tz = timezone if timezone else "Asia/Kolkata"
        cal_id = calendar_id if calendar_id else "saptarshibhosale604@gmail.com"
        return super()._run(
            summary=summary,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            timezone=tz,
            calendar_id=cal_id,
            recurrence=recurrence,
            location=location,
            description=description,
            attendees=attendees,
            reminders=reminders,
            conference_data=conference_data,
            color_id=color_id,
            transparency=transparency,
            run_manager=run_manager,
        )

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
        api_resource = build_calendar_service(credentials=credentials)
        calendar_toolkit = CalendarToolkit(api_resource=api_resource)
        all_tools = calendar_toolkit.get_tools()
        print(f"[OK] Total Calendar toolkit tools found: {len(all_tools)}")

        for tool in all_tools:
            tool_name = getattr(tool, "name", "")
            if tool_name in selected_tool_names:
                if tool_name == "create_calendar_event":
                    tool = PatchedCalendarCreateEvent(api_resource=api_resource)
                elif tool_name == "get_current_datetime":
                    tool = PatchedGetCurrentDatetime(api_resource=api_resource)

                filtered_tools.append(tool)
                print(f"  [SELECTED & CONFIGURED] {tool_name}")
            else:
                print(f"  [EXCLUDED] {tool_name}")

        print(f"[OK] Successfully loaded {len(filtered_tools)} selected Calendar tools.")

    except Exception as error:
        print(f"[ERROR] Failed to initialize Calendar toolkit: {str(error)}")
        print("  Ensure credentials.json is placed correctly and required packages are installed.")

    return filtered_tools
