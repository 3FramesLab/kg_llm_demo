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

    def execute_ruleset(
        self,
        ruleset_id: str,
        source_db_config: DatabaseConnectionInfo,
        target_db_config: DatabaseConnectionInfo,
        limit: int = 100,
        include_matched: bool = True,
        include_unmatched: bool = True
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
                        source_conn, target_conn, rule, limit
                    )
                    all_matched.extend(matched)

                # Execute unmatched queries
                if include_unmatched:
                    unmatched_src = self._execute_unmatched_source_query(
                        source_conn, target_conn, rule, limit
                    )
                    all_unmatched_source.extend(unmatched_src)

                    unmatched_tgt = self._execute_unmatched_target_query(
                        source_conn, target_conn, rule, limit
                    )
                    all_unmatched_target.extend(unmatched_tgt)

            elapsed_ms = (time.time() - start_time) * 1000

            logger.info(
                f"Execution complete: {len(all_matched)} matched, "
                f"{len(all_unmatched_source)} unmatched source, "
                f"{len(all_unmatched_target)} unmatched target"
            )

            return RuleExecutionResponse(
                success=True,
                matched_count=len(all_matched),
                unmatched_source_count=len(all_unmatched_source),
                unmatched_target_count=len(all_unmatched_target),
                matched_records=all_matched[:limit] if limit else all_matched,
                unmatched_source=all_unmatched_source[:limit] if limit else all_unmatched_source,
                unmatched_target=all_unmatched_target[:limit] if limit else all_unmatched_target,
                execution_time_ms=elapsed_ms
            )

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

    def _execute_matched_query(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule,
        limit: int
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

            # For matched records, we need to join on the same connection
            # Assuming both schemas are on the same database for now
            query = f"""
            SELECT s.*, t.*
            FROM {rule.source_schema}.{rule.source_table} s
            INNER JOIN {rule.target_schema}.{rule.target_table} t
                ON {join_condition}
            WHERE ROWNUM <= {limit}
            """

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
        limit: int
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

            query = f"""
            SELECT s.*
            FROM {rule.source_schema}.{rule.source_table} s
            WHERE NOT EXISTS (
                SELECT 1
                FROM {rule.target_schema}.{rule.target_table} t
                WHERE {join_condition}
            )
            AND ROWNUM <= {limit}
            """

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
        limit: int
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

            query = f"""
            SELECT t.*
            FROM {rule.target_schema}.{rule.target_table} t
            WHERE NOT EXISTS (
                SELECT 1
                FROM {rule.source_schema}.{rule.source_table} s
                WHERE {join_condition}
            )
            AND ROWNUM <= {limit}
            """

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
            return f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}"

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
