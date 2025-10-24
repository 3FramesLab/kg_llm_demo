"""
Initialize Landing Database.

Creates the necessary database, schemas, and metadata tables for landing database operations.
Run this script once before using the landing database feature.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import pymysql
from kg_builder import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_database():
    """Create landing database if it doesn't exist."""
    try:
        # Connect without selecting database
        conn = pymysql.connect(
            host=config.LANDING_DB_HOST,
            port=config.LANDING_DB_PORT,
            user=config.LANDING_DB_USERNAME,
            password=config.LANDING_DB_PASSWORD,
            charset='utf8mb4'
        )

        with conn.cursor() as cursor:
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config.LANDING_DB_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"✓ Database '{config.LANDING_DB_DATABASE}' created/verified")

        conn.close()
        return True

    except Exception as e:
        logger.error(f"✗ Failed to create database: {e}")
        return False


def create_metadata_tables():
    """Create metadata tables for tracking staging tables and executions."""
    try:
        conn = pymysql.connect(
            host=config.LANDING_DB_HOST,
            port=config.LANDING_DB_PORT,
            user=config.LANDING_DB_USERNAME,
            password=config.LANDING_DB_PASSWORD,
            database=config.LANDING_DB_DATABASE,
            charset='utf8mb4'
        )

        with conn.cursor() as cursor:
            # Create staging_table_metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `staging_table_metadata` (
                    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
                    `table_name` VARCHAR(255) NOT NULL UNIQUE,
                    `execution_id` VARCHAR(100) NOT NULL,
                    `ruleset_id` VARCHAR(100) NOT NULL,
                    `source_or_target` ENUM('source', 'target') NOT NULL,
                    `source_db_type` VARCHAR(50) NOT NULL,
                    `source_db_host` VARCHAR(255) NOT NULL,
                    `row_count` BIGINT DEFAULT 0,
                    `size_bytes` BIGINT DEFAULT NULL,
                    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `expires_at` TIMESTAMP NOT NULL,
                    `status` ENUM('active', 'expired', 'deleted') DEFAULT 'active',
                    INDEX `idx_execution_id` (`execution_id`),
                    INDEX `idx_ruleset_id` (`ruleset_id`),
                    INDEX `idx_created_at` (`created_at`),
                    INDEX `idx_expires_at` (`expires_at`),
                    INDEX `idx_status` (`status`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            logger.info("✓ Table 'staging_table_metadata' created/verified")

            # Create execution_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `execution_history` (
                    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
                    `execution_id` VARCHAR(100) NOT NULL UNIQUE,
                    `ruleset_id` VARCHAR(100) NOT NULL,
                    `execution_type` VARCHAR(50) DEFAULT 'landing_database',
                    `source_db_type` VARCHAR(50),
                    `target_db_type` VARCHAR(50),
                    `matched_count` BIGINT DEFAULT 0,
                    `unmatched_source_count` BIGINT DEFAULT 0,
                    `unmatched_target_count` BIGINT DEFAULT 0,
                    `total_source_count` BIGINT DEFAULT 0,
                    `total_target_count` BIGINT DEFAULT 0,
                    `rcr` DECIMAL(5,2) DEFAULT 0,
                    `dqcs` DECIMAL(5,3) DEFAULT 0,
                    `rei` DECIMAL(10,2) DEFAULT 0,
                    `extraction_time_ms` DECIMAL(15,2) DEFAULT 0,
                    `reconciliation_time_ms` DECIMAL(15,2) DEFAULT 0,
                    `total_time_ms` DECIMAL(15,2) DEFAULT 0,
                    `mongodb_document_id` VARCHAR(100),
                    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX `idx_ruleset_id` (`ruleset_id`),
                    INDEX `idx_created_at` (`created_at`),
                    INDEX `idx_rcr` (`rcr`),
                    INDEX `idx_dqcs` (`dqcs`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            logger.info("✓ Table 'execution_history' created/verified")

            # Create indexes on execution_history
            try:
                cursor.execute("""
                    CREATE INDEX `idx_execution_type` ON `execution_history` (`execution_type`)
                """)
            except pymysql.err.OperationalError:
                # Index might already exist
                pass

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"✗ Failed to create metadata tables: {e}")
        return False


def test_connection():
    """Test connection to landing database."""
    try:
        from kg_builder.services.landing_db_connector import get_landing_connector

        connector = get_landing_connector()
        if connector is None:
            logger.error("✗ Landing database is not configured")
            return False

        if connector.health_check():
            logger.info("✓ Landing database connection successful")

            # Get database info
            db_info = connector.get_database_info()
            logger.info(f"  Database: {db_info['database']}")
            logger.info(f"  Version: {db_info['version']}")
            logger.info(f"  Size: {db_info['size_mb']} MB")
            logger.info(f"  Staging tables: {db_info['staging_table_count']}")
            return True
        else:
            logger.error("✗ Landing database health check failed")
            return False

    except Exception as e:
        logger.error(f"✗ Connection test failed: {e}")
        return False


def main():
    """Main initialization function."""
    logger.info("=" * 60)
    logger.info("Landing Database Initialization")
    logger.info("=" * 60)

    # Check configuration
    if not config.LANDING_DB_ENABLED:
        logger.error("✗ Landing database is not enabled. Set LANDING_DB_ENABLED=true in .env")
        return False

    if not config.LANDING_DB_USERNAME or not config.LANDING_DB_PASSWORD:
        logger.error("✗ Landing database credentials not configured. Set LANDING_DB_USERNAME and LANDING_DB_PASSWORD in .env")
        return False

    logger.info(f"Configuration:")
    logger.info(f"  Host: {config.LANDING_DB_HOST}:{config.LANDING_DB_PORT}")
    logger.info(f"  Database: {config.LANDING_DB_DATABASE}")
    logger.info(f"  Username: {config.LANDING_DB_USERNAME}")
    logger.info(f"  Schema: {config.LANDING_DB_SCHEMA}")
    logger.info(f"  Keep Staging: {config.LANDING_KEEP_STAGING}")
    logger.info(f"  TTL: {config.LANDING_STAGING_TTL_HOURS} hours")
    logger.info("")

    # Step 1: Create database
    logger.info("Step 1: Creating database...")
    if not create_database():
        return False
    logger.info("")

    # Step 2: Create metadata tables
    logger.info("Step 2: Creating metadata tables...")
    if not create_metadata_tables():
        return False
    logger.info("")

    # Step 3: Test connection
    logger.info("Step 3: Testing connection...")
    if not test_connection():
        return False
    logger.info("")

    logger.info("=" * 60)
    logger.info("✓ Landing database initialization complete!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Configure source and target database connections in .env")
    logger.info("2. Run demo_landing_reconciliation.py to test the system")
    logger.info("3. Use the API endpoint POST /api/v1/reconciliation/execute-with-landing")
    logger.info("")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
