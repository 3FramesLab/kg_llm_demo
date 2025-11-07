#!/usr/bin/env python3
"""Check SQLite database schema"""

import sqlite3
import os

def check_schema():
    db_path = "data/landing_kpi.db"
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("KPI Definitions columns:")
    cursor.execute("PRAGMA table_info(kpi_definitions)")
    for col in cursor.fetchall():
        print(f"  {col[1]} ({col[2]})")
    
    print("\nExecution Results columns:")
    cursor.execute("PRAGMA table_info(kpi_execution_results)")
    for col in cursor.fetchall():
        print(f"  {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
