"""
Query Builder - SQL Generation for Generic CDC Framework
Generates parameterized SQL for all CDC operations
"""

import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, PROJECT_ROOT)

from typing import List, Optional, Dict, Any
from Langchain.Tools.ToolsFinanceAssist.config.table_adapters import TableAdapter


class QueryBuilder:
    """Builds parameterized SQL queries for CDC operations"""
    
    def __init__(self, adapter: TableAdapter):
        self.adapter = adapter
        self.table = adapter.table
        self.pk = adapter.pk
        self.name_col = adapter.name_col
        self.value_cols = adapter.value_cols
        self.date_col = adapter.date_col
        self.extra_cols = adapter.extra_cols
        self.cdc_cols = adapter.cdc_cols
        
        # All columns that are carried forward on update
        self.all_data_cols = [self.name_col] + self.value_cols + self.extra_cols
        if self.date_col:
            self.all_data_cols.append(self.date_col)
    
    # -------------------------------------------------------------------------
    # CORE CDC QUERIES
    # -------------------------------------------------------------------------
    
    def get_latest_active_record(self, name: str) -> tuple[str, tuple]:
        """Find the latest active record for a name"""
        sql = f"""
            SELECT * FROM {self.table}
            WHERE {self.name_col} = ? AND is_latest = 1 AND status = 'ACTIVE'
        """
        return sql, (name,)
    
    def get_latest_record(self, name: str) -> tuple[str, tuple]:
        """Find the latest record for a name (any status)"""
        sql = f"""
            SELECT * FROM {self.table}
            WHERE {self.name_col} = ? AND is_latest = 1
        """
        return sql, (name,)
    
    def close_record(self, pk_value: int) -> tuple[str, tuple]:
        """Mark a record as CLOSED (keep is_latest=1 as final state)"""
        sql = f"""
            UPDATE {self.table}
            SET status = 'CLOSED'
            WHERE {self.pk} = ?
        """
        return sql, (pk_value,)
    
    def insert_new_record(self, data: Dict[str, Any]) -> tuple[str, tuple]:
        """Insert a new record with is_latest=1"""
        cols = list(data.keys())
        placeholders = ", ".join(["?"] * len(cols))
        sql = f"""
            INSERT INTO {self.table} ({", ".join(cols)})
            VALUES ({placeholders})
        """
        return sql, tuple(data.values())
    
    def supersede_old_record(self, old_pk: int, new_pk: int) -> tuple[str, tuple]:
        """Mark old record as superseded by new record"""
        sql = f"""
            UPDATE {self.table}
            SET is_latest = 0, superseded_by = ?
            WHERE {self.pk} = ?
        """
        return sql, (new_pk, old_pk)
    
    # -------------------------------------------------------------------------
    # READ QUERIES
    # -------------------------------------------------------------------------
    
    def get_current_records(self) -> tuple[str, tuple]:
        """Get all current active records (latest version)"""
        sql = f"""
            SELECT * FROM {self.table}
            WHERE is_latest = 1 AND status = 'ACTIVE'
            ORDER BY {self.pk}
        """
        return sql, ()
    
    def get_closed_records(self) -> tuple[str, tuple]:
        """Get all closed records (final state)"""
        sql = f"""
            SELECT * FROM {self.table}
            WHERE status = 'CLOSED' AND is_latest = 1
            ORDER BY {self.pk}
        """
        return sql, ()
    
    def get_record_history(self, name: str) -> tuple[str, tuple]:
        """Get full history for a specific name"""
        sql = f"""
            SELECT * FROM {self.table}
            WHERE {self.name_col} = ?
            ORDER BY {self.pk}
        """
        return sql, (name,)
    
    def get_all_records(self) -> tuple[str, tuple]:
        """Get all records (admin/debug)"""
        sql = f"""
            SELECT * FROM {self.table}
            ORDER BY {self.pk}
        """
        return sql, ()
    
    # -------------------------------------------------------------------------
    # HELPER: BUILD RECORD DATA FOR INSERT
    # -------------------------------------------------------------------------
    
    def build_new_record_data(
        self,
        name: str,
        value_updates: Dict[str, Any],
        old_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build data dict for new record by merging old record with updates
        """
        new_data = {}
        
        # Name column
        new_data[self.name_col] = name
        
        # Value columns - use updates or fall back to old values
        for col in self.value_cols:
            new_data[col] = value_updates.get(col, old_record.get(col))
        
        # Extra columns - carry forward from old record
        for col in self.extra_cols:
            new_data[col] = old_record.get(col)
        
        # Date column - carry forward from old record
        if self.date_col:
            new_data[self.date_col] = old_record.get(self.date_col)
        
        # CDC columns
        new_data["status"] = "ACTIVE"
        new_data["superseded_by"] = None
        new_data["is_latest"] = 1
        
        return new_data
    
    def build_initial_record_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build data dict for a brand new record (no old record)"""
        new_data = {}
        
        # Required: name
        if self.name_col not in data:
            raise ValueError(f"Missing required column: {self.name_col}")
        new_data[self.name_col] = data[self.name_col]
        
        # Value columns
        for col in self.value_cols:
            if col not in data:
                raise ValueError(f"Missing required column: {col}")
            new_data[col] = data[col]
        
        # Extra columns (optional)
        for col in self.extra_cols:
            new_data[col] = data.get(col)
        
        # Date column
        if self.date_col:
            new_data[self.date_col] = data.get(self.date_col)
        
        # CDC columns
        new_data["status"] = "ACTIVE"
        new_data["superseded_by"] = None
        new_data["is_latest"] = 1
        
        return new_data


# ============================================================================
# FACTORY
# ============================================================================

def get_query_builder(table_name: str) -> QueryBuilder:
    """Get QueryBuilder for a table"""
    from config.table_adapters import get_adapter
    adapter = get_adapter(table_name)
    return QueryBuilder(adapter)


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    from config.table_adapters import TABLE_ADAPTERS
    
    print("QUERY BUILDER DEMO")
    print("=" * 60)
    
    for table_name, adapter in TABLE_ADAPTERS.items():
        qb = QueryBuilder(adapter)
        print(f"\n--- {table_name} ---")
        
        # Show key queries
        sql, params = qb.get_current_records()
        print(f"Current: {sql.strip()}")
        
        sql, params = qb.get_latest_active_record("test")
        print(f"Latest Active: {sql.strip()} | params: {params}")
        
        sql, params = qb.close_record(1)
        print(f"Close: {sql.strip()} | params: {params}")
        
        sql, params = qb.insert_new_record({"name": "test", "amt": 100})
        print(f"Insert: {sql.strip()} | params: {params}")