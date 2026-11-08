"""
Auto-Generated CDC Tools - LangChain Tool Wrappers
Dynamically creates 7 tools per table from TableAdapter config
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, PROJECT_ROOT)

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json

from Langchain.Tools.ToolsFinanceAssist.config.table_adapters import TABLE_ADAPTERS, get_adapter
from Langchain.Tools.ToolsFinanceAssist.Services.cdc_service import get_cdc_service, CDCResult


# ============================================================================
# PYDANTIC SCHEMAS (Dynamic - created per table)
# ============================================================================

def create_close_schema(table_name: str, adapter) -> type:
    """Create schema for close_record tool"""
    annotations = {"name": str}
    fields = {"name": Field(description=f"Name of the record to close in {table_name}")}
    
    CloseSchema = type(
        f"Close{adapter.table.title().replace('_', '')}Schema", 
        (BaseModel,), 
        {"__annotations__": annotations, **fields}
    )
    return CloseSchema


def create_update_schema(table_name: str, adapter) -> type:
    """Create schema for update_record tool"""
    # Build fields dynamically from value_cols
    annotations = {"name": str}
    fields = {"name": Field(description=f"Name of the record to update in {table_name}")}
    for col in adapter.value_cols:
        annotations[col] = Optional[float]
        fields[col] = Field(default=None, description=f"New {col} (optional)")
    
    UpdateSchema = type(
        f"Update{adapter.table.title().replace('_', '')}Schema", 
        (BaseModel,), 
        {"__annotations__": annotations, **fields}
    )
    return UpdateSchema


def create_add_schema(table_name: str, adapter) -> type:
    """Create schema for add_record tool"""
    annotations = {}
    fields = {}
    # Required: name_col
    annotations[adapter.name_col] = str
    fields[adapter.name_col] = Field(description=f"Name for the new {table_name} record")
    # Required: value_cols
    for col in adapter.value_cols:
        annotations[col] = float
        fields[col] = Field(description=f"{col} for the new record")
    # Optional: extra_cols
    for col in adapter.extra_cols:
        annotations[col] = Optional[str]
        fields[col] = Field(default=None, description=f"{col} (optional)")
    # Optional: date_col
    if adapter.date_col:
        annotations[adapter.date_col] = Optional[str]
        fields[adapter.date_col] = Field(default=None, description=f"{adapter.date_col} (optional, defaults to today)")
    
    AddSchema = type(
        f"Add{adapter.table.title().replace('_', '')}Schema", 
        (BaseModel,), 
        {"__annotations__": annotations, **fields}
    )
    return AddSchema


def create_history_schema(table_name: str, adapter) -> type:
    """Create schema for get_record_history tool"""
    annotations = {"name": str}
    fields = {"name": Field(description=f"Name of the record to get history for in {table_name}")}
    
    HistorySchema = type(
        f"History{adapter.table.title().replace('_', '')}Schema", 
        (BaseModel,), 
        {"__annotations__": annotations, **fields}
    )
    return HistorySchema


def create_latest_schema(table_name: str, adapter) -> type:
    """Create schema for get_latest_record tool"""
    annotations = {"name": str}
    fields = {"name": Field(description=f"Name of the record to get latest value for in {table_name}")}
    
    LatestSchema = type(
        f"Latest{adapter.table.title().replace('_', '')}Schema", 
        (BaseModel,), 
        {"__annotations__": annotations, **fields}
    )
    return LatestSchema


# ============================================================================
# TOOL FACTORIES
# ============================================================================

def make_close_tool(adapter) -> tool:
    """Create tool_close_record for a table"""
    schema = create_close_schema(adapter.table, adapter)
    
    @tool(args_schema=schema)
    def close_record(name: str) -> str:
        """
        Close a record (mark as CLOSED, preserve history).
        Use when user says they have closed/exited a position.
        Does NOT delete the row - creates immutable audit trail.
        """
        service = get_cdc_service(adapter.table)
        result = service.close_record(name)
        if result.success:
            return f"[OK] {result.message}"
        else:
            return f"[ERROR] {result.error}"
    
    close_record.name = f"close_record_{adapter.table}"
    return close_record


def make_update_tool(adapter) -> tool:
    """Create tool_update_record for a table"""
    schema = create_update_schema(adapter.table, adapter)
    
    @tool(args_schema=schema)
    def update_record(name: str, **value_updates) -> str:
        """
        Update record by creating a NEW row (append-only).
        Old row is marked as superseded. Preserves full history.
        Use when user says 'change value of X to Y'.
        Only value columns can be updated: {adapter.value_cols}
        """
        # Filter out None values
        filtered_updates = {k: v for k, v in value_updates.items() if v is not None}
        
        if not filtered_updates:
            return f"[ERROR] No valid update values provided. Allowed: {adapter.value_cols}"
        
        service = get_cdc_service(adapter.table)
        result = service.update_record(name, **filtered_updates)
        if result.success:
            data = result.data
            return (
                f"[OK] {result.message}\n"
                f"   Old Record: PK {data['old_pk']} (now superseded)\n"
                f"   New Record: PK {data['new_pk']} (current)\n"
                f"   Updated: {data['updated_values']}"
            )
        else:
            return f"[ERROR] {result.error}"
    
    update_record.name = f"update_record_{adapter.table}"
    return update_record


def make_add_tool(adapter) -> tool:
    """Create tool_add_record for a table"""
    schema = create_add_schema(adapter.table, adapter)
    
    @tool(args_schema=schema)
    def add_record(**data) -> str:
        """
        Add a brand new record (first entry).
        """
        service = get_cdc_service(adapter.table)
        result = service.add_record(**data)
        if result.success:
            return f"[OK] {result.message}"
        else:
            return f"[ERROR] {result.error}"
    
    add_record.name = f"add_record_{adapter.table}"
    return add_record


def make_get_current_tool(adapter) -> tool:
    """Create tool_get_current_records for a table"""
    
    @tool
    def get_current_records() -> str:
        """
        Get current active records (latest values only).
        Shows one row per name with current status.
        """
        service = get_cdc_service(adapter.table)
        records = service.get_current_records()
        return service.format_current_display(records)
    
    get_current_records.name = f"get_current_records_{adapter.table}"
    return get_current_records


def make_get_history_tool(adapter) -> tool:
    """Create tool_get_record_history for a table"""
    schema = create_history_schema(adapter.table, adapter)
    
    @tool(args_schema=schema)
    def get_record_history(name: str) -> str:
        """
        Get full history for a specific record (all versions).
        Shows the complete chain of updates and closures.
        """
        service = get_cdc_service(adapter.table)
        records = service.get_record_history(name)
        return service.format_history_display(records)
    
    get_record_history.name = f"get_record_history_{adapter.table}"
    return get_record_history


def make_get_closed_tool(adapter) -> tool:
    """Create tool_get_closed_records for a table"""
    
    @tool
    def get_closed_records() -> str:
        """
        Get all closed records.
        Shows the final state of each closed record.
        """
        service = get_cdc_service(adapter.table)
        records = service.get_closed_records()
        if not records:
            return f"[EMPTY] No closed records in {adapter.table}."
        
        output = f"[CLOSED] Closed {adapter.table.replace('_', ' ').title()} Records:\n"
        output += "=" * 80 + "\n"
        
        for r in records:
            output += f"\n[CLOSED] PK: {r.pk} | {r.name}\n"
            for col in adapter.value_cols:
                if col in r.data:
                    output += f"   {col}: {r.data[col]}\n"
            for col in adapter.extra_cols:
                if col in r.data and r.data[col] is not None:
                    output += f"   {col}: {r.data[col]}\n"
            if adapter.date_col and adapter.date_col in r.data:
                output += f"   Date: {r.data[adapter.date_col]}\n"
        
        return output
    
    get_closed_records.name = f"get_closed_records_{adapter.table}"
    return get_closed_records


def make_get_latest_tool(adapter) -> tool:
    """Create tool_get_latest_record for a table"""
    schema = create_latest_schema(adapter.table, adapter)
    
    @tool(args_schema=schema)
    def get_latest_record(name: str) -> str:
        """
        Get the latest/current record for a specific name.
        """
        service = get_cdc_service(adapter.table)
        record = service.get_latest_record(name)
        if not record:
            return f"[ERROR] No record found for: {name} in {adapter.table}"
        
        status_marker = "[ACTIVE]" if record.status == "ACTIVE" else "[CLOSED]"
        
        output = f"{status_marker} Latest Record for '{name}' ({adapter.table}):\n"
        output += "=" * 60 + "\n"
        output += f"   PK: {record.pk} | Status: {record.status}\n"
        
        for col in adapter.value_cols:
            if col in record.data:
                output += f"   {col}: {record.data[col]}\n"
        
        for col in adapter.extra_cols:
            if col in record.data and record.data[col] is not None:
                output += f"   {col}: {record.data[col]}\n"
        
        if adapter.date_col and adapter.date_col in record.data:
            output += f"   Date: {record.data[adapter.date_col]}\n"
        
        if record.superseded_by:
            output += f"\n   [NOTE] This record is superseded by PK {record.superseded_by}"
        
        return output
    
    get_latest_record.name = f"get_latest_record_{adapter.table}"
    return get_latest_record


# ============================================================================
# GENERATE ALL TOOLS
# ============================================================================

def generate_all_cdc_tools() -> List[tool]:
    """Generate all 35 tools (7 per table × 5 tables)"""
    all_tools = []
    
    for table_name, adapter in TABLE_ADAPTERS.items():
        all_tools.extend([
            make_close_tool(adapter),
            make_update_tool(adapter),
            make_add_tool(adapter),
            make_get_current_tool(adapter),
            make_get_history_tool(adapter),
            make_get_closed_tool(adapter),
            make_get_latest_tool(adapter),
        ])
    
    return all_tools


# ============================================================================
# EXPORTS
# ============================================================================

# Generate all tools
ALL_CDC_TOOLS = generate_all_cdc_tools()

# Also export per-table tool groups for selective registration
def get_tools_for_table(table_name: str) -> List[tool]:
    """Get the 7 tools for a specific table"""
    adapter = get_adapter(table_name)
    return [
        make_close_tool(adapter),
        make_update_tool(adapter),
        make_add_tool(adapter),
        make_get_current_tool(adapter),
        make_get_history_tool(adapter),
        make_get_closed_tool(adapter),
        make_get_latest_tool(adapter),
    ]


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("CDC TOOLS GENERATED")
    print("=" * 60)
    print(f"Total tools: {len(ALL_CDC_TOOLS)}")
    print(f"Tables: {list(TABLE_ADAPTERS.keys())}")
    print(f"Tools per table: 7")
    
    print("\nTool names:")
    for t in ALL_CDC_TOOLS:
        print(f"  - {t.name}")