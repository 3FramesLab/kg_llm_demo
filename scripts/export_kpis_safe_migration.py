#!/usr/bin/env python3
"""
Safe KPI Migration - Handles Duplicates
Generates SQL script that safely migrates KPIs without duplicate key errors.
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

def export_kpis_safe_migration(db_path: str = "data/landing_kpi.db"):
    """Export KPIs with safe migration that handles duplicates."""
    
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
        
        # Generate SAFE SQL script
        sql_script = []
        sql_script.append("-- SAFE KPI Migration Script")
        sql_script.append("-- Generated from SQLite to MS SQL Server")
        sql_script.append("-- Handles duplicates by checking existing KPIs first")
        sql_script.append(f"-- Generated on: {datetime.now()}")
        sql_script.append("-- Database: KPI_Analytics")
        sql_script.append("")
        sql_script.append("USE [KPI_Analytics];")
        sql_script.append("GO")
        sql_script.append("")
        sql_script.append("PRINT 'Starting SAFE KPI Migration...';")
        sql_script.append("GO")
        sql_script.append("")
        
        # Add each KPI with duplicate checking
        for i, kpi in enumerate(kpis, 1):
            log(f"📋 Processing KPI {i}/{len(kpis)}: '{kpi['name']}'")
            
            sql_script.append(f"-- KPI {i}: {kpi['name']}")
            sql_script.append(f"PRINT 'Processing KPI: {kpi['name']}';")
            sql_script.append("")
            
            # Check if KPI already exists by name
            sql_script.append("IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = " + escape_sql_string(kpi['name']) + ")")
            sql_script.append("BEGIN")
            sql_script.append("    PRINT '  -> Inserting new KPI';")
            sql_script.append("    INSERT INTO kpi_definitions (")
            sql_script.append("        name, alias_name, group_name, description, nl_definition,")
            sql_script.append("        created_at, updated_at, created_by, is_active")
            sql_script.append("    ) VALUES (")
            sql_script.append(f"        {escape_sql_string(kpi['name'])},")
            sql_script.append(f"        {escape_sql_string(kpi['alias_name'])},")
            sql_script.append(f"        {escape_sql_string(kpi['group_name'])},")
            sql_script.append(f"        {escape_sql_string(kpi['description'])},")
            sql_script.append(f"        {escape_sql_string(kpi['nl_definition'])},")
            sql_script.append(f"        {escape_sql_string(kpi['created_at'])},")
            sql_script.append(f"        {escape_sql_string(kpi['updated_at'])},")
            sql_script.append(f"        {escape_sql_string(kpi['created_by'])},")
            sql_script.append(f"        {escape_sql_string(kpi['is_active'])}")
            sql_script.append("    );")
            sql_script.append("END")
            sql_script.append("ELSE")
            sql_script.append("BEGIN")
            sql_script.append("    PRINT '  -> KPI already exists, skipping';")
            sql_script.append("END")
            sql_script.append("GO")
            sql_script.append("")
        
        # Get execution results (limited sample)
        cursor.execute("SELECT COUNT(*) FROM kpi_execution_results")
        execution_count = cursor.fetchone()[0]
        
        if execution_count > 0:
            log(f"📈 Found {execution_count} execution results")
            sql_script.append("-- Sample Execution Results (Recent ones only)")
            sql_script.append("PRINT 'Adding sample execution results...';")
            sql_script.append("GO")
            sql_script.append("")
            
            # Get recent executions for each KPI (limit to avoid huge script)
            cursor.execute("""
                SELECT 
                    id, kpi_id, kg_name, select_schema, generated_sql,
                    number_of_records, execution_status, execution_timestamp,
                    execution_time_ms, confidence_score, error_message
                FROM kpi_execution_results
                WHERE id IN (
                    SELECT MAX(id) 
                    FROM kpi_execution_results 
                    GROUP BY kpi_id
                )
                ORDER BY kpi_id
            """)
            
            executions = cursor.fetchall()
            
            for i, exec_result in enumerate(executions, 1):
                sql_script.append(f"-- Latest execution for KPI ID {exec_result['kpi_id']}")
                
                # Find the KPI name for this execution
                kpi_name = "Unknown"
                for kpi in kpis:
                    if kpi['id'] == exec_result['kpi_id']:
                        kpi_name = kpi['name']
                        break
                
                sql_script.append("-- Get the new KPI ID after migration")
                sql_script.append("DECLARE @kpi_id INT;")
                sql_script.append("SELECT @kpi_id = id FROM kpi_definitions WHERE name = " + escape_sql_string(kpi_name) + ";")
                sql_script.append("")
                sql_script.append("IF @kpi_id IS NOT NULL")
                sql_script.append("BEGIN")
                sql_script.append("    INSERT INTO kpi_execution_results (")
                sql_script.append("        kpi_id, kg_name, select_schema, generated_sql,")
                sql_script.append("        number_of_records, execution_status, execution_timestamp,")
                sql_script.append("        execution_time_ms, confidence_score, error_message")
                sql_script.append("    ) VALUES (")
                sql_script.append("        @kpi_id,")
                sql_script.append(f"        {escape_sql_string(exec_result['kg_name'])},")
                sql_script.append(f"        {escape_sql_string(exec_result['select_schema'])},")
                sql_script.append(f"        {escape_sql_string(exec_result['generated_sql'])},")
                sql_script.append(f"        {exec_result['number_of_records'] or 0},")
                sql_script.append(f"        {escape_sql_string(exec_result['execution_status'])},")
                sql_script.append(f"        {escape_sql_string(exec_result['execution_timestamp'])},")
                sql_script.append(f"        {exec_result['execution_time_ms'] or 0},")
                sql_script.append(f"        {exec_result['confidence_score'] or 0},")
                sql_script.append(f"        {escape_sql_string(exec_result['error_message'])}")
                sql_script.append("    );")
                sql_script.append("    PRINT '  -> Added execution result';")
                sql_script.append("END")
                sql_script.append("GO")
                sql_script.append("")
        
        # Final verification
        sql_script.append("-- Final Verification")
        sql_script.append("PRINT 'Migration completed! Summary:';")
        sql_script.append("SELECT COUNT(*) as 'Total KPIs' FROM kpi_definitions;")
        sql_script.append("SELECT COUNT(*) as 'Total Executions' FROM kpi_execution_results;")
        sql_script.append("")
        sql_script.append("-- Show sample of migrated KPIs")
        sql_script.append("PRINT 'Sample migrated KPIs:';")
        sql_script.append("SELECT TOP 10 name, group_name, created_at FROM kpi_definitions ORDER BY created_at DESC;")
        sql_script.append("GO")
        sql_script.append("")
        sql_script.append("PRINT 'SAFE KPI Migration completed successfully!';")
        
        # Write SQL script to file
        output_file = "scripts/migrate_kpis_safe.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_script))
        
        conn.close()
        
        log("="*80)
        log("📊 SAFE EXPORT SUMMARY")
        log("="*80)
        log(f"✅ KPIs exported: {len(kpis)}")
        log(f"📈 Latest execution results: {min(execution_count, len(kpis))}")
        log(f"📄 SAFE SQL script generated: {output_file}")
        log("")
        log("🛡️ SAFE MIGRATION FEATURES:")
        log("✅ Checks for existing KPIs before inserting")
        log("✅ Skips duplicates automatically")
        log("✅ Uses KPI names instead of IDs for linking")
        log("✅ Provides detailed progress messages")
        log("")
        log("🚀 Next steps:")
        log("1. Review the generated SAFE SQL script")
        log("2. Run it on your MS SQL Server:")
        log(f"   sqlcmd -S your-server -d KPI_Analytics -i {output_file}")
        log("3. Or copy/paste the SQL into SQL Server Management Studio")
        log("")
        log("📋 This script will safely migrate without duplicate errors!")
        
        return True
        
    except Exception as e:
        log(f"❌ Export failed: {e}")
        return False

def main():
    """Main export function."""
    log("🛡️ Starting SAFE KPI Migration Export")
    log("="*80)
    
    success = export_kpis_safe_migration()
    
    if success:
        log("🎉 SAFE export completed successfully!")
        sys.exit(0)
    else:
        log("❌ Export failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
