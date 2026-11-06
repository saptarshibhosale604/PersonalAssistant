#!/usr/bin/env python3
"""
Database Backup to CSV Utility
Script location: Langchain/Tools/ToolsSqlDatabase/backup_to_csv.py
Backs up all tables from all SQLite databases in CloudPII/ToolsSqlDatabase/
to timestamped CSV files in CloudPII/ToolsSqlDatabase/Backup/.
"""

import sqlite3
import csv
import os
import glob
from datetime import datetime
from pathlib import Path

# Configuration - Script is at Langchain/Tools/ToolsSqlDatabase/backup_to_csv.py
# Databases are at CloudPII/ToolsSqlDatabase/
# Backups go to CloudPII/ToolsSqlDatabase/Backup/
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # Go up to PersonalAssistant root
DB_DIR = PROJECT_ROOT / "CloudPII" / "ToolsSqlDatabase"
BACKUP_DIR = DB_DIR / "Backup"
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

def get_database_files():
    """Discover all .db files in the database directory."""
    return list(DB_DIR.glob("*.db"))

def get_tables_and_views(conn):
    """Retrieve all tables and views from a database connection."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")
    return [row[0] for row in cursor.fetchall()]

def export_table_to_csv(conn, table_name, output_path):
    """Export a single table/view to CSV."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    return len(rows)

def main():
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    db_files = get_database_files()
    
    if not db_files:
        print("❌ No database files found!")
        return
    
    print(f"[MISSION START] Backing up {len(db_files)} database(s) at {timestamp}")
    print(f"[TARGET] {BACKUP_DIR}")
    
    total_tables = 0
    total_rows = 0
    
    for db_path in db_files:
        db_name = db_path.stem
        print(f"\n[PROCESSING] Database: {db_name}")
        
        try:
            conn = sqlite3.connect(db_path)
            tables = get_tables_and_views(conn)
            
            if not tables:
                print(f"   [WARNING] No tables/views found in {db_name}")
                conn.close()
                continue
            
            for table in tables:
                # Skip sqlite_sequence (internal table)
                if table == 'sqlite_sequence':
                    continue
                
                csv_filename = f"{db_name}__{table}_{timestamp}.csv"
                csv_path = BACKUP_DIR / csv_filename
                
                row_count = export_table_to_csv(conn, table, csv_path)
                total_tables += 1
                total_rows += row_count
                print(f"   [OK] {table} -> {csv_filename} ({row_count} rows)")
            
            conn.close()
            
        except Exception as e:
            print(f"   [ERROR] Processing {db_name}: {e}")
    
    print(f"\n[MISSION COMPLETE]")
    print(f"   Databases processed: {len(db_files)}")
    print(f"   Tables/Views backed up: {total_tables}")
    print(f"   Total rows exported: {total_rows}")
    print(f"   Backup location: {BACKUP_DIR}")

if __name__ == "__main__":
    main()