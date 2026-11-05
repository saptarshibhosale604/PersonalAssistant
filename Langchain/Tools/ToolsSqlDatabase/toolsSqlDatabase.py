"""
LangChain SQL Database Tools Module
Provides ToolsList() to retrieve the complete default suite of SQL database tools
using SQLDatabaseToolkit and ChatGoogleGenerativeAI (gemini-3.5-flash-lite).
"""

import os
from typing import List, Any
from langchain_core.tools import Tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI

def get_sql_tools(llm: Any = None) -> List[Tool]:
    """
    Initializes the SQLDatabase instance pointing to CloudPII/ToolsSqlDatabase/mydatabase.db
    and returns the complete set of default tools from SQLDatabaseToolkit
    (QuerySQLDatabaseTool, InfoSQLDatabaseTool, ListSQLDatabaseTool, QuerySQLCheckerTool).
    
    Args:
        llm: Language model instance required by QuerySQLCheckerTool.
             If None, defaults to ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite").
    """
    # Resolve absolute path to CloudPII/ToolsSqlDatabase/mydatabase.db
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../CloudPII/ToolsSqlDatabase"))
    os.makedirs(base_dir, exist_ok=True)
    
    db_path = os.path.join(base_dir, "mydatabase.db")
    db_uri = f"sqlite:///{db_path.replace(os.sep, '/')}"

    # Initialize SQLDatabase connection with timeout for SQLite concurrency
    db = SQLDatabase.from_uri(db_uri, engine_args={"connect_args": {"timeout": 15}})

    # If llm is not provided, initialize ChatGoogleGenerativeAI with gemini-3.5-flash-lite
    if llm is None:
        try:
            DEFAULT_MAX_TOKENS = 2048
            DEFAULT_MAX_RETRIES = 2
            llm = ChatGoogleGenerativeAI(
                model="gemini-3.5-flash-lite",
                max_tokens=DEFAULT_MAX_TOKENS,
                max_retries=DEFAULT_MAX_RETRIES,
            )
        except Exception:
            # Fallback if google genai is not available
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    # Use SQLDatabaseToolkit to get all 4 default tools with original names
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    return tools

def ToolsList() -> List[Tool]:
    """
    Returns the complete list of default SQL database tools for the agent manager.
    """
    return get_sql_tools()
