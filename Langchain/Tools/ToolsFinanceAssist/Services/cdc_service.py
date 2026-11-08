"""
Generic CDC Service - Append-Only Ledger Implementation
Single implementation for all tables using TableAdapter config
"""

import sqlite3
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, PROJECT_ROOT)

from Langchain.Tools.ToolsFinanceAssist.config.table_adapters import TableAdapter, get_adapter
from Langchain.Tools.ToolsFinanceAssist.Services.query_builder import QueryBuilder


# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent.parent / "CloudPII" / "ToolsSqlDatabase" / "finance.db"


@dataclass
class CDCResult:
    """Standard result for CDC operations"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class Record:
    """Generic record container"""
    pk: int
    name: str
    data: Dict[str, Any]
    status: str
    superseded_by: Optional[int]
    is_latest: bool


class CDCService:
    """
    Generic CDC Service for any table configured in TableAdapter.
    
    Implements append-only event-sourcing pattern:
    - Never delete rows, only mark as CLOSED or superseded
    - New rows for value updates create immutable history chain
    - Current view via is_latest=1 AND status='ACTIVE'
    """
    
    def __init__(self, table_name: str):
        self.adapter = get_adapter(table_name)
        self.qb = QueryBuilder(self.adapter)
        self.table_name = table_name
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _row_to_record(self, row: sqlite3.Row) -> Record:
        """Convert sqlite3.Row to Record"""
        data = dict(row)
        pk = data.pop(self.adapter.pk)
        name = data.pop(self.adapter.name_col)
        status = data.pop("status")
        superseded_by = data.pop("superseded_by")
        is_latest = bool(data.pop("is_latest"))
        return Record(pk=pk, name=name, data=data, status=status, superseded_by=superseded_by, is_latest=is_latest)
    
    # =========================================================================
    # CORE CDC OPERATIONS
    # =========================================================================
    
    def close_record(self, name: str) -> CDCResult:
        """
        Mark a record as CLOSED (user closed the position).
        Does NOT delete the row - preserves history.
        Keeps is_latest=1 as the final state of this record.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Find the latest active record for this name
            sql, params = self.qb.get_latest_active_record(name)
            cursor.execute(sql, params)
            row = cursor.fetchone()
            
            if not row:
                return CDCResult(
                    success=False,
                    message="",
                    error=f"No active record found for '{name}' in {self.table_name}"
                )
            
            pk_value = row[self.adapter.pk]
            
            # Mark as CLOSED (keep is_latest=1 as final state)
            sql, params = self.qb.close_record(pk_value)
            cursor.execute(sql, params)
            
            conn.commit()
            return CDCResult(
                success=True,
                message=f"Record '{name}' (PK: {pk_value}) in {self.table_name} marked as CLOSED",
                data={"closed_pk": pk_value, "table": self.table_name}
            )
        except Exception as e:
            conn.rollback()
            return CDCResult(success=False, message="", error=str(e))
        finally:
            conn.close()
    
    def update_record(self, name: str, **value_updates) -> CDCResult:
        """
        Update record by creating a NEW row (append-only).
        Old row is marked as superseded (is_latest=0, superseded_by=new_pk).
        Only columns in value_cols can be updated; extra_cols are carried forward.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Find the latest active record
            sql, params = self.qb.get_latest_active_record(name)
            cursor.execute(sql, params)
            old_row = cursor.fetchone()
            
            if not old_row:
                return CDCResult(
                    success=False,
                    message="",
                    error=f"No active record found for '{name}' in {self.table_name}"
                )
            
            old_pk = old_row[self.adapter.pk]
            old_data = dict(old_row)
            
            # Validate that only allowed columns are being updated
            invalid_cols = set(value_updates.keys()) - set(self.adapter.value_cols)
            if invalid_cols:
                return CDCResult(
                    success=False,
                    message="",
                    error=f"Invalid columns for update: {invalid_cols}. Allowed: {self.adapter.value_cols}"
                )
            
            # Build new record data
            new_data = self.qb.build_new_record_data(name, value_updates, old_data)
            
            # Insert new record
            sql, params = self.qb.insert_new_record(new_data)
            cursor.execute(sql, params)
            new_pk = cursor.lastrowid
            
            # Update old record: mark as superseded
            sql, params = self.qb.supersede_old_record(old_pk, new_pk)
            cursor.execute(sql, params)
            
            conn.commit()
            return CDCResult(
                success=True,
                message=f"Record '{name}' in {self.table_name} updated. New PK: {new_pk}",
                data={
                    "old_pk": old_pk,
                    "new_pk": new_pk,
                    "table": self.table_name,
                    "updated_values": value_updates
                }
            )
        except Exception as e:
            conn.rollback()
            return CDCResult(success=False, message="", error=str(e))
        finally:
            conn.close()
    
    def add_record(self, **data) -> CDCResult:
        """Add a brand new record (first entry for this name)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Build initial record data
            new_data = self.qb.build_initial_record_data(data)
            
            # Insert new record
            sql, params = self.qb.insert_new_record(new_data)
            cursor.execute(sql, params)
            new_pk = cursor.lastrowid
            
            conn.commit()
            return CDCResult(
                success=True,
                message=f"New record '{data.get(self.adapter.name_col)}' added to {self.table_name} with PK: {new_pk}",
                data={"pk": new_pk, "table": self.table_name}
            )
        except Exception as e:
            conn.rollback()
            return CDCResult(success=False, message="", error=str(e))
        finally:
            conn.close()
    
    # =========================================================================
    # QUERY OPERATIONS
    # =========================================================================
    
    def get_current_records(self) -> List[Record]:
        """Get current active records (one per name, latest values)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            sql, params = self.qb.get_current_records()
            cursor.execute(sql, params)
            return [self._row_to_record(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_closed_records(self) -> List[Record]:
        """Get all closed records (final state of each closed name)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            sql, params = self.qb.get_closed_records()
            cursor.execute(sql, params)
            return [self._row_to_record(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_record_history(self, name: str) -> List[Record]:
        """Get full history for a specific name (all versions)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            sql, params = self.qb.get_record_history(name)
            cursor.execute(sql, params)
            return [self._row_to_record(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_all_records(self) -> List[Record]:
        """Get all records (for admin/debug)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            sql, params = self.qb.get_all_records()
            cursor.execute(sql, params)
            return [self._row_to_record(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_latest_record(self, name: str) -> Optional[Record]:
        """Get the latest record for a specific name (any status)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            sql, params = self.qb.get_latest_record(name)
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return self._row_to_record(row) if row else None
        finally:
            conn.close()
    
    # =========================================================================
    # DISPLAY FORMATTING
    # =========================================================================
    
    def format_current_display(self, records: List[Record]) -> str:
        """Format current records for display"""
        if not records:
            return f"[EMPTY] No active records in {self.table_name}."
        
        output = f"[CURRENT] {self.table_name.replace('_', ' ').title()} Records:\n"
        output += "=" * 80 + "\n"
        
        for r in records:
            status_marker = "[ACTIVE]" if r.status == "ACTIVE" else "[CLOSED]"
            output += f"\n{status_marker} PK: {r.pk} | {r.name}\n"
            
            # Show value columns
            for col in self.adapter.value_cols:
                if col in r.data:
                    output += f"   {col}: {r.data[col]}\n"
            
            # Show extra columns
            for col in self.adapter.extra_cols:
                if col in r.data and r.data[col] is not None:
                    output += f"   {col}: {r.data[col]}\n"
            
            if self.adapter.date_col and self.adapter.date_col in r.data:
                output += f"   Date: {r.data[self.adapter.date_col]}\n"
        
        return output
    
    def format_history_display(self, records: List[Record]) -> str:
        """Format record history for display"""
        if not records:
            return f"[EMPTY] No history found."
        
        name = records[0].name
        output = f"[HISTORY] {name} ({self.table_name}):\n"
        output += "=" * 80 + "\n"
        
        for r in records:
            status_marker = "[ACTIVE]" if r.status == "ACTIVE" else "[CLOSED]"
            chain_info = f" -> supersedes PK {r.superseded_by}" if r.superseded_by else ""
            latest_tag = " [LATEST]" if r.is_latest else ""
            
            output += f"\n{status_marker} PK: {r.pk}{latest_tag}{chain_info}\n"
            output += f"   Status: {r.status}\n"
            
            for col in self.adapter.value_cols:
                if col in r.data:
                    output += f"   {col}: {r.data[col]}\n"
            
            for col in self.adapter.extra_cols:
                if col in r.data and r.data[col] is not None:
                    output += f"   {col}: {r.data[col]}\n"
            
            if self.adapter.date_col and self.adapter.date_col in r.data:
                output += f"   Date: {r.data[self.adapter.date_col]}\n"
        
        return output


# =========================================================================
# FACTORY
# =========================================================================

def get_cdc_service(table_name: str) -> CDCService:
    """Get CDCService instance for a table"""
    return CDCService(table_name)


# =========================================================================
# DEMO
# =========================================================================

if __name__ == "__main__":
    from config.table_adapters import TABLE_ADAPTERS
    
    print("CDC SERVICE DEMO")
    print("=" * 60)
    
    for table_name in TABLE_ADAPTERS.keys():
        print(f"\n--- {table_name} ---")
        service = get_cdc_service(table_name)
        
        # Show current records
        current = service.get_current_records()
        print(service.format_current_display(current))