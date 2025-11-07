#!/usr/bin/env python3
"""
Export KPIs from SQLite to SQL Script
Generates SQL INSERT statements that can be run on MS SQL Server to migrate KPIs.
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configure basic logging
def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def escape_sql_string(value):
    """Escape string for SQL insertion."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    # Escape single quotes and wrap in quotes
    escaped = str(value).replace("'", "''")
    return f"N'{escaped}'"

def export_kpis_from_sqlite(db_path: str = "data/landing_kpi.db"):
    """Export KPIs from SQLite and generate SQL script."""
    
    log("🔍 Checking SQLite database...")
    
    if not os.path.exists(db_path):
        log(f"❌ SQLite database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all KPIs
        cursor.execute("""
            SELECT 
                id, name, alias_name, group_name, description, nl_definition,
                created_at, updated_at, created_by, is_active
            FROM kpi_definitions
            ORDER BY id
        """)
        
        kpis = cursor.fetchall()
        log(f"📊 Found {len(kpis)} KPIs in SQLite")
        
        if not kpis:
            log("⚠️ No KPIs found to export")
            return False
        
        # Generate SQL script
        sql_script = []
        sql_script.append("-- KPI Migration Script")
        sql_script.append("-- Generated from SQLite to MS SQL Server")
        sql_script.append(f"-- Generated on: {datetime.now()}")
        sql_script.append("-- Database: KPI_Analytics")
        sql_script.append("")
        sql_script.append("USE [KPI_Analytics];")
        sql_script.append("GO")
        sql_script.append("")
        sql_script.append("-- Disable identity insert temporarily")
        sql_script.append("SET IDENTITY_INSERT kpi_definitions ON;")
        sql_script.append("GO")
        sql_script.append("")
        
        # Add each KPI
        for i, kpi in enumerate(kpis, 1):
            log(f"📋 Processing KPI {i}/{len(kpis)}: '{kpi['name']}'")
            
            sql_script.append(f"-- KPI {i}: {kpi['name']}")
            sql_script.append("INSERT INTO kpi_definitions (")
            sql_script.append("    id, name, alias_name, group_name, description, nl_definition,")
            sql_script.append("    created_at, updated_at, created_by, is_active")
            sql_script.append(") VALUES (")
            sql_script.append(f"    {kpi['id']},")
            sql_script.append(f"    {escape_sql_string(kpi['name'])},")
            sql_script.append(f"    {escape_sql_string(kpi['alias_name'])},")
            sql_script.append(f"    {escape_sql_string(kpi['group_name'])},")
            sql_script.append(f"    {escape_sql_string(kpi['description'])},")
            sql_script.append(f"    {escape_sql_string(kpi['nl_definition'])},")
            sql_script.append(f"    {escape_sql_string(kpi['created_at'])},")
            sql_script.append(f"    {escape_sql_string(kpi['updated_at'])},")
            sql_script.append(f"    {escape_sql_string(kpi['created_by'])},")
            sql_script.append(f"    {escape_sql_string(kpi['is_active'])}")
            sql_script.append(");")
            sql_script.append("")
        
        # Get execution results
        cursor.execute("SELECT COUNT(*) FROM kpi_execution_results")
        execution_count = cursor.fetchone()[0]
        
        if execution_count > 0:
            log(f"📈 Found {execution_count} execution results")
            sql_script.append("-- Execution Results")
            sql_script.append("SET IDENTITY_INSERT kpi_execution_results ON;")
            sql_script.append("GO")
            sql_script.append("")
            
            cursor.execute("""
                SELECT
                    id, kpi_id, kg_name, select_schema, ruleset_name, db_type,
                    limit_records, use_llm, excluded_fields, generated_sql,
                    number_of_records, joined_columns, sql_query_type, operation,
                    execution_status, execution_timestamp, execution_time_ms,
                    confidence_score, error_message, result_data,
                    source_table, target_table
                FROM kpi_execution_results
                ORDER BY kpi_id, execution_timestamp DESC
            """)
            
            executions = cursor.fetchall()
            
            for i, exec_result in enumerate(executions, 1):
                if i <= 50:  # Limit to first 50 executions to keep script manageable
                    sql_script.append(f"-- Execution {i}")
                    sql_script.append("INSERT INTO kpi_execution_results (")
                    sql_script.append("    id, kpi_id, kg_name, select_schema, generated_sql,")
                    sql_script.append("    number_of_records, execution_status, execution_timestamp,")
                    sql_script.append("    execution_time_ms, confidence_score, error_message")
                    sql_script.append(") VALUES (")
                    sql_script.append(f"    {exec_result['id']},")
                    sql_script.append(f"    {exec_result['kpi_id']},")
                    sql_script.append(f"    {escape_sql_string(exec_result['kg_name'])},")
                    sql_script.append(f"    {escape_sql_string(exec_result['select_schema'])},")
                    sql_script.append(f"    {escape_sql_string(exec_result['generated_sql'])},")
                    sql_script.append(f"    {exec_result['number_of_records'] or 0},")
                    sql_script.append(f"    {escape_sql_string(exec_result['execution_status'])},")
                    sql_script.append(f"    {escape_sql_string(exec_result['execution_timestamp'])},")
                    sql_script.append(f"    {exec_result['execution_time_ms'] or 0},")
                    sql_script.append(f"    {exec_result['confidence_score'] or 0},")
                    sql_script.append(f"    {escape_sql_string(exec_result['error_message'])}")
                    sql_script.append(");")
                    sql_script.append("")
            
            sql_script.append("SET IDENTITY_INSERT kpi_execution_results OFF;")
            sql_script.append("GO")
            sql_script.append("")
        
        sql_script.append("-- Re-enable identity insert")
        sql_script.append("SET IDENTITY_INSERT kpi_definitions OFF;")
        sql_script.append("GO")
        sql_script.append("")
        sql_script.append("-- Verify migration")
        sql_script.append("SELECT COUNT(*) as 'Total KPIs' FROM kpi_definitions;")
        sql_script.append("SELECT COUNT(*) as 'Total Executions' FROM kpi_execution_results;")
        sql_script.append("GO")
        sql_script.append("")
        sql_script.append("PRINT 'KPI Migration completed successfully!';")
        
        # Write SQL script to file
        output_file = "scripts/migrate_kpis.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_script))
        
        conn.close()
        
        log("="*80)
        log("📊 EXPORT SUMMARY")
        log("="*80)
        log(f"✅ KPIs exported: {len(kpis)}")
        log(f"📈 Execution results: {min(execution_count, 50)} (limited to 50)")
        log(f"📄 SQL script generated: {output_file}")
        log("")
        log("🚀 Next steps:")
        log("1. Review the generated SQL script")
        log("2. Run it on your MS SQL Server:")
        log("   sqlcmd -S your-server -d KPI_Analytics -i scripts/migrate_kpis.sql")
        log("3. Or copy/paste the SQL into SQL Server Management Studio")
        log("")
        log("📋 Sample KPIs to be migrated:")
        for kpi in kpis[:5]:
            log(f"   - {kpi['name']} ({kpi['group_name'] or 'No Group'})")
        if len(kpis) > 5:
            log(f"   ... and {len(kpis) - 5} more")
        
        return True
        
    except Exception as e:
        log(f"❌ Export failed: {e}")
        return False

def main():
    """Main export function."""
    log("🚀 Starting KPI Export from SQLite")
    log("="*80)
    
    success = export_kpis_from_sqlite()
    
    if success:
        log("🎉 Export completed successfully!")
        sys.exit(0)
    else:
        log("❌ Export failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
