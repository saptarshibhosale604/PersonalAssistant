"""
LangChain Tools for Personal Finance Tracking - CDC Framework
Provides append-only ledger tools for all finance tables in finance.db
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, PROJECT_ROOT)

from Langchain.Tools.ToolsFinanceAssist.tools.cdc_tools import ALL_CDC_TOOLS


# ============================================================================
# EXPORT ALL CDC TOOLS
# ============================================================================

# All 35 tools (7 per table × 5 tables)
tools = ALL_CDC_TOOLS

# Also provide categorized access
def get_tools_by_table(table_name: str):
    """Get the 7 tools for a specific table"""
    from Langchain.Tools.ToolsFinanceAssist.tools.cdc_tools import get_tools_for_table
    return get_tools_for_table(table_name)


def get_all_tools():
    """Get all 35 CDC tools"""
    return ALL_CDC_TOOLS


def ToolsList():
    """Return all tools for agent registration"""
    return tools


# ============================================================================
# TABLE MAPPING
# ============================================================================

TABLES = [
    "mutual_fund",
    "fixed_deposit", 
    "physical",
    "saving",
    "stock"
]

TOOLS_PER_TABLE = 7
TOTAL_TOOLS = len(TABLES) * TOOLS_PER_TABLE  # 35


# ============================================================================
# DEMO / VERIFICATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TOOLS FINANCE ASSIST - CDC FRAMEWORK")
    print("=" * 60)
    print(f"Tables: {TABLES}")
    print(f"Tools per table: {TOOLS_PER_TABLE}")
    print(f"Total tools: {TOTAL_TOOLS}")
    print()
    
    print("All tools:")
    for i, tool in enumerate(tools, 1):
        print(f"  {i:2d}. {tool.name}")
    
    print()
    print("Tools by table:")
    for table in TABLES:
        table_tools = get_tools_by_table(table)
        print(f"  {table}: {len(table_tools)} tools")
        for t in table_tools:
            print(f"    - {t.name}")