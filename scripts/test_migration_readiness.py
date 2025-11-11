#!/usr/bin/env python3
"""
Test Migration Readiness
Checks if both SQLite and MS SQL Server databases are ready for KPI migration.
"""

import sqlite3
import pyodbc
import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kg_builder.config import (
    SOURCE_DB_HOST, SOURCE_DB_PORT, SOURCE_DB_DATABASE, 
    SOURCE_DB_USERNAME, SOURCE_DB_PASSWORD
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_sqlite_database(db_path: str = "data/landing_kpi.db"):
    """Test SQLite database connection and content."""
    logger.info("🔍 Testing SQLite Database...")
    
    try:
        if not os.path.exists(db_path):
            logger.error(f"❌ SQLite database not found: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'kpi_definitions' not in tables:
            logger.error("❌ kpi_definitions table not found in SQLite")
            return False
        
        if 'kpi_execution_results' not in tables:
            logger.warning("⚠️ kpi_execution_results table not found in SQLite")
        
        # Count KPIs
        cursor.execute("SELECT COUNT(*) FROM kpi_definitions")
        kpi_count = cursor.fetchone()[0]
        
        # Count executions
        cursor.execute("SELECT COUNT(*) FROM kpi_execution_results")
        execution_count = cursor.fetchone()[0]
        
        # Sample KPIs
        cursor.execute("SELECT name, group_name FROM kpi_definitions LIMIT 5")
        sample_kpis = cursor.fetchall()
        
        conn.close()
        
        logger.info(f"✅ SQLite database ready")
        logger.info(f"   📊 KPIs found: {kpi_count}")
        logger.info(f"   📈 Execution results: {execution_count}")
        logger.info(f"   📋 Sample KPIs:")
        for name, group in sample_kpis:
            logger.info(f"      - {name} ({group or 'No Group'})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SQLite test failed: {e}")
        return False


def test_mssql_database(host: str = None, database: str = "KPI_Analytics"):
    """Test MS SQL Server database connection and schema."""
    logger.info("🔍 Testing MS SQL Server Database...")
    
    try:
        host = host or SOURCE_DB_HOST
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={host};"
            f"DATABASE={database};"
            f"UID={SOURCE_DB_USERNAME};"
            f"PWD={SOURCE_DB_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'kpi_definitions' not in tables:
            logger.error("❌ kpi_definitions table not found in MS SQL Server")
            return False
        
        if 'kpi_execution_results' not in tables:
            logger.error("❌ kpi_execution_results table not found in MS SQL Server")
            return False
        
        # Count existing KPIs
        cursor.execute("SELECT COUNT(*) FROM kpi_definitions")
        kpi_count = cursor.fetchone()[0]
        
        # Count existing executions
        cursor.execute("SELECT COUNT(*) FROM kpi_execution_results")
        execution_count = cursor.fetchone()[0]
        
        # Sample existing KPIs
        cursor.execute("SELECT TOP 5 name, group_name FROM kpi_definitions")
        sample_kpis = cursor.fetchall()
        
        conn.close()
        
        logger.info(f"✅ MS SQL Server database ready")
        logger.info(f"   📊 Existing KPIs: {kpi_count}")
        logger.info(f"   📈 Existing executions: {execution_count}")
        if sample_kpis:
            logger.info(f"   📋 Existing KPIs:")
            for name, group in sample_kpis:
                logger.info(f"      - {name} ({group or 'No Group'})")
        else:
            logger.info(f"   📋 No existing KPIs (fresh database)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MS SQL Server test failed: {e}")
        return False


def test_migration_readiness():
    """Test if migration can proceed."""
    logger.info("="*80)
    logger.info("🧪 TESTING MIGRATION READINESS")
    logger.info("="*80)
    
    sqlite_ready = test_sqlite_database()
    mssql_ready = test_mssql_database()
    
    logger.info("\n" + "="*80)
    logger.info("📊 READINESS SUMMARY")
    logger.info("="*80)
    
    if sqlite_ready and mssql_ready:
        logger.info("🎉 MIGRATION READY!")
        logger.info("✅ SQLite database accessible with KPIs")
        logger.info("✅ MS SQL Server database accessible with schema")
        logger.info("\n🚀 You can now run the migration:")
        logger.info("   python scripts/migrate_kpis_sqlite_to_mssql.py --dry-run")
        logger.info("   python scripts/migrate_kpis_sqlite_to_mssql.py")
        return True
    else:
        logger.error("❌ MIGRATION NOT READY")
        if not sqlite_ready:
            logger.error("❌ SQLite database issues - check if database exists and has KPIs")
        if not mssql_ready:
            logger.error("❌ MS SQL Server database issues - check connection and schema")
        logger.info("\n🔧 Fix the issues above before running migration")
        return False


def main():
    """Main test function."""
    try:
        success = test_migration_readiness()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
