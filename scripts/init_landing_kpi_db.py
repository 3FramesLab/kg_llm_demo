"""
Initialize Landing KPI SQLite Database

This script creates the SQLite database schema for the Landing KPI CRUD Management system.
Database location: data/landing_kpi.db

Tables:
- kpi_definitions: Master KPI configuration
- kpi_execution_results: Execution history and results
"""

import sqlite3
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_landing_kpi_db(db_path: str = "data/landing_kpi.db"):
    """Initialize Landing KPI database with schema."""
    
    # Create data directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created directory: {db_dir}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ==================== KPI Definitions Table ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpi_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL UNIQUE,
                alias_name VARCHAR(255),
                group_name VARCHAR(255),
                description TEXT,
                nl_definition TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(100),
                is_active BOOLEAN DEFAULT 1
            )
        """)
        logger.info("✓ Created table: kpi_definitions")
        
        # ==================== KPI Execution Results Table ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpi_execution_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kpi_id INTEGER NOT NULL,
                
                -- Execution Parameters
                kg_name VARCHAR(255) NOT NULL,
                select_schema VARCHAR(255) NOT NULL,
                ruleset_name VARCHAR(255),
                db_type VARCHAR(50) DEFAULT 'mysql',
                limit_records INTEGER DEFAULT 1000,
                use_llm BOOLEAN DEFAULT 1,
                excluded_fields TEXT,
                
                -- Execution Results
                generated_sql TEXT,
                number_of_records INTEGER DEFAULT 0,
                joined_columns TEXT,
                sql_query_type VARCHAR(100),
                operation VARCHAR(50),
                
                -- Additional Metadata
                execution_status VARCHAR(50) DEFAULT 'pending',
                execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time_ms REAL,
                confidence_score REAL,
                error_message TEXT,
                
                -- Query Result Data Storage
                result_data TEXT,
                source_table VARCHAR(255),
                target_table VARCHAR(255),
                
                FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE
            )
        """)
        logger.info("✓ Created table: kpi_execution_results")
        
        # ==================== Create Indexes ====================
        indexes = [
            ("idx_kpi_name", "kpi_definitions", "name"),
            ("idx_kpi_active", "kpi_definitions", "is_active"),
            ("idx_execution_kpi_id", "kpi_execution_results", "kpi_id"),
            ("idx_execution_timestamp", "kpi_execution_results", "execution_timestamp DESC"),
            ("idx_execution_status", "kpi_execution_results", "execution_status"),
        ]
        
        for idx_name, table_name, columns in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({columns})")
                logger.info(f"✓ Created index: {idx_name}")
            except sqlite3.OperationalError as e:
                logger.warning(f"Index {idx_name} may already exist: {e}")
        
        conn.commit()
        logger.info("✅ Database initialization completed successfully!")
        logger.info(f"Database location: {os.path.abspath(db_path)}")
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_database(db_path: str = "data/landing_kpi.db"):
    """Verify database schema is correctly created."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('kpi_definitions', 'kpi_execution_results')
        """)
        tables = cursor.fetchall()
        
        if len(tables) == 2:
            logger.info("✅ All required tables exist")
            
            # Check columns in kpi_definitions
            cursor.execute("PRAGMA table_info(kpi_definitions)")
            kpi_cols = [row[1] for row in cursor.fetchall()]
            logger.info(f"kpi_definitions columns: {', '.join(kpi_cols)}")
            
            # Check columns in kpi_execution_results
            cursor.execute("PRAGMA table_info(kpi_execution_results)")
            exec_cols = [row[1] for row in cursor.fetchall()]
            logger.info(f"kpi_execution_results columns: {', '.join(exec_cols)}")
            
            return True
        else:
            logger.error(f"❌ Expected 2 tables, found {len(tables)}")
            return False
            
    finally:
        conn.close()


if __name__ == "__main__":
    db_path = "data/landing_kpi.db"
    
    logger.info("=" * 60)
    logger.info("Landing KPI Database Initialization")
    logger.info("=" * 60)
    
    # Initialize database
    init_landing_kpi_db(db_path)
    
    # Verify
    logger.info("\n" + "=" * 60)
    logger.info("Verifying Database Schema")
    logger.info("=" * 60)
    verify_database(db_path)

