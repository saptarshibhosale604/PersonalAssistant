"""
LangChain SQL Database Tools Module
Provides ToolsList() and SQL database tool suite initialization, including custom tools
to list available database files and switch active databases dynamically.
"""

import os
from pathlib import Path
from typing import List, Any
from langchain_core.tools import Tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI

# Module-level variable to track the currently active database filename
_ACTIVE_DB_FILENAME = "mydatabase.db"

def get_sql_tools(llm: Any = None) -> List[Tool]:
    """
    Initializes the SQLDatabase instance pointing to CloudPII/ToolsSqlDatabase/<_ACTIVE_DB_FILENAME>
    and returns the complete set of default tools from SQLDatabaseToolkit plus custom database management tools.
    """
    global _ACTIVE_DB_FILENAME
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../CloudPII/ToolsSqlDatabase"))
    os.makedirs(base_dir, exist_ok=True)
    
    db_path = os.path.join(base_dir, _ACTIVE_DB_FILENAME)
    db_uri = f"sqlite:///{db_path.replace(os.sep, '/')}"

    db = SQLDatabase.from_uri(db_uri, engine_args={"connect_args": {"timeout": 15}})

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
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    def sql_db_list_databases(tool_input: str = "") -> str:
        """List all available .db files in CloudPII/ToolsSqlDatabase/."""
        try:
            if not os.path.exists(base_dir):
                return "Database directory does not exist."
            db_files = [f for f in os.listdir(base_dir) if f.endswith(".db")]
            if not db_files:
                return "No .db files found in CloudPII/ToolsSqlDatabase/."
            active_notice = f" (Active: {_ACTIVE_DB_FILENAME})"
            return f"Available databases{active_notice}:\n" + "\n".join([f"- {f}" for f in db_files])
        except Exception as e:
            return f"Error listing databases: {str(e)}"

    def sql_db_use_database(db_name: str) -> str:
        """Select one of the .db files from CloudPII/ToolsSqlDatabase/ to use as the active database."""
        global _ACTIVE_DB_FILENAME
        try:
            safe_name = Path(db_name.strip()).name
            if not safe_name.endswith(".db"):
                safe_name += ".db"
            
            target_path = os.path.join(base_dir, safe_name)
            if not os.path.exists(target_path):
                return f"Database file '{safe_name}' does not exist in CloudPII/ToolsSqlDatabase/."
            
            _ACTIVE_DB_FILENAME = safe_name
            return f"Successfully switched active database to '{_ACTIVE_DB_FILENAME}'. All subsequent SQL queries and table inspections will target this database."
        except Exception as e:
            return f"Error switching database: {str(e)}"

    list_databases_tool = Tool(
        name="sql_db_list_databases",
        func=sql_db_list_databases,
        description="List all available .db files in CloudPII/ToolsSqlDatabase/"
    )

    use_database_tool = Tool(
        name="sql_db_use_database",
        func=sql_db_use_database,
        description="Select one of the .db files from CloudPII/ToolsSqlDatabase/ to use as the active database. Input should be the database filename (e.g. 'finance.db')."
    )

    # Wrap toolkit tools so that every time ANY toolkit tool (like sql_db_query, sql_db_list_tables, etc.)
    # is invoked, it dynamically connects to the currently active _ACTIVE_DB_FILENAME database.
    original_tools = toolkit.get_tools()
    wrapped_tools = []

    for t in original_tools:
        # Create a closure/wrapper that builds a fresh SQLDatabase on each tool execution
        def make_wrapper(original_tool):
            def wrapper(tool_input: str) -> str:
                curr_path = os.path.join(base_dir, _ACTIVE_DB_FILENAME)
                curr_uri = f"sqlite:///{curr_path.replace(os.sep, '/')}"
                fresh_db = SQLDatabase.from_uri(curr_uri, engine_args={"connect_args": {"timeout": 15}})
                
                # Temporarily bind fresh_db to a temporary toolkit for this tool execution
                temp_toolkit = SQLDatabaseToolkit(db=fresh_db, llm=llm)
                temp_tools = {ot.name: ot for ot in temp_toolkit.get_tools()}
                
                if original_tool.name in temp_tools:
                    return temp_tools[original_tool.name].run(tool_input)
                return original_tool.run(tool_input)
            return wrapper

        wrapped_tool = Tool(
            name=t.name,
            func=make_wrapper(t),
            description=t.description
        )
        wrapped_tools.append(wrapped_tool)

    return wrapped_tools + [list_databases_tool, use_database_tool]

def ToolsList() -> List[Tool]:
    """
    Returns the complete list of default SQL database tools and custom database management tools for the agent manager.
    """
    return get_sql_tools()
