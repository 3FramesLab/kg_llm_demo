#!/usr/bin/env python3
"""
KPI Migration Script: SQLite to MS SQL Server
Migrates all KPI definitions and execution results from SQLite to MS SQL Server.
"""

import sqlite3
import pyodbc
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kg_builder.config import (
    SOURCE_DB_HOST, SOURCE_DB_PORT, SOURCE_DB_DATABASE, 
    SOURCE_DB_USERNAME, SOURCE_DB_PASSWORD
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KPIMigrator:
    """Migrates KPIs from SQLite to MS SQL Server."""
    
    def __init__(self, 
                 sqlite_path: str = "data/landing_kpi.db",
                 mssql_host: str = None,
                 mssql_database: str = "KPI_Analytics"):
        """Initialize the migrator."""
        self.sqlite_path = sqlite_path
        self.mssql_host = mssql_host or SOURCE_DB_HOST
        self.mssql_database = mssql_database
        self.mssql_username = SOURCE_DB_USERNAME
        self.mssql_password = SOURCE_DB_PASSWORD
        
        logger.info("KPI Migrator initialized")
        logger.info(f"Source: SQLite ({sqlite_path})")
        logger.info(f"Target: MS SQL Server ({self.mssql_host}/{mssql_database})")
    
    def get_sqlite_connection(self):
        """Get SQLite connection."""
        if not os.path.exists(self.sqlite_path):
            raise FileNotFoundError(f"SQLite database not found: {self.sqlite_path}")
        
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_mssql_connection(self):
        """Get MS SQL Server connection."""
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.mssql_host};"
            f"DATABASE={self.mssql_database};"
            f"UID={self.mssql_username};"
            f"PWD={self.mssql_password};"
            f"TrustServerCertificate=yes;"
        )
        return pyodbc.connect(connection_string)
    
    def test_connections(self) -> bool:
        """Test both database connections."""
        logger.info("Testing database connections...")
        
        try:
            # Test SQLite
            sqlite_conn = self.get_sqlite_connection()
            cursor = sqlite_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM kpi_definitions")
            sqlite_count = cursor.fetchone()[0]
            sqlite_conn.close()
            logger.info(f"✓ SQLite connection successful - {sqlite_count} KPIs found")
            
            # Test MS SQL Server
            mssql_conn = self.get_mssql_connection()
            cursor = mssql_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM kpi_definitions")
            mssql_count = cursor.fetchone()[0]
            mssql_conn.close()
            logger.info(f"✓ MS SQL Server connection successful - {mssql_count} KPIs currently exist")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    def get_sqlite_kpis(self) -> List[Dict[str, Any]]:
        """Get all KPIs from SQLite."""
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    id, name, alias_name, group_name, description, nl_definition,
                    created_at, updated_at, created_by, is_active
                FROM kpi_definitions
                ORDER BY id
            """)
            
            kpis = []
            for row in cursor.fetchall():
                kpi = {
                    'id': row['id'],
                    'name': row['name'],
                    'alias_name': row['alias_name'],
                    'group_name': row['group_name'],
                    'description': row['description'],
                    'nl_definition': row['nl_definition'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'created_by': row['created_by'],
                    'is_active': bool(row['is_active'])
                }
                kpis.append(kpi)
            
            logger.info(f"Retrieved {len(kpis)} KPIs from SQLite")
            return kpis
            
        finally:
            conn.close()
    
    def get_sqlite_executions(self, sqlite_kpi_id: int) -> List[Dict[str, Any]]:
        """Get all execution results for a KPI from SQLite."""
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    id, kpi_id, kg_name, select_schema, ruleset_name, db_type,
                    limit_records, use_llm, excluded_fields, generated_sql,
                    number_of_records, joined_columns, sql_query_type, operation,
                    execution_status, execution_timestamp, execution_time_ms,
                    confidence_score, error_message, result_data, evidence_data,
                    evidence_count, source_table, target_table, user_id,
                    session_id, client_ip, user_agent
                FROM kpi_execution_results
                WHERE kpi_id = ?
                ORDER BY execution_timestamp DESC
            """, (sqlite_kpi_id,))
            
            executions = []
            for row in cursor.fetchall():
                execution = {
                    'sqlite_id': row['id'],
                    'kpi_id': row['kpi_id'],
                    'kg_name': row['kg_name'],
                    'select_schema': row['select_schema'],
                    'ruleset_name': row['ruleset_name'],
                    'db_type': row['db_type'],
                    'limit_records': row['limit_records'],
                    'use_llm': bool(row['use_llm']) if row['use_llm'] is not None else None,
                    'excluded_fields': row['excluded_fields'],
                    'generated_sql': row['generated_sql'],
                    'number_of_records': row['number_of_records'],
                    'joined_columns': row['joined_columns'],
                    'sql_query_type': row['sql_query_type'],
                    'operation': row['operation'],
                    'execution_status': row['execution_status'],
                    'execution_timestamp': row['execution_timestamp'],
                    'execution_time_ms': row['execution_time_ms'],
                    'confidence_score': row['confidence_score'],
                    'error_message': row['error_message'],
                    'result_data': row['result_data'],
                    'evidence_data': row['evidence_data'],
                    'evidence_count': row['evidence_count'],
                    'source_table': row['source_table'],
                    'target_table': row['target_table'],
                    'user_id': row['user_id'],
                    'session_id': row['session_id'],
                    'client_ip': row['client_ip'],
                    'user_agent': row['user_agent']
                }
                executions.append(execution)
            
            return executions
            
        finally:
            conn.close()
    
    def check_kpi_exists_in_mssql(self, name: str) -> Optional[int]:
        """Check if KPI already exists in MS SQL Server."""
        conn = self.get_mssql_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM kpi_definitions WHERE name = ?", (name,))
            row = cursor.fetchone()
            return row[0] if row else None
            
        finally:
            conn.close()

    def migrate_kpi_definition(self, kpi: Dict[str, Any]) -> int:
        """Migrate a single KPI definition to MS SQL Server."""
        conn = self.get_mssql_connection()
        cursor = conn.cursor()

        try:
            # Check if KPI already exists
            existing_id = self.check_kpi_exists_in_mssql(kpi['name'])
            if existing_id:
                logger.info(f"KPI '{kpi['name']}' already exists with ID {existing_id}, skipping...")
                return existing_id

            # Insert new KPI
            cursor.execute("""
                INSERT INTO kpi_definitions (
                    name, alias_name, group_name, description, nl_definition,
                    created_at, updated_at, created_by, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi['name'],
                kpi['alias_name'],
                kpi['group_name'],
                kpi['description'],
                kpi['nl_definition'],
                kpi['created_at'],
                kpi['updated_at'],
                kpi['created_by'],
                kpi['is_active']
            ))

            # Get the new ID
            cursor.execute("SELECT @@IDENTITY")
            new_id = cursor.fetchone()[0]

            conn.commit()
            logger.info(f"✓ Migrated KPI '{kpi['name']}' -> ID {new_id}")
            return new_id

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to migrate KPI '{kpi['name']}': {e}")
            raise
        finally:
            conn.close()

    def migrate_execution_results(self, executions: List[Dict[str, Any]], new_kpi_id: int) -> int:
        """Migrate execution results for a KPI."""
        if not executions:
            return 0

        conn = self.get_mssql_connection()
        cursor = conn.cursor()
        migrated_count = 0

        try:
            for execution in executions:
                try:
                    cursor.execute("""
                        INSERT INTO kpi_execution_results (
                            kpi_id, kg_name, select_schema, ruleset_name, db_type,
                            limit_records, use_llm, excluded_fields, generated_sql,
                            number_of_records, joined_columns, sql_query_type, operation,
                            execution_status, execution_timestamp, execution_time_ms,
                            confidence_score, error_message, result_data, evidence_data,
                            evidence_count, source_table, target_table, user_id,
                            session_id, client_ip, user_agent
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        new_kpi_id,  # Use new KPI ID
                        execution['kg_name'],
                        execution['select_schema'],
                        execution['ruleset_name'],
                        execution['db_type'],
                        execution['limit_records'],
                        execution['use_llm'],
                        execution['excluded_fields'],
                        execution['generated_sql'],
                        execution['number_of_records'],
                        execution['joined_columns'],
                        execution['sql_query_type'],
                        execution['operation'],
                        execution['execution_status'],
                        execution['execution_timestamp'],
                        execution['execution_time_ms'],
                        execution['confidence_score'],
                        execution['error_message'],
                        execution['result_data'],
                        execution['evidence_data'],
                        execution['evidence_count'],
                        execution['source_table'],
                        execution['target_table'],
                        execution['user_id'],
                        execution['session_id'],
                        execution['client_ip'],
                        execution['user_agent']
                    ))
                    migrated_count += 1

                except Exception as e:
                    logger.warning(f"Failed to migrate execution {execution['sqlite_id']}: {e}")
                    continue

            conn.commit()
            logger.info(f"✓ Migrated {migrated_count} execution results")
            return migrated_count

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to migrate execution results: {e}")
            raise
        finally:
            conn.close()

    def migrate_all_kpis(self, include_executions: bool = True) -> Dict[str, int]:
        """Migrate all KPIs from SQLite to MS SQL Server."""
        logger.info("="*80)
        logger.info("🚀 STARTING KPI MIGRATION")
        logger.info("="*80)

        # Test connections first
        if not self.test_connections():
            raise Exception("Database connection test failed")

        # Get all KPIs from SQLite
        sqlite_kpis = self.get_sqlite_kpis()

        if not sqlite_kpis:
            logger.warning("No KPIs found in SQLite database")
            return {'kpis_migrated': 0, 'executions_migrated': 0}

        stats = {
            'kpis_migrated': 0,
            'kpis_skipped': 0,
            'executions_migrated': 0,
            'errors': 0
        }

        # Migrate each KPI
        for i, kpi in enumerate(sqlite_kpis, 1):
            logger.info(f"\n📋 Migrating KPI {i}/{len(sqlite_kpis)}: '{kpi['name']}'")

            try:
                # Migrate KPI definition
                new_kpi_id = self.migrate_kpi_definition(kpi)

                if new_kpi_id:
                    if self.check_kpi_exists_in_mssql(kpi['name']) == new_kpi_id:
                        stats['kpis_migrated'] += 1
                    else:
                        stats['kpis_skipped'] += 1

                    # Migrate execution results if requested
                    if include_executions:
                        executions = self.get_sqlite_executions(kpi['id'])
                        if executions:
                            logger.info(f"  📊 Found {len(executions)} execution results")
                            migrated_executions = self.migrate_execution_results(executions, new_kpi_id)
                            stats['executions_migrated'] += migrated_executions
                        else:
                            logger.info("  📊 No execution results found")

            except Exception as e:
                logger.error(f"❌ Failed to migrate KPI '{kpi['name']}': {e}")
                stats['errors'] += 1
                continue

        # Final summary
        logger.info("\n" + "="*80)
        logger.info("📊 MIGRATION SUMMARY")
        logger.info("="*80)
        logger.info(f"✅ KPIs migrated: {stats['kpis_migrated']}")
        logger.info(f"⏭️  KPIs skipped (already exist): {stats['kpis_skipped']}")
        logger.info(f"📊 Execution results migrated: {stats['executions_migrated']}")
        logger.info(f"❌ Errors: {stats['errors']}")
        logger.info(f"🎯 Success rate: {((stats['kpis_migrated'] + stats['kpis_skipped']) / len(sqlite_kpis) * 100):.1f}%")

        if stats['errors'] == 0:
            logger.info("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        else:
            logger.warning("⚠️ Migration completed with some errors")

        return stats


def main():
    """Main migration function."""
    import argparse

    parser = argparse.ArgumentParser(description='Migrate KPIs from SQLite to MS SQL Server')
    parser.add_argument('--sqlite-path', default='data/landing_kpi.db',
                       help='Path to SQLite database')
    parser.add_argument('--mssql-host', default=None,
                       help='MS SQL Server host (uses config default if not specified)')
    parser.add_argument('--mssql-database', default='KPI_Analytics',
                       help='MS SQL Server database name')
    parser.add_argument('--skip-executions', action='store_true',
                       help='Skip migrating execution results (KPI definitions only)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test connections and show what would be migrated')

    args = parser.parse_args()

    try:
        migrator = KPIMigrator(
            sqlite_path=args.sqlite_path,
            mssql_host=args.mssql_host,
            mssql_database=args.mssql_database
        )

        if args.dry_run:
            logger.info("🧪 DRY RUN MODE - Testing connections and showing migration plan")
            if migrator.test_connections():
                kpis = migrator.get_sqlite_kpis()
                logger.info(f"Would migrate {len(kpis)} KPIs:")
                for kpi in kpis:
                    logger.info(f"  - {kpi['name']} ({kpi['group_name']})")
            return

        # Perform actual migration
        stats = migrator.migrate_all_kpis(include_executions=not args.skip_executions)

        # Exit with appropriate code
        if stats['errors'] == 0:
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
