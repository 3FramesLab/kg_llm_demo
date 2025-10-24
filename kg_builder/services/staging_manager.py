"""
Staging Table Manager for Landing Database.

Handles creation, tracking, indexing, and cleanup of staging tables.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from kg_builder.services.landing_db_connector import LandingDBConnector
from kg_builder.models import StagingTableInfo, StagingTableMetadata
from kg_builder import config

logger = logging.getLogger(__name__)


class StagingManager:
    """Manages staging tables in landing database."""

    def __init__(self, connector: LandingDBConnector):
        """
        Initialize staging manager.

        Args:
            connector: Landing database connector
        """
        self.connector = connector
        self.schema = config.LANDING_DB_SCHEMA
        logger.info(f"Initialized StagingManager with schema: {self.schema}")

    def generate_staging_table_name(
        self,
        execution_id: str,
        source_or_target: str,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate unique staging table name.

        Args:
            execution_id: Execution ID
            source_or_target: 'source' or 'target'
            timestamp: Optional timestamp (uses current if not provided)

        Returns:
            Staging table name
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        ts = timestamp.strftime("%Y%m%d_%H%M%S")
        return f"recon_stage_{execution_id}_{source_or_target}_{ts}"

    def create_staging_table(
        self,
        table_name: str,
        columns: List[Dict[str, str]],
        execution_id: str,
        ruleset_id: str,
        source_or_target: str,
        source_db_type: str,
        source_db_host: str
    ) -> str:
        """
        Create staging table with specified columns.

        Args:
            table_name: Name of staging table
            columns: List of column definitions [{'name': 'col1', 'type': 'VARCHAR(255)'}, ...]
            execution_id: Execution ID
            ruleset_id: Ruleset ID
            source_or_target: 'source' or 'target'
            source_db_type: Source database type
            source_db_host: Source database host

        Returns:
            Table name created
        """
        try:
            # Build column definitions
            column_defs = []
            for col in columns:
                col_name = col['name']
                col_type = col.get('type', 'TEXT')
                nullable = col.get('nullable', True)
                null_clause = '' if nullable else 'NOT NULL'
                column_defs.append(f"`{col_name}` {col_type} {null_clause}")

            columns_sql = ',\n    '.join(column_defs)

            # Create table
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                `_staging_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
                `_created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                {columns_sql}
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """

            with self.connector.cursor() as cursor:
                cursor.execute(create_table_sql)

            logger.info(f"Created staging table: {table_name} with {len(columns)} columns")

            # Store metadata
            self._store_staging_metadata(
                table_name=table_name,
                execution_id=execution_id,
                ruleset_id=ruleset_id,
                source_or_target=source_or_target,
                source_db_type=source_db_type,
                source_db_host=source_db_host,
                row_count=0
            )

            return table_name

        except Exception as e:
            logger.error(f"Failed to create staging table {table_name}: {e}")
            raise

    def create_indexes(
        self,
        table_name: str,
        index_columns: List[str]
    ) -> List[str]:
        """
        Create indexes on staging table for join performance.

        Args:
            table_name: Staging table name
            index_columns: Columns to index

        Returns:
            List of created index names
        """
        created_indexes = []

        try:
            for col in index_columns:
                index_name = f"idx_{table_name}_{col}"[:64]  # MySQL index name limit

                create_index_sql = f"""
                CREATE INDEX `{index_name}`
                ON `{table_name}` (`{col}`)
                """

                try:
                    with self.connector.cursor() as cursor:
                        cursor.execute(create_index_sql)
                    created_indexes.append(index_name)
                    logger.debug(f"Created index: {index_name}")
                except Exception as e:
                    # Index might already exist
                    if "Duplicate key name" not in str(e):
                        logger.warning(f"Failed to create index {index_name}: {e}")

            logger.info(f"Created {len(created_indexes)} indexes on {table_name}")
            return created_indexes

        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return created_indexes

    def get_staging_table_info(self, table_name: str) -> Optional[StagingTableInfo]:
        """
        Get information about a staging table.

        Args:
            table_name: Staging table name

        Returns:
            StagingTableInfo or None if not found
        """
        try:
            # Get row count
            row_count_result = self.connector.execute_one(
                f"SELECT COUNT(*) as count FROM `{table_name}`"
            )
            row_count = row_count_result.get('count', 0) if row_count_result else 0

            # Get table size
            size_result = self.connector.execute_one(f"""
                SELECT
                    ROUND((data_length + index_length) / 1024 / 1024, 2) as size_mb
                FROM information_schema.tables
                WHERE table_schema = '{self.connector.db_config.database}'
                AND table_name = '{table_name}'
            """)
            size_mb = size_result.get('size_mb', 0) if size_result else 0

            # Get indexes
            indexes = []
            try:
                indexes_result = self.connector.execute(f"""
                    SELECT DISTINCT index_name
                    FROM information_schema.statistics
                    WHERE table_schema = '{self.connector.db_config.database}'
                    AND table_name = '{table_name}'
                    AND index_name != 'PRIMARY'
                """)
                if indexes_result:
                    # Handle both uppercase and lowercase column names
                    for idx in indexes_result:
                        idx_name = idx.get('index_name') or idx.get('INDEX_NAME') or idx.get('Index_name')
                        if idx_name:
                            indexes.append(idx_name)
            except Exception as e:
                logger.debug(f"Could not fetch indexes: {e}")

            # Get created_at from metadata or table
            created_at_result = self.connector.execute_one(
                f"SELECT MIN(_created_at) as created_at FROM `{table_name}`"
            )
            created_at = created_at_result.get('created_at') if created_at_result else datetime.utcnow()

            return StagingTableInfo(
                table_name=table_name,
                row_count=row_count,
                created_at=created_at,
                size_mb=size_mb,
                indexes=indexes
            )

        except Exception as e:
            logger.error(f"Failed to get staging table info for {table_name}: {e}")
            return None

    def update_row_count(self, table_name: str) -> int:
        """
        Update row count in metadata table.

        Args:
            table_name: Staging table name

        Returns:
            Row count
        """
        try:
            result = self.connector.execute_one(
                f"SELECT COUNT(*) as count FROM `{table_name}`"
            )
            row_count = result.get('count', 0) if result else 0

            # Update metadata if table exists
            try:
                with self.connector.cursor() as cursor:
                    cursor.execute("""
                        UPDATE staging_table_metadata
                        SET row_count = %s
                        WHERE table_name = %s
                    """, (row_count, table_name))
            except Exception:
                # Metadata table might not exist yet
                pass

            return row_count

        except Exception as e:
            logger.error(f"Failed to update row count for {table_name}: {e}")
            return 0

    def drop_staging_table(self, table_name: str) -> bool:
        """
        Drop staging table.

        Args:
            table_name: Table name to drop

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.connector.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

            logger.info(f"Dropped staging table: {table_name}")

            # Update metadata status
            try:
                with self.connector.cursor() as cursor:
                    cursor.execute("""
                        UPDATE staging_table_metadata
                        SET status = 'deleted'
                        WHERE table_name = %s
                    """, (table_name,))
            except Exception:
                # Metadata might not exist
                pass

            return True

        except Exception as e:
            logger.error(f"Failed to drop staging table {table_name}: {e}")
            return False

    def cleanup_expired_tables(self, ttl_hours: Optional[int] = None) -> int:
        """
        Clean up expired staging tables based on TTL.

        Args:
            ttl_hours: Time to live in hours (uses config if not provided)

        Returns:
            Number of tables cleaned up
        """
        if ttl_hours is None:
            ttl_hours = config.LANDING_STAGING_TTL_HOURS

        try:
            # Find expired tables from metadata
            cutoff_time = datetime.utcnow() - timedelta(hours=ttl_hours)

            expired_tables = self.connector.execute("""
                SELECT table_name
                FROM staging_table_metadata
                WHERE created_at < %s
                AND status = 'active'
            """, (cutoff_time,))

            cleaned_count = 0
            for row in expired_tables:
                table_name = row['table_name']
                if self.drop_staging_table(table_name):
                    cleaned_count += 1

            logger.info(f"Cleaned up {cleaned_count} expired staging tables (TTL: {ttl_hours}h)")
            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired tables: {e}")
            return 0

    def list_staging_tables(self, active_only: bool = True) -> List[StagingTableMetadata]:
        """
        List all staging tables.

        Args:
            active_only: Only return active tables (not deleted)

        Returns:
            List of StagingTableMetadata
        """
        try:
            query = """
                SELECT *
                FROM staging_table_metadata
                WHERE 1=1
            """
            if active_only:
                query += " AND status = 'active'"

            query += " ORDER BY created_at DESC"

            results = self.connector.execute(query)

            tables = []
            for row in results:
                tables.append(StagingTableMetadata(**row))

            return tables

        except Exception as e:
            logger.error(f"Failed to list staging tables: {e}")
            return []

    def _store_staging_metadata(
        self,
        table_name: str,
        execution_id: str,
        ruleset_id: str,
        source_or_target: str,
        source_db_type: str,
        source_db_host: str,
        row_count: int
    ):
        """Store metadata about staging table."""
        try:
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(hours=config.LANDING_STAGING_TTL_HOURS)

            with self.connector.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO staging_table_metadata
                    (table_name, execution_id, ruleset_id, source_or_target,
                     source_db_type, source_db_host, row_count, created_at, expires_at, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    table_name, execution_id, ruleset_id, source_or_target,
                    source_db_type, source_db_host, row_count, created_at, expires_at, 'active'
                ))

            logger.debug(f"Stored metadata for staging table: {table_name}")

        except Exception as e:
            # Metadata table might not exist yet, that's OK
            logger.debug(f"Could not store staging metadata: {e}")


def get_staging_manager(connector: Optional[LandingDBConnector] = None) -> Optional[StagingManager]:
    """
    Get staging manager instance.

    Args:
        connector: Landing database connector (creates if not provided)

    Returns:
        StagingManager or None if landing DB not configured
    """
    if connector is None:
        from kg_builder.services.landing_db_connector import get_landing_connector
        connector = get_landing_connector()

    if connector is None:
        return None

    return StagingManager(connector)
