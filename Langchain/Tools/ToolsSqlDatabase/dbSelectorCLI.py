"""
Database Selector & SQL Query Interface Module
Scans CloudPII/ToolsSqlDatabase/ for .db files, allows user selection,
and provides an interactive SQL execution console or LangChain toolset.
"""

import os
import sqlite3
from typing import List, Optional, Any
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_core.tools import Tool

DEFAULT_DB_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../CloudPII/ToolsSqlDatabase")
)

def list_available_databases(db_dir: str = DEFAULT_DB_DIR) -> List[str]:
    """Scans the target directory and returns a list of .db filenames."""
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        return []
    
    files = os.listdir(db_dir)
    db_files = [f for f in files if f.endswith(('.db', '.sqlite', '.sqlite3'))]
    return sorted(db_files)

def select_database_interactive(db_dir: str = DEFAULT_DB_DIR) -> Optional[str]:
    """
    Lists all available databases and prompts the user to select one.
    Returns the absolute path to the selected database file.
    """
    db_files = list_available_databases(db_dir)
    
    if not db_files:
        print(f"[TACTICAL ALERT] No .db files found in directory: {db_dir}")
        print("[TACTICAL ALERT] Creating default 'mydatabase.db'...")
        default_path = os.path.join(db_dir, "mydatabase.db")
        conn = sqlite3.connect(default_path)
        conn.close()
        db_files = ["mydatabase.db"]

    print("\n========================================")
    print("       CLOUD PII SQL DATABASE SELECTOR   ")
    print("========================================")
    for idx, db_name in enumerate(db_files, start=1):
        print(f"  [{idx}] {db_name}")
    print("========================================")

    while True:
        try:
            choice = input(f"Select database [1-{len(db_files)}] (default [1], or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return None
            
            # If user presses enter without typing anything, default to 1 (index 0)
            if choice == "":
                choice = "1"
            
            selected_idx = int(choice) - 1
            if 0 <= selected_idx < len(db_files):
                chosen_db = db_files[selected_idx]
                full_path = os.path.join(db_dir, chosen_db)
                print(f"[ACK] Selected database: {chosen_db} ({full_path})")
                return full_path
            else:
                print("[ERROR] Invalid selection index. Try again.")
        except ValueError:
            print("[ERROR] Please enter a valid integer corresponding to the database index.")

def run_sql_query_shell(db_path: str):
    """
    Opens an interactive SQL query session against the specified SQLite database.
    Supports multi-line SQL statements ending with a semicolon (;).
    """
    if not db_path or not os.path.exists(db_path):
        print("[ERROR] Invalid database path provided.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n[READY] Connected to SQLite DB: {os.path.basename(db_path)}")
    print("Type any valid SQL query (end statements with ';') or type 'EXIT' to quit.")
    
    buffer = []
    while True:
        try:
            prompt = "SQL> " if not buffer else "   -> "
            line = input(prompt)
            
            # If buffer is empty, check for EXIT/QUIT
            if not buffer:
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                if stripped_line.upper() in ('EXIT', 'QUIT'):
                    break
            
            buffer.append(line)
            full_query = "\n".join(buffer)
            
            # Check if query ends with semicolon
            if full_query.strip().endswith(";"):
                try:
                    cleaned_query = full_query.strip().upper()
                    is_select = cleaned_query.startswith("SELECT") or cleaned_query.startswith("PRAGMA") or cleaned_query.startswith("EXPLAIN")
                    
                    if is_select:
                        cursor.execute(full_query)
                        rows = cursor.fetchall()
                        col_names = [description[0] for description in cursor.description] if cursor.description else []
                        
                        print("\n--- QUERY RESULT ---")
                        if col_names:
                            print(" | ".join(col_names))
                            print("-" * (len(" | ".join(col_names))))
                        for row in rows:
                            print(" | ".join(str(val) for val in row))
                        print(f"({len(rows)} rows returned)\n")
                    else:
                        cursor.executescript(full_query)
                        conn.commit()
                        print(f"[SUCCESS] Query executed and committed successfully.")
                except Exception as e:
                    print(f"[SQL ERROR]: {e}")
                finally:
                    buffer = [] # Reset buffer
                    
        except (KeyboardInterrupt, EOFError):
            print("\n[ACK] Session terminated.")
            break
        except Exception as e:
            print(f"[ERROR]: {e}")
            buffer = []

    conn.close()
    print("[ACK] Database connection closed.")

def get_langchain_tools_for_selected_db(db_path: str, llm: Any = None) -> List[Tool]:
    """
    Returns LangChain SQLDatabaseToolkit tools configured for the specific selected database.
    """
    db_uri = f"sqlite:///{db_path.replace(os.sep, '/')}"
    db = SQLDatabase.from_uri(db_uri, engine_args={"connect_args": {"timeout": 15}})
    
    if llm is None:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", max_tokens=2048)
        
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    return toolkit.get_tools()

if __name__ == "__main__":
    db_path = select_database_interactive()
    if db_path:
        run_sql_query_shell(db_path)
