"""
Reconciliation execution service for running reconciliation rules against databases.

This service executes SQL-based reconciliation queries to find matched and unmatched records.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

try:
    import jaydebeapi
    JAYDEBEAPI_AVAILABLE = True
except ImportError:
    JAYDEBEAPI_AVAILABLE = False
    logging.warning("JayDeBeApi not installed. Database execution will not be available.")

from kg_builder.models import (
    ReconciliationRule,
    ReconciliationRuleSet,
    DatabaseConnectionInfo,
    MatchedRecord,
    RuleExecutionResponse
)
from kg_builder.config import JDBC_DRIVERS_PATH
from kg_builder.services.rule_storage import get_rule_storage

logger = logging.getLogger(__name__)


class ReconciliationExecutor:
    """Execute reconciliation rules against actual databases using SQL."""

    def __init__(self):
        """Initialize the reconciliation executor."""
        self.jdbc_drivers_path = Path(JDBC_DRIVERS_PATH) if JDBC_DRIVERS_PATH else None
        self.storage = get_rule_storage()

    @staticmethod
    def _quote_identifier(identifier: str, db_type: str = "mysql") -> str:
        """
        Quote database identifiers (schema, table, column names) based on database type.

        Args:
            identifier: The identifier to quote (schema, table, or column name)
            db_type: Database type (mysql, oracle, postgresql, sqlserver)

        Returns:
            Quoted identifier appropriate for the database type
        """
        if not identifier:
            return identifier

        db_type = db_type.lower()

        if db_type == "mysql":
            # MySQL uses backticks
            return f"`{identifier}`"
        elif db_type == "oracle":
            # Oracle uses double quotes
            return f'"{identifier}"'
        elif db_type == "postgresql":
            # PostgreSQL uses double quotes
            return f'"{identifier}"'
        elif db_type == "sqlserver":
            # SQL Server uses square brackets
            return f"[{identifier}]"
        else:
            # Default to backticks (MySQL style)
            return f"`{identifier}`"

    def execute_ruleset(
        self,
        ruleset_id: str,
        source_db_config: DatabaseConnectionInfo,
        target_db_config: DatabaseConnectionInfo,
        limit: int = 100,
        include_matched: bool = True,
        include_unmatched: bool = True,
        store_in_mongodb: bool = True
    ) -> RuleExecutionResponse:
        """
        Execute a complete ruleset against databases.

        Args:
            ruleset_id: ID of the ruleset to execute
            source_db_config: Source database connection info
            target_db_config: Target database connection info
            limit: Maximum number of records to return per category
            include_matched: Include matched records in results
            include_unmatched: Include unmatched records in results
            store_in_mongodb: Store results in MongoDB as JSON documents

        Returns:
            RuleExecutionResponse with matched and unmatched records
        """
        if not JAYDEBEAPI_AVAILABLE:
            raise RuntimeError(
                "JayDeBeApi is not installed. "
                "Please install it with: pip install JayDeBeApi"
            )

        logger.info(f"Executing ruleset '{ruleset_id}' with limit={limit}")
        start_time = time.time()

        # Load the ruleset
        ruleset = self.storage.load_ruleset(ruleset_id)
        if not ruleset:
            raise ValueError(f"Ruleset '{ruleset_id}' not found")

        # Connect to databases
        source_conn = None
        target_conn = None

        try:
            # Establish connections
            logger.debug("Connecting to source database...")
            source_conn = self._connect_to_database(source_db_config)
            if not source_conn:
                raise RuntimeError("Failed to connect to source database")

            logger.debug("Connecting to target database...")
            target_conn = self._connect_to_database(target_db_config)
            if not target_conn:
                raise RuntimeError("Failed to connect to target database")

            # Execute all rules
            all_matched = []
            all_unmatched_source = []
            all_unmatched_target = []

            for rule in ruleset.rules:
                logger.debug(f"Executing rule: {rule.rule_name}")

                # Execute matched records query
                if include_matched:
                    matched = self._execute_matched_query(
                        source_conn, target_conn, rule, limit, source_db_config.db_type
                    )
                    all_matched.extend(matched)

                # Execute unmatched queries
                if include_unmatched:
                    unmatched_src = self._execute_unmatched_source_query(
                        source_conn, target_conn, rule, limit, source_db_config.db_type
                    )
                    all_unmatched_source.extend(unmatched_src)

                    unmatched_tgt = self._execute_unmatched_target_query(
                        source_conn, target_conn, rule, limit, source_db_config.db_type
                    )
                    all_unmatched_target.extend(unmatched_tgt)

            elapsed_ms = (time.time() - start_time) * 1000

            # Count inactive records from source data
            inactive_count = self._count_inactive_records(
                source_conn, ruleset, source_db_config.db_type
            )

            logger.info(
                f"Execution complete: {len(all_matched)} matched, "
                f"{len(all_unmatched_source)} unmatched source, "
                f"{len(all_unmatched_target)} unmatched target, "
                f"{inactive_count} inactive records"
            )

            # Prepare response
            response_data = {
                "success": True,
                "matched_count": len(all_matched),
                "unmatched_source_count": len(all_unmatched_source),
                "unmatched_target_count": len(all_unmatched_target),
                "matched_records": all_matched[:limit] if limit else all_matched,
                "unmatched_source": all_unmatched_source[:limit] if limit else all_unmatched_source,
                "unmatched_target": all_unmatched_target[:limit] if limit else all_unmatched_target,
                "execution_time_ms": elapsed_ms,
                "inactive_count": inactive_count
            }

            # Store in MongoDB if requested
            mongodb_doc_id = None
            storage_location = "memory"

            if store_in_mongodb:
                try:
                    from kg_builder.services.mongodb_storage import get_mongodb_storage

                    logger.info("Storing reconciliation results in MongoDB...")
                    mongo_storage = get_mongodb_storage()

                    # Convert MatchedRecord objects to dictionaries for MongoDB storage
                    matched_dicts = [
                        {
                            "source_record": m.source_record,
                            "target_record": m.target_record,
                            "match_confidence": m.match_confidence,
                            "rule_used": m.rule_used,
                            "rule_name": m.rule_name
                        }
                        for m in all_matched
                    ]

                    # Prepare execution metadata
                    execution_metadata = {
                        "execution_time_ms": elapsed_ms,
                        "limit": limit,
                        "source_db_type": source_db_config.db_type,
                        "target_db_type": target_db_config.db_type,
                        "include_matched": include_matched,
                        "include_unmatched": include_unmatched
                    }

                    mongodb_doc_id = mongo_storage.store_reconciliation_result(
                        ruleset_id=ruleset_id,
                        matched_records=matched_dicts,
                        unmatched_source=all_unmatched_source,
                        unmatched_target=all_unmatched_target,
                        execution_metadata=execution_metadata
                    )

                    storage_location = "mongodb"
                    logger.info(f"Results stored in MongoDB with document ID: {mongodb_doc_id}")

                except Exception as e:
                    logger.warning(f"Failed to store results in MongoDB: {e}")
                    # Continue without MongoDB storage

            response_data["mongodb_document_id"] = mongodb_doc_id
            response_data["storage_location"] = storage_location

            return RuleExecutionResponse(**response_data)

        except Exception as e:
            logger.error(f"Error executing ruleset: {e}", exc_info=True)
            raise

        finally:
            # Clean up connections
            if source_conn:
                try:
                    source_conn.close()
                    logger.debug("Source connection closed")
                except Exception as e:
                    logger.error(f"Error closing source connection: {e}")

            if target_conn:
                try:
                    target_conn.close()
                    logger.debug("Target connection closed")
                except Exception as e:
                    logger.error(f"Error closing target connection: {e}")

    def _count_inactive_records(
        self,
        source_conn: Any,
        ruleset: ReconciliationRuleSet,
        db_type: str = "mysql"
    ) -> int:
        """
        Count inactive records in the source database.

        Looks for records where is_active = 0 or is_active IS NULL in the source table.

        Args:
            source_conn: Database connection
            ruleset: The reconciliation ruleset
            db_type: Database type (mysql, oracle, etc.)

        Returns:
            Count of inactive records
        """
        try:
            if not ruleset.rules:
                logger.warning("No rules in ruleset, cannot count inactive records")
                return 0

            # Get the first rule to determine source table
            first_rule = ruleset.rules[0]
            source_schema = first_rule.source_schema
            source_table = first_rule.source_table

            # Quote identifiers based on database type
            schema_quoted = self._quote_identifier(source_schema, db_type)
            table_quoted = self._quote_identifier(source_table, db_type)
            is_active_quoted = self._quote_identifier("is_active", db_type)

            # Build query to count inactive records
            query = f"""
            SELECT COUNT(*) as inactive_count
            FROM {schema_quoted}.{table_quoted}
            WHERE {is_active_quoted} = 0 OR {is_active_quoted} IS NULL
            """

            logger.debug(f"[INACTIVE COUNT QUERY] SQL:\n{query}")

            # Execute query
            cursor = source_conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

            inactive_count = result[0] if result else 0
            logger.info(f"Found {inactive_count} inactive records in {source_schema}.{source_table}")

            return inactive_count

        except Exception as e:
            logger.warning(f"Failed to count inactive records: {e}")
            # Return 0 if we can't count (don't fail the entire execution)
            return 0

    def _execute_matched_query(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule,
        limit: int,
        db_type: str = "mysql"
    ) -> List[MatchedRecord]:
        """Execute query to find matched records."""
        try:
            # Build JOIN query
            join_conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                if rule.transformation:
                    join_conditions.append(f"{rule.transformation} = t.{tgt_col}")
                else:
                    join_conditions.append(f"s.{src_col} = t.{tgt_col}")

            join_condition = " AND ".join(join_conditions)

            # Quote identifiers based on database type
            source_schema_quoted = self._quote_identifier(rule.source_schema, db_type)
            source_table_quoted = self._quote_identifier(rule.source_table, db_type)
            target_schema_quoted = self._quote_identifier(rule.target_schema, db_type)
            target_table_quoted = self._quote_identifier(rule.target_table, db_type)

            # For matched records, we need to join on the same connection
            # Assuming both schemas are on the same database for now
            # Use LIMIT for MySQL, ROWNUM for Oracle
            limit_clause = f"LIMIT {limit}" if db_type.lower() == "mysql" else f"WHERE ROWNUM <= {limit}"

            query = f"""
            SELECT s.*, t.*
            FROM {source_schema_quoted}.{source_table_quoted} s
            INNER JOIN {target_schema_quoted}.{target_table_quoted} t
                ON {join_condition}
            {limit_clause}
            """

            logger.debug(f"[MATCHED QUERY] Rule: {rule.rule_name}")
            logger.debug(f"[MATCHED QUERY] SQL:\n{query}")

            cursor = source_conn.cursor()
            cursor.execute(query)

            # Get column names
            source_columns = []
            target_columns = []
            all_columns = [desc[0] for desc in cursor.description]

            # Fetch results
            rows = cursor.fetchall()
            cursor.close()

            matched_records = []
            for row in rows:
                # Split row data into source and target
                # This is simplified - in production, you'd need better column mapping
                row_dict = dict(zip(all_columns, row))

                matched_records.append(MatchedRecord(
                    source_record=row_dict,  # Simplified
                    target_record=row_dict,  # Simplified
                    match_confidence=rule.confidence_score,
                    rule_used=rule.rule_id,
                    rule_name=rule.rule_name
                ))

            logger.debug(f"Found {len(matched_records)} matched records for rule {rule.rule_name}")
            return matched_records

        except Exception as e:
            logger.error(f"Error executing matched query: {e}")
            return []

    def _execute_unmatched_source_query(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule,
        limit: int,
        db_type: str = "mysql"
    ) -> List[Dict[str, Any]]:
        """Execute query to find unmatched source records."""
        try:
            # Build NOT EXISTS query
            join_conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                if rule.transformation:
                    join_conditions.append(f"{rule.transformation} = t.{tgt_col}")
                else:
                    join_conditions.append(f"s.{src_col} = t.{tgt_col}")

            join_condition = " AND ".join(join_conditions)

            # Quote identifiers based on database type
            source_schema_quoted = self._quote_identifier(rule.source_schema, db_type)
            source_table_quoted = self._quote_identifier(rule.source_table, db_type)
            target_schema_quoted = self._quote_identifier(rule.target_schema, db_type)
            target_table_quoted = self._quote_identifier(rule.target_table, db_type)

            # Use LIMIT for MySQL, ROWNUM for Oracle
            limit_clause = f"LIMIT {limit}" if db_type.lower() == "mysql" else f"AND ROWNUM <= {limit}"

            query = f"""
            SELECT s.*
            FROM {source_schema_quoted}.{source_table_quoted} s
            WHERE NOT EXISTS (
                SELECT 1
                FROM {target_schema_quoted}.{target_table_quoted} t
                WHERE {join_condition}
            )
            {limit_clause}
            """

            logger.debug(f"[UNMATCHED SOURCE QUERY] Rule: {rule.rule_name}")
            logger.debug(f"[UNMATCHED SOURCE QUERY] SQL:\n{query}")

            cursor = source_conn.cursor()
            cursor.execute(query)

            # Get column names
            columns = [desc[0] for desc in cursor.description]

            # Fetch results
            rows = cursor.fetchall()
            cursor.close()

            unmatched = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                row_dict['rule_id'] = rule.rule_id
                row_dict['rule_name'] = rule.rule_name
                unmatched.append(row_dict)

            logger.debug(f"Found {len(unmatched)} unmatched source records for rule {rule.rule_name}")
            return unmatched

        except Exception as e:
            logger.error(f"Error executing unmatched source query: {e}")
            return []

    def _execute_unmatched_target_query(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule,
        limit: int,
        db_type: str = "mysql"
    ) -> List[Dict[str, Any]]:
        """Execute query to find unmatched target records."""
        try:
            # Build NOT EXISTS query
            join_conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                if rule.transformation:
                    join_conditions.append(f"{rule.transformation} = t.{tgt_col}")
                else:
                    join_conditions.append(f"s.{src_col} = t.{tgt_col}")

            join_condition = " AND ".join(join_conditions)

            # Quote identifiers based on database type
            source_schema_quoted = self._quote_identifier(rule.source_schema, db_type)
            source_table_quoted = self._quote_identifier(rule.source_table, db_type)
            target_schema_quoted = self._quote_identifier(rule.target_schema, db_type)
            target_table_quoted = self._quote_identifier(rule.target_table, db_type)

            # Use LIMIT for MySQL, ROWNUM for Oracle
            limit_clause = f"LIMIT {limit}" if db_type.lower() == "mysql" else f"AND ROWNUM <= {limit}"

            query = f"""
            SELECT t.*
            FROM {target_schema_quoted}.{target_table_quoted} t
            WHERE NOT EXISTS (
                SELECT 1
                FROM {source_schema_quoted}.{source_table_quoted} s
                WHERE {join_condition}
            )
            {limit_clause}
            """

            logger.debug(f"[UNMATCHED TARGET QUERY] Rule: {rule.rule_name}")
            logger.debug(f"[UNMATCHED TARGET QUERY] SQL:\n{query}")

            cursor = target_conn.cursor()
            cursor.execute(query)

            # Get column names
            columns = [desc[0] for desc in cursor.description]

            # Fetch results
            rows = cursor.fetchall()
            cursor.close()

            unmatched = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                row_dict['rule_id'] = rule.rule_id
                row_dict['rule_name'] = rule.rule_name
                unmatched.append(row_dict)

            logger.debug(f"Found {len(unmatched)} unmatched target records for rule {rule.rule_name}")
            return unmatched

        except Exception as e:
            logger.error(f"Error executing unmatched target query: {e}")
            return []

    def _connect_to_database(
        self,
        db_config: DatabaseConnectionInfo
    ) -> Optional[Any]:
        """
        Connect to a database using JayDeBeApi.

        Args:
            db_config: Database connection configuration

        Returns:
            Database connection or None if failed
        """
        try:
            # Build JDBC URL based on database type
            jdbc_url = self._build_jdbc_url(db_config)

            # Get JDBC driver class
            driver_class = self._get_driver_class(db_config.db_type)

            # Get driver JAR path
            driver_jar = self._get_driver_jar(db_config.db_type)

            # Connect using JayDeBeApi
            logger.debug(f"Connecting to {jdbc_url} with driver {driver_class}")

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
            return None

    def _build_jdbc_url(self, db_config: DatabaseConnectionInfo) -> str:
        """Build JDBC URL based on database type."""
        db_type = db_config.db_type.lower()

        if db_type == "oracle":
            if db_config.service_name:
                return f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}/{db_config.service_name}"
            else:
                return f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}:{db_config.database}"

        elif db_type == "sqlserver" or db_type == "mssql":
            return f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database}"

        elif db_type == "postgresql" or db_type == "postgres":
            return f"jdbc:postgresql://{db_config.host}:{db_config.port}/{db_config.database}"

        elif db_type == "mysql":
            # Add connection timeout and other parameters for MySQL
            # Increased timeouts for complex reconciliation queries that may take longer
            # connectTimeout: time to establish connection (60s)
            # socketTimeout: time to wait for data from server (120s for complex joins)
            return f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}?connectTimeout=60000&socketTimeout=120000&autoReconnect=true"

        else:
            raise ValueError(f"Unsupported database type: {db_config.db_type}")

    def _get_driver_class(self, db_type: str) -> str:
        """Get JDBC driver class name for database type."""
        db_type = db_type.lower()

        drivers = {
            "oracle": "oracle.jdbc.OracleDriver",
            "sqlserver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
            "mssql": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
            "postgresql": "org.postgresql.Driver",
            "postgres": "org.postgresql.Driver",
            "mysql": "com.mysql.cj.jdbc.Driver"
        }

        if db_type not in drivers:
            raise ValueError(f"Unknown database type: {db_type}")

        return drivers[db_type]

    def _get_driver_jar(self, db_type: str) -> str:
        """Get path to JDBC driver JAR file."""
        if not self.jdbc_drivers_path or not self.jdbc_drivers_path.exists():
            raise ValueError(
                f"JDBC drivers path not configured or doesn't exist: {self.jdbc_drivers_path}"
            )

        db_type = db_type.lower()

        # Map database types to JAR file patterns
        jar_patterns = {
            "oracle": "ojdbc*.jar",
            "sqlserver": "mssql-jdbc*.jar",
            "mssql": "mssql-jdbc*.jar",
            "postgresql": "postgresql*.jar",
            "postgres": "postgresql*.jar",
            "mysql": "mysql-connector*.jar"
        }

        if db_type not in jar_patterns:
            raise ValueError(f"Unknown database type: {db_type}")

        # Find the JAR file
        pattern = jar_patterns[db_type]
        jar_files = list(self.jdbc_drivers_path.glob(pattern))

        if not jar_files:
            raise ValueError(
                f"JDBC driver not found for {db_type}. "
                f"Expected pattern: {pattern} in {self.jdbc_drivers_path}"
            )

        # Use the first matching JAR
        return str(jar_files[0])


# Singleton instance
_reconciliation_executor: Optional[ReconciliationExecutor] = None


def get_reconciliation_executor() -> ReconciliationExecutor:
    """Get or create the singleton reconciliation executor instance."""
    global _reconciliation_executor
    if _reconciliation_executor is None:
        _reconciliation_executor = ReconciliationExecutor()
    return _reconciliation_executor
