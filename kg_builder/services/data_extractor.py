"""
Data Extractor for Landing Database.

Extracts data from source/target databases and loads into landing database
using bulk loading methods (LOAD DATA INFILE for MySQL).
"""
import logging
import csv
import os
import tempfile
import time
import jaydebeapi
from typing import List, Dict, Any, Optional, Tuple
from kg_builder.models import DatabaseConnectionInfo, ReconciliationRule
from kg_builder.services.landing_db_connector import LandingDBConnector
from kg_builder.services.staging_manager import StagingManager
from kg_builder import config

logger = logging.getLogger(__name__)


class DataExtractor:
    """Extracts data from source/target databases to landing database."""

    def __init__(
        self,
        landing_connector: LandingDBConnector,
        staging_manager: StagingManager
    ):
        """
        Initialize data extractor.

        Args:
            landing_connector: Landing database connector
            staging_manager: Staging table manager
        """
        self.landing_connector = landing_connector
        self.staging_manager = staging_manager
        logger.info("Initialized DataExtractor")

    def extract_to_landing(
        self,
        source_db_config: DatabaseConnectionInfo,
        rules: List[ReconciliationRule],
        execution_id: str,
        ruleset_id: str,
        source_or_target: str,  # 'source' or 'target'
        limit: Optional[int] = None
    ) -> Tuple[str, int, float]:
        """
        Extract data from source/target database to landing staging table.

        Args:
            source_db_config: Source database configuration
            rules: List of reconciliation rules
            execution_id: Execution ID
            ruleset_id: Ruleset ID
            source_or_target: 'source' or 'target'
            limit: Limit number of rows (None for all)

        Returns:
            Tuple of (staging_table_name, row_count, extraction_time_ms)
        """
        start_time = time.time()

        try:
            # Connect to source database
            source_conn = self._connect_to_database(source_db_config)

            # Determine which tables and columns to extract
            tables_to_extract = self._get_tables_from_rules(rules, source_or_target)

            # Extract each table (for now, we'll handle one table; can extend for multiple)
            # In a multi-table scenario, you'd create one staging table per source table
            # For simplicity, we'll extract the first rule's table
            if not tables_to_extract:
                raise ValueError("No tables to extract from rules")

            table_info = tables_to_extract[0]
            schema = table_info['schema']
            table = table_info['table']
            columns = table_info['columns']

            logger.info(f"Extracting {source_or_target} data from {schema}.{table}")

            # Generate staging table name
            staging_table_name = self.staging_manager.generate_staging_table_name(
                execution_id=execution_id,
                source_or_target=source_or_target
            )

            # Extract data from source
            data, column_names, column_types = self._extract_data_from_source(
                source_conn=source_conn,
                source_db_config=source_db_config,
                schema=schema,
                table=table,
                columns=columns,
                limit=limit
            )

            logger.info(f"Extracted {len(data)} rows from {schema}.{table}")

            # Create staging table in landing DB
            column_defs = self._build_column_definitions(column_names, column_types)
            self.staging_manager.create_staging_table(
                table_name=staging_table_name,
                columns=column_defs,
                execution_id=execution_id,
                ruleset_id=ruleset_id,
                source_or_target=source_or_target,
                source_db_type=source_db_config.db_type,
                source_db_host=source_db_config.host
            )

            # Load data into landing DB
            row_count = self._bulk_load_to_landing(
                staging_table_name=staging_table_name,
                column_names=column_names,
                data=data
            )

            # Create indexes on join columns
            join_columns = table_info.get('join_columns', [])
            if join_columns:
                self.staging_manager.create_indexes(staging_table_name, join_columns)

            # Update row count in metadata
            self.staging_manager.update_row_count(staging_table_name)

            # Close source connection
            source_conn.close()

            extraction_time_ms = (time.time() - start_time) * 1000
            logger.info(
                f"Extraction complete: {row_count} rows in {extraction_time_ms:.2f}ms "
                f"({row_count/(extraction_time_ms/1000):.0f} rows/sec)"
            )

            return staging_table_name, row_count, extraction_time_ms

        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            raise

    def _connect_to_database(self, db_config: DatabaseConnectionInfo) -> Any:
        """Connect to source/target database using JDBC."""
        try:
            jdbc_url = self._build_jdbc_url(db_config)
            driver_class = self._get_driver_class(db_config.db_type)
            driver_jar = self._get_driver_jar(db_config.db_type)

            logger.debug(f"Connecting to {jdbc_url}")

            conn = jaydebeapi.connect(
                driver_class,
                jdbc_url,
                [db_config.username, db_config.password],
                driver_jar
            )

            logger.debug("Database connection established")
            return conn

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def _build_jdbc_url(self, db_config: DatabaseConnectionInfo) -> str:
        """Build JDBC URL based on database type."""
        db_type = db_config.db_type.lower()

        if db_type == "oracle":
            if db_config.service_name:
                return f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}/{db_config.service_name}"
            else:
                return f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}:{db_config.database}"
        elif db_type == "sqlserver":
            return f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database}"
        elif db_type == "mysql":
            return f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}"
        elif db_type == "postgresql":
            return f"jdbc:postgresql://{db_config.host}:{db_config.port}/{db_config.database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def _get_driver_class(self, db_type: str) -> str:
        """Get JDBC driver class for database type."""
        db_type = db_type.lower()
        drivers = {
            "oracle": "oracle.jdbc.OracleDriver",
            "sqlserver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
            "mysql": "com.mysql.cj.jdbc.Driver",
            "postgresql": "org.postgresql.Driver"
        }
        return drivers.get(db_type, "")

    def _get_driver_jar(self, db_type: str) -> str:
        """Get JDBC driver JAR path for database type."""
        jdbc_dir = config.JDBC_DRIVERS_PATH
        db_type = db_type.lower()

        jar_patterns = {
            "oracle": "ojdbc*.jar",
            "sqlserver": "mssql-jdbc*.jar",
            "mysql": "mysql-connector-j*.jar",
            "postgresql": "postgresql-*.jar"
        }

        import glob
        pattern = os.path.join(jdbc_dir, jar_patterns.get(db_type, "*.jar"))
        jars = glob.glob(pattern)

        if not jars:
            logger.warning(f"No JDBC driver found for {db_type} at {pattern}")
            return ""

        return jars[0]

    def _get_tables_from_rules(
        self,
        rules: List[ReconciliationRule],
        source_or_target: str
    ) -> List[Dict[str, Any]]:
        """
        Extract unique tables and columns from rules.

        NOTE: We extract ALL columns from each table (not just rule columns)
        to ensure all columns are available for JOIN operations, even if some
        rules get filtered out during validation.
        """
        tables_map = {}

        for rule in rules:
            if source_or_target == 'source':
                key = f"{rule.source_schema}.{rule.source_table}"
                if key not in tables_map:
                    tables_map[key] = {
                        'schema': rule.source_schema,
                        'table': rule.source_table,
                        'columns': '*',  # Extract ALL columns
                        'join_columns': set(rule.source_columns)
                    }
                else:
                    # Track join columns for indexing
                    tables_map[key]['join_columns'].update(rule.source_columns)
            else:  # target
                key = f"{rule.target_schema}.{rule.target_table}"
                if key not in tables_map:
                    tables_map[key] = {
                        'schema': rule.target_schema,
                        'table': rule.target_table,
                        'columns': '*',  # Extract ALL columns
                        'join_columns': set(rule.target_columns)
                    }
                else:
                    # Track join columns for indexing
                    tables_map[key]['join_columns'].update(rule.target_columns)

        # Convert join_columns sets to lists
        for table_info in tables_map.values():
            table_info['join_columns'] = list(table_info['join_columns'])

        return list(tables_map.values())

    def _extract_data_from_source(
        self,
        source_conn: Any,
        source_db_config: DatabaseConnectionInfo,
        schema: str,
        table: str,
        columns,  # Can be '*' (string) or List[str]
        limit: Optional[int]
    ) -> Tuple[List[tuple], List[str], List[str]]:
        """Extract data from source database."""
        # If no specific columns, select all
        if not columns or columns == '*' or columns == ['*']:
            columns_clause = "*"
            logger.info(f"Extracting ALL columns from {schema}.{table}")
        else:
            columns_clause = ", ".join([f'"{col}"' if source_db_config.db_type == 'oracle' else f"`{col}`" for col in columns])
            logger.info(f"Extracting {len(columns)} columns from {schema}.{table}")

        # Build query
        limit_clause = ""
        if limit:
            if source_db_config.db_type.lower() == "oracle":
                limit_clause = f"WHERE ROWNUM <= {limit}"
            elif source_db_config.db_type.lower() == "sqlserver":
                limit_clause = f"TOP {limit}"
                query = f"SELECT {limit_clause} {columns_clause} FROM {schema}.{table}"
            else:  # MySQL, PostgreSQL
                limit_clause = f"LIMIT {limit}"

        if source_db_config.db_type.lower() != "sqlserver":
            query = f"SELECT {columns_clause} FROM {schema}.{table} {limit_clause}"

        logger.debug(f"Extraction query: {query}")

        cursor = source_conn.cursor()
        cursor.execute(query)

        # Get column names and types from cursor description
        column_names = [desc[0] for desc in cursor.description]
        column_types = [desc[1] for desc in cursor.description]

        # Fetch all data
        data = cursor.fetchall()
        cursor.close()

        return data, column_names, column_types

    def _build_column_definitions(
        self,
        column_names: List[str],
        column_types: List[Any]
    ) -> List[Dict[str, str]]:
        """Build column definitions for staging table."""
        column_defs = []

        for col_name, col_type in zip(column_names, column_types):
            # Map JDBC types to MySQL types (simplified)
            # In production, you'd have more sophisticated type mapping
            mysql_type = self._map_jdbc_type_to_mysql(col_type)

            column_defs.append({
                'name': col_name,
                'type': mysql_type,
                'nullable': True
            })

        return column_defs

    def _map_jdbc_type_to_mysql(self, jdbc_type: Any) -> str:
        """Map JDBC type to MySQL type."""
        # This is a simplified mapping
        # In production, use jdbc_type's type code
        type_str = str(jdbc_type).upper()

        if 'CHAR' in type_str or 'TEXT' in type_str:
            return 'TEXT'
        elif 'INT' in type_str or 'NUMBER' in type_str:
            return 'BIGINT'
        elif 'DECIMAL' in type_str or 'NUMERIC' in type_str:
            return 'DECIMAL(38,10)'
        elif 'FLOAT' in type_str or 'DOUBLE' in type_str:
            return 'DOUBLE'
        elif 'DATE' in type_str:
            return 'DATETIME'
        elif 'TIMESTAMP' in type_str:
            return 'TIMESTAMP'
        elif 'BOOL' in type_str:
            return 'BOOLEAN'
        else:
            return 'TEXT'

    def _bulk_load_to_landing(
        self,
        staging_table_name: str,
        column_names: List[str],
        data: List[tuple]
    ) -> int:
        """
        Bulk load data into landing database using LOAD DATA INFILE.

        Args:
            staging_table_name: Target staging table
            column_names: List of column names
            data: Data rows

        Returns:
            Number of rows inserted
        """
        if not data:
            return 0

        if config.LANDING_USE_BULK_COPY:
            return self._bulk_load_with_load_data_infile(
                staging_table_name, column_names, data
            )
        else:
            return self._bulk_load_with_batch_insert(
                staging_table_name, column_names, data
            )

    def _bulk_load_with_load_data_infile(
        self,
        staging_table_name: str,
        column_names: List[str],
        data: List[tuple]
    ) -> int:
        """Bulk load using MySQL LOAD DATA LOCAL INFILE."""
        try:
            # Create temporary CSV file
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                newline='',
                suffix='.csv',
                delete=False,
                encoding='utf-8'
            )

            try:
                # Write data to CSV
                writer = csv.writer(temp_file, quoting=csv.QUOTE_MINIMAL)
                for row in data:
                    # Convert None to NULL string and handle other types
                    cleaned_row = []
                    for val in row:
                        if val is None:
                            cleaned_row.append('\\N')  # MySQL NULL representation
                        else:
                            cleaned_row.append(str(val))
                    writer.writerow(cleaned_row)

                temp_file.close()

                # Load data using LOAD DATA INFILE
                columns_clause = ', '.join([f"`{col}`" for col in column_names])

                load_sql = f"""
                LOAD DATA LOCAL INFILE '{temp_file.name.replace(chr(92), '/')}'
                INTO TABLE `{staging_table_name}`
                FIELDS TERMINATED BY ','
                OPTIONALLY ENCLOSED BY '"'
                LINES TERMINATED BY '\\n'
                ({columns_clause})
                """

                with self.landing_connector.cursor() as cursor:
                    cursor.execute(load_sql)
                    row_count = cursor.rowcount

                logger.info(f"Bulk loaded {row_count} rows using LOAD DATA INFILE")
                return row_count

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file.name)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")

        except Exception as e:
            logger.warning(f"LOAD DATA INFILE failed: {e}. Falling back to batch insert.")
            return self._bulk_load_with_batch_insert(staging_table_name, column_names, data)

    def _bulk_load_with_batch_insert(
        self,
        staging_table_name: str,
        column_names: List[str],
        data: List[tuple]
    ) -> int:
        """Bulk load using batch INSERT statements."""
        batch_size = config.LANDING_BATCH_SIZE
        total_inserted = 0

        try:
            columns_clause = ', '.join([f"`{col}`" for col in column_names])
            placeholders = ', '.join(['%s'] * len(column_names))
            insert_sql = f"""
            INSERT INTO `{staging_table_name}` ({columns_clause})
            VALUES ({placeholders})
            """

            # Insert in batches
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]

                with self.landing_connector.cursor(dictionary=False) as cursor:
                    cursor.executemany(insert_sql, batch)
                    total_inserted += len(batch)

                if (i // batch_size + 1) % 10 == 0:
                    logger.debug(f"Inserted {total_inserted}/{len(data)} rows")

            logger.info(f"Batch inserted {total_inserted} rows")
            return total_inserted

        except Exception as e:
            logger.error(f"Batch insert failed: {e}")
            raise


def get_data_extractor(
    landing_connector: Optional[LandingDBConnector] = None,
    staging_manager: Optional[StagingManager] = None
) -> Optional[DataExtractor]:
    """
    Get data extractor instance.

    Args:
        landing_connector: Landing database connector
        staging_manager: Staging manager

    Returns:
        DataExtractor or None if not configured
    """
    if landing_connector is None:
        from kg_builder.services.landing_db_connector import get_landing_connector
        landing_connector = get_landing_connector()

    if landing_connector is None:
        return None

    if staging_manager is None:
        from kg_builder.services.staging_manager import get_staging_manager
        staging_manager = get_staging_manager(landing_connector)

    return DataExtractor(landing_connector, staging_manager)
