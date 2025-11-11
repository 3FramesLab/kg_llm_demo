#!/usr/bin/env python3
"""
KPI Data Migration Script
Migrates existing KPI data from SQLite to MS SQL Server.
"""

import sqlite3
import json
import logging
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def migrate_kpi_data():
    """Migrate KPI data from SQLite to MS SQL Server."""
    
    print("="*60)
    print("KPI DATA MIGRATION: SQLite → MS SQL Server")
    print("="*60)
    
    # Paths
    sqlite_db_path = Path("data/landing_kpi.db")
    
    if not sqlite_db_path.exists():
        print(f"❌ SQLite database not found: {sqlite_db_path}")
        print("   No data to migrate.")
        return
    
    try:
        # Initialize MS SQL Server service
        mssql_service = LandingKPIServiceMSSQL()
        print(f"✓ Connected to MS SQL Server: {mssql_service.host}/{mssql_service.database}")
        
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name
        sqlite_cursor = sqlite_conn.cursor()
        
        print(f"✓ Connected to SQLite: {sqlite_db_path}")
        
        # ==================== Migrate KPI Definitions ====================
        
        print("\n--- Migrating KPI Definitions ---")
        
        sqlite_cursor.execute("""
            SELECT name, alias_name, group_name, description, nl_definition, 
                   created_at, created_by, is_active
            FROM kpi_definitions
            WHERE is_active = 1
        """)
        
        kpi_definitions = sqlite_cursor.fetchall()
        print(f"Found {len(kpi_definitions)} KPI definitions to migrate")
        
        kpi_id_mapping = {}  # SQLite ID → MS SQL Server ID
        
        for sqlite_kpi in kpi_definitions:
            try:
                kpi_data = {
                    'name': sqlite_kpi['name'],
                    'alias_name': sqlite_kpi['alias_name'],
                    'group_name': sqlite_kpi['group_name'],
                    'description': sqlite_kpi['description'],
                    'nl_definition': sqlite_kpi['nl_definition'],
                    'created_by': sqlite_kpi['created_by'] or 'migration'
                }
                
                # Check if KPI already exists
                existing_kpis = mssql_service.get_all_kpis()
                existing_names = [kpi['name'] for kpi in existing_kpis]
                
                if kpi_data['name'] in existing_names:
                    print(f"  ⚠️  KPI '{kpi_data['name']}' already exists, skipping")
                    continue
                
                # Create KPI in MS SQL Server
                new_kpi = mssql_service.create_kpi(kpi_data)
                kpi_id_mapping[sqlite_kpi['name']] = new_kpi['id']
                
                print(f"  ✓ Migrated KPI: {kpi_data['name']} (ID: {new_kpi['id']})")
                
            except Exception as e:
                print(f"  ❌ Failed to migrate KPI '{sqlite_kpi['name']}': {e}")
        
        print(f"✓ Migrated {len(kpi_id_mapping)} KPI definitions")
        
        # ==================== Migrate Execution Results ====================
        
        print("\n--- Migrating Execution Results ---")
        
        sqlite_cursor.execute("""
            SELECT kd.name as kpi_name, ker.*
            FROM kpi_execution_results ker
            JOIN kpi_definitions kd ON ker.kpi_id = kd.id
            ORDER BY ker.execution_timestamp DESC
            LIMIT 100  -- Migrate only recent executions
        """)
        
        execution_results = sqlite_cursor.fetchall()
        print(f"Found {len(execution_results)} execution results to migrate")
        
        migrated_executions = 0
        
        for sqlite_execution in execution_results:
            try:
                kpi_name = sqlite_execution['kpi_name']
                
                # Skip if KPI wasn't migrated
                if kpi_name not in kpi_id_mapping:
                    continue
                
                mssql_kpi_id = kpi_id_mapping[kpi_name]
                
                # Create execution record
                execution_params = {
                    'kg_name': sqlite_execution['kg_name'],
                    'select_schema': sqlite_execution['select_schema'],
                    'db_type': sqlite_execution['db_type'] or 'sqlserver',
                    'limit_records': sqlite_execution['limit_records'] or 1000,
                    'use_llm': bool(sqlite_execution['use_llm']),
                    'user_id': 'migration'
                }
                
                execution_record = mssql_service.create_execution_record(mssql_kpi_id, execution_params)
                
                # Update with results
                result_data = {
                    'generated_sql': sqlite_execution['generated_sql'],
                    'number_of_records': sqlite_execution['number_of_records'] or 0,
                    'joined_columns': json.loads(sqlite_execution['joined_columns'] or '[]'),
                    'sql_query_type': sqlite_execution['sql_query_type'],
                    'operation': sqlite_execution['operation'],
                    'execution_status': sqlite_execution['execution_status'] or 'success',
                    'execution_time_ms': sqlite_execution['execution_time_ms'],
                    'confidence_score': sqlite_execution['confidence_score'],
                    'error_message': sqlite_execution['error_message'],
                    'result_data': json.loads(sqlite_execution['result_data'] or '[]'),
                    'evidence_data': [],  # SQLite didn't store evidence data
                    'source_table': sqlite_execution['source_table'],
                    'target_table': sqlite_execution['target_table']
                }
                
                mssql_service.update_execution_result(execution_record['id'], result_data)
                migrated_executions += 1
                
                print(f"  ✓ Migrated execution for KPI: {kpi_name}")
                
            except Exception as e:
                print(f"  ❌ Failed to migrate execution for '{kpi_name}': {e}")
        
        print(f"✓ Migrated {migrated_executions} execution results")
        
        # ==================== Summary ====================
        
        print(f"\n{'='*60}")
        print("MIGRATION COMPLETE")
        print(f"{'='*60}")
        print(f"✓ KPI Definitions: {len(kpi_id_mapping)} migrated")
        print(f"✓ Execution Results: {migrated_executions} migrated")
        print(f"✓ Target Database: {mssql_service.host}/{mssql_service.database}")
        print("")
        print("Next Steps:")
        print("1. Test the new MS SQL Server endpoints")
        print("2. Update your application to use the new API routes")
        print("3. Backup the SQLite database before removing it")
        print("")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
    
    return True


if __name__ == "__main__":
    success = migrate_kpi_data()
    sys.exit(0 if success else 1)
