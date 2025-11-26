"""
Initialize Groups/Dashboards Database for MySQL.

Creates the necessary database and tables for groups and dashboards management.
Run this script once before using the groups/dashboards feature.
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
    """Create groups database if it doesn't exist."""
    try:
        # Connect without selecting database
        conn = pymysql.connect(
            host=config.GROUPS_DB_HOST,
            port=config.GROUPS_DB_PORT,
            user=config.GROUPS_DB_USERNAME,
            password=config.GROUPS_DB_PASSWORD,
            charset='utf8mb4'
        )

        with conn.cursor() as cursor:
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config.GROUPS_DB_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"✓ Database '{config.GROUPS_DB_DATABASE}' created/verified")

        conn.close()
        return True

    except Exception as e:
        logger.error(f"✗ Failed to create database: {e}")
        return False


def create_tables():
    """Create groups and dashboards tables."""
    try:
        conn = pymysql.connect(
            host=config.GROUPS_DB_HOST,
            port=config.GROUPS_DB_PORT,
            user=config.GROUPS_DB_USERNAME,
            password=config.GROUPS_DB_PASSWORD,
            database=config.GROUPS_DB_DATABASE,
            charset='utf8mb4'
        )

        with conn.cursor() as cursor:
            # Create groups table (note: backticks because 'groups' is a reserved keyword)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `groups` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `code` VARCHAR(50) UNIQUE NOT NULL,
                    `name` VARCHAR(255) NOT NULL,
                    `description` TEXT,
                    `color` VARCHAR(20),
                    `icon` VARCHAR(50),
                    `is_active` BOOLEAN DEFAULT TRUE,
                    `created_by` VARCHAR(100) DEFAULT 'system',
                    `updated_by` VARCHAR(100) DEFAULT 'system',
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_groups_is_active` (`is_active`),
                    INDEX `idx_groups_code` (`code`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            logger.info("✓ Table 'groups' created/verified")

            # Create dashboards table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `dashboards` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `code` VARCHAR(50) UNIQUE NOT NULL,
                    `name` VARCHAR(255) NOT NULL,
                    `description` TEXT,
                    `layout` JSON,
                    `widgets` JSON,
                    `is_active` BOOLEAN DEFAULT TRUE,
                    `created_by` VARCHAR(100) DEFAULT 'system',
                    `updated_by` VARCHAR(100) DEFAULT 'system',
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_dashboards_is_active` (`is_active`),
                    INDEX `idx_dashboards_code` (`code`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            logger.info("✓ Table 'dashboards' created/verified")

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"✗ Failed to create tables: {e}")
        return False


def test_connection():
    """Test database connection and verify tables."""
    try:
        conn = pymysql.connect(
            host=config.GROUPS_DB_HOST,
            port=config.GROUPS_DB_PORT,
            user=config.GROUPS_DB_USERNAME,
            password=config.GROUPS_DB_PASSWORD,
            database=config.GROUPS_DB_DATABASE,
            charset='utf8mb4'
        )

        with conn.cursor() as cursor:
            # Check groups table
            cursor.execute("SELECT COUNT(*) FROM `groups`")
            groups_count = cursor.fetchone()[0]
            logger.info(f"✓ Groups table: {groups_count} records")

            # Check dashboards table
            cursor.execute("SELECT COUNT(*) FROM `dashboards`")
            dashboards_count = cursor.fetchone()[0]
            logger.info(f"✓ Dashboards table: {dashboards_count} records")

        conn.close()
        return True

    except Exception as e:
        logger.error(f"✗ Connection test failed: {e}")
        return False


def insert_sample_data():
    """Insert sample groups and dashboards for testing."""
    try:
        conn = pymysql.connect(
            host=config.GROUPS_DB_HOST,
            port=config.GROUPS_DB_PORT,
            user=config.GROUPS_DB_USERNAME,
            password=config.GROUPS_DB_PASSWORD,
            database=config.GROUPS_DB_DATABASE,
            charset='utf8mb4'
        )

        with conn.cursor() as cursor:
            # Check if sample data already exists
            cursor.execute("SELECT COUNT(*) FROM `groups`")
            if cursor.fetchone()[0] > 0:
                logger.info("✓ Sample data already exists, skipping...")
                conn.close()
                return True

            # Insert sample group
            cursor.execute("""
                INSERT INTO `groups` (code, name, description, color, icon, is_active, created_by)
                VALUES ('SAMPLE_GROUP', 'Sample Group', 'A sample group for testing', '#5B6FE5', 'dashboard', TRUE, 'system')
            """)
            logger.info("✓ Inserted sample group")

            # Get the group ID
            group_id = cursor.lastrowid

            # Insert sample dashboard
            cursor.execute("""
                INSERT INTO `dashboards` (code, name, description, layout, widgets, is_active, created_by)
                VALUES (
                    'SAMPLE_DASHBOARD',
                    'Sample Dashboard',
                    'A sample dashboard for testing',
                    '{"columns": 12, "rows": 6}',
                    '[{"id": "widget1", "type": "chart", "title": "Sample Chart"}]',
                    TRUE,
                    'system'
                )
            """)
            logger.info("✓ Inserted sample dashboard")

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"✗ Failed to insert sample data: {e}")
        return False


def main():
    """Main initialization function."""
    logger.info("=" * 60)
    logger.info("Groups/Dashboards Database Initialization")
    logger.info("=" * 60)
    logger.info("")

    logger.info(f"Configuration:")
    logger.info(f"  Host: {config.GROUPS_DB_HOST}:{config.GROUPS_DB_PORT}")
    logger.info(f"  Database: {config.GROUPS_DB_DATABASE}")
    logger.info(f"  Username: {config.GROUPS_DB_USERNAME}")
    logger.info(f"  Database Type: {config.GROUPS_DB_TYPE}")
    logger.info("")

    # Step 1: Create database
    logger.info("Step 1: Creating database...")
    if not create_database():
        return False
    logger.info("")

    # Step 2: Create tables
    logger.info("Step 2: Creating tables...")
    if not create_tables():
        return False
    logger.info("")

    # Step 3: Test connection
    logger.info("Step 3: Testing connection...")
    if not test_connection():
        return False
    logger.info("")

    # Step 4: Insert sample data
    logger.info("Step 4: Inserting sample data...")
    if not insert_sample_data():
        logger.warning("⚠ Sample data insertion failed, but database is ready")
    logger.info("")

    logger.info("=" * 60)
    logger.info("✓ Groups/Dashboards database initialization complete!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Restart your application to load the new JDBC service")
    logger.info("2. Test the API endpoint GET /api/v1/groups")
    logger.info("3. Use POST /api/v1/groups to create new groups")
    logger.info("4. Use POST /api/v1/dashboards to create new dashboards")
    logger.info("")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

