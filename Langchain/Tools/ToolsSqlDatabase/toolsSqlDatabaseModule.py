"""
LangChain SQL Database Tools Module
Provides ToolsList() to retrieve the SQL database tools suite.
"""

from typing import List, Any
from langchain_core.tools import Tool
from .toolsSqlDatabase import get_sql_tools

def ToolsList() -> List[Tool]:
    """
    Returns the list of SQL database tools for the agent manager.
    """
    return get_sql_tools()
