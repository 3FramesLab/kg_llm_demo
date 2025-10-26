"""
Reconciliation execution service for running reconciliation rules against databases.

This service executes SQL-based reconciliation queries to find matched and unmatched records.
"""

import logging
import time
import json
from datetime import datetime
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
    def _normalize_schema_name(schema_name: str, db_type: str = "sqlserver") -> str:
        """
        Normalize schema name to actual database schema.

        For SQL Server, converts JSON filename schemas to 'dbo' (default schema).

        Args:
            schema_name: Schema name from reconciliation rules (may be JSON filename)
            db_type: Database type

        Returns:
            Normalized schema name
        """
        if db_type.lower() == "sqlserver":
            # If schema looks like a filename (has -, _, or mix of cases), use 'dbo'
            if any(char in schema_name for char in ['-', '_']) or schema_name.islower():
                logger.info(f"Normalizing SQL Server schema '{schema_name}' to 'dbo'")
                return "dbo"
        return schema_name

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

    def _log_sql_query(self, query_type: str, rule_name: str, sql: str, attempt: str = "FIRST"):
        """
        Log SQL query in a formatted way for debugging.

        Args:
            query_type: Type of query (MATCHED, UNMATCHED_SOURCE, UNMATCHED_TARGET, INACTIVE_COUNT)
            rule_name: Name of the rule being executed
            sql: The SQL query to log
            attempt: Attempt number (FIRST, RETRY)
        """
        separator = "=" * 100
        logger.info(f"\n{separator}")
        logger.info(f"[{attempt} ATTEMPT] {query_type} QUERY - Rule: {rule_name}")
        logger.info(f"{separator}")
        logger.info(f"SQL:\n{sql}")
        logger.info(f"{separator}\n")

    def _get_limit_clause(self, limit: int, db_type: str = "mysql", is_where_clause: bool = False) -> str:
        """
        Generate database-specific LIMIT clause.

        Args:
            limit: Number of rows to limit
            db_type: Database type (mysql, oracle, postgresql, sqlserver)
            is_where_clause: If True, returns clause for WHERE context (e.g., "AND ROWNUM <= 100")
                           If False, returns clause for SELECT context (e.g., "LIMIT 100" or "TOP 100")

        Returns:
            Database-specific limit clause
        """
        db_type = db_type.lower()

        if db_type == "mysql":
            return f"LIMIT {limit}"
        elif db_type == "oracle":
            # Oracle uses ROWNUM in WHERE clause
            return f"AND ROWNUM <= {limit}" if is_where_clause else f"WHERE ROWNUM <= {limit}"
        elif db_type == "postgresql":
            return f"LIMIT {limit}"
        elif db_type == "sqlserver":
            # SQL Server uses TOP in SELECT clause
            return f"TOP {limit}"
        else:
            # Default to MySQL style
            return f"LIMIT {limit}"

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
            RuleExecutionResponse with matched and unmatched records, generated SQL, and file path
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

            # Execute all rules and collect SQL queries
            all_matched = []
            all_unmatched_source = []
            all_unmatched_target = []
            generated_sql = []

            for rule in ruleset.rules:
                logger.debug(f"Executing rule: {rule.rule_name}")

                # Execute matched records query
                if include_matched:
                    matched, matched_sql = self._execute_matched_query(
                        source_conn, target_conn, rule, limit, source_db_config.db_type
                    )
                    all_matched.extend(matched)
                    if matched_sql:
                        generated_sql.append(matched_sql)

                # Execute unmatched queries
                if include_unmatched:
                    unmatched_src, unmatched_src_sql = self._execute_unmatched_source_query(
                        source_conn, target_conn, rule, limit, source_db_config.db_type
                    )
                    all_unmatched_source.extend(unmatched_src)
                    if unmatched_src_sql:
                        generated_sql.append(unmatched_src_sql)

                    unmatched_tgt, unmatched_tgt_sql = self._execute_unmatched_target_query(
                        source_conn, target_conn, rule, limit, source_db_config.db_type
                    )
                    all_unmatched_target.extend(unmatched_tgt)
                    if unmatched_tgt_sql:
                        generated_sql.append(unmatched_tgt_sql)

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
                "inactive_count": inactive_count,
                "generated_sql": generated_sql
            }

            # Store results to file
            result_file_path = None
            try:
                result_file_path = self._store_results_to_file(
                    ruleset_id=ruleset_id,
                    response_data=response_data,
                    all_matched=all_matched,
                    all_unmatched_source=all_unmatched_source,
                    all_unmatched_target=all_unmatched_target
                )
                logger.info(f"Results stored to file: {result_file_path}")
                response_data["result_file_path"] = result_file_path
            except Exception as e:
                logger.warning(f"Failed to store results to file: {e}")
                # Continue without file storage

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
        If the is_active column doesn't exist, returns 0.

        Args:
            source_conn: Database connection
            ruleset: The reconciliation ruleset
            db_type: Database type (mysql, oracle, etc.)

        Returns:
            Count of inactive records (0 if is_active column doesn't exist)
        """
        try:
            if not ruleset.rules:
                logger.warning("No rules in ruleset, cannot count inactive records")
                return 0

            # Get the first rule to determine source table
            first_rule = ruleset.rules[0]
            source_schema = self._normalize_schema_name(first_rule.source_schema, db_type)
            source_table = first_rule.source_table

            # Quote identifiers based on database type
            schema_quoted = self._quote_identifier(source_schema, db_type)
            table_quoted = self._quote_identifier(source_table, db_type)
            is_active_quoted = self._quote_identifier("is_active", db_type)

            # First, check if the is_active column exists
            cursor = source_conn.cursor()
            column_exists = False

            try:
                # Try to check if column exists (database-specific approach)
                if db_type == "sqlserver":
                    # SQL Server - check INFORMATION_SCHEMA
                    check_query = f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{source_table}'
                    AND COLUMN_NAME = 'is_active'
                    """
                    if source_schema:
                        check_query = f"""
                        SELECT COUNT(*)
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = '{source_schema}'
                        AND TABLE_NAME = '{source_table}'
                        AND COLUMN_NAME = 'is_active'
                        """
                elif db_type == "oracle":
                    # Oracle - check ALL_TAB_COLUMNS
                    check_query = f"""
                    SELECT COUNT(*)
                    FROM ALL_TAB_COLUMNS
                    WHERE TABLE_NAME = UPPER('{source_table}')
                    AND COLUMN_NAME = UPPER('is_active')
                    """
                    if source_schema:
                        check_query += f" AND OWNER = UPPER('{source_schema}')"
                else:
                    # MySQL/PostgreSQL - check INFORMATION_SCHEMA
                    check_query = f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{source_table}'
                    AND COLUMN_NAME = 'is_active'
                    """
                    if source_schema:
                        check_query += f" AND TABLE_SCHEMA = '{source_schema}'"

                cursor.execute(check_query)
                result = cursor.fetchone()
                column_exists = result and result[0] > 0

            except Exception as check_error:
                # If checking fails, try to query the column directly
                logger.debug(f"Column existence check failed, trying direct query: {check_error}")
                try:
                    test_query = f"SELECT {is_active_quoted} FROM {schema_quoted}.{table_quoted} WHERE 1=0"
                    cursor.execute(test_query)
                    column_exists = True
                except:
                    try:
                        test_query = f"SELECT {is_active_quoted} FROM {table_quoted} WHERE 1=0"
                        cursor.execute(test_query)
                        column_exists = True
                    except:
                        column_exists = False

            # If column doesn't exist, return 0
            if not column_exists:
                logger.info(f"Column 'is_active' does not exist in {source_schema}.{source_table}. Skipping inactive count.")
                cursor.close()
                return 0

            # Column exists, proceed with counting inactive records
            query = f"""
            SELECT COUNT(*) as inactive_count
            FROM {schema_quoted}.{table_quoted}
            WHERE {is_active_quoted} = 0 OR {is_active_quoted} IS NULL
            """

            self._log_sql_query("INACTIVE_COUNT", f"{source_schema}.{source_table}", query, "FIRST")

            # Execute query
            try:
                cursor.execute(query)
            except Exception as schema_error:
                # If schema prefix fails, try without schema (defaults to dbo in SQL Server)
                logger.warning(f"Query with schema prefix failed: {schema_error}. Trying without schema prefix...")
                query_no_schema = f"""
                SELECT COUNT(*) as inactive_count
                FROM {table_quoted}
                WHERE {is_active_quoted} = 0 OR {is_active_quoted} IS NULL
                """
                self._log_sql_query("INACTIVE_COUNT", f"{source_schema}.{source_table}", query_no_schema, "RETRY")
                cursor.execute(query_no_schema)
                query = query_no_schema  # Use the no-schema version for logging

            result = cursor.fetchone()
            cursor.close()

            inactive_count = result[0] if result else 0
            logger.info(f"Found {inactive_count} inactive records in {source_schema}.{source_table}")

            return inactive_count

        except Exception as e:
            logger.warning(f"Failed to count inactive records: {e}. Returning 0.")
            # Return 0 if we can't count (don't fail the entire execution)
            return 0

    def _execute_matched_query(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule,
        limit: int,
        db_type: str = "mysql"
    ) -> Tuple[List[MatchedRecord], Optional[Dict[str, Any]]]:
        """Execute query to find matched records. Returns (records, sql_info)."""
        try:
            # Build JOIN query
            join_conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                if rule.transformation:
                    join_conditions.append(f"{rule.transformation} = t.{tgt_col}")
                else:
                    join_conditions.append(f"s.{src_col} = t.{tgt_col}")

            join_condition = " AND ".join(join_conditions)

            # Normalize and quote identifiers based on database type
            source_schema = self._normalize_schema_name(rule.source_schema, db_type)
            target_schema = self._normalize_schema_name(rule.target_schema, db_type)

            source_schema_quoted = self._quote_identifier(source_schema, db_type)
            source_table_quoted = self._quote_identifier(rule.source_table, db_type)
            target_schema_quoted = self._quote_identifier(target_schema, db_type)
            target_table_quoted = self._quote_identifier(rule.target_table, db_type)

            # Get database-specific limit clause
            limit_clause = self._get_limit_clause(limit, db_type, is_where_clause=False)

            # For SQL Server, TOP goes in SELECT clause
            if db_type.lower() == "sqlserver":
                query = f"""
            SELECT {limit_clause} s.*, t.*
            FROM {source_schema_quoted}.{source_table_quoted} s
            INNER JOIN {target_schema_quoted}.{target_table_quoted} t
                ON {join_condition}
            """
            else:
                # For MySQL, Oracle, PostgreSQL, LIMIT goes at the end
                query = f"""
            SELECT s.*, t.*
            FROM {source_schema_quoted}.{source_table_quoted} s
            INNER JOIN {target_schema_quoted}.{target_table_quoted} t
                ON {join_condition}
            {limit_clause}
            """

            self._log_sql_query("MATCHED", rule.rule_name, query, "FIRST")

            cursor = source_conn.cursor()
            try:
                cursor.execute(query)
            except Exception as schema_error:
                # If schema prefix fails, try without schema (defaults to dbo in SQL Server)
                logger.warning(f"Query with schema prefix failed: {schema_error}. Trying without schema prefix...")
                query_no_schema = f"""
                SELECT s.*, t.*
                FROM {source_table_quoted} s
                INNER JOIN {target_table_quoted} t
                    ON {join_condition}
                {limit_clause}
                """
                self._log_sql_query("MATCHED", rule.rule_name, query_no_schema, "RETRY")
                cursor.execute(query_no_schema)
                query = query_no_schema  # Use the no-schema version for response

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

            # Prepare SQL info for response
            sql_info = {
                "rule_id": rule.rule_id,
                "rule_name": rule.rule_name,
                "query_type": "matched",
                "source_sql": query,
                "target_sql": None,
                "description": f"Find matched records between {rule.source_table} and {rule.target_table}"
            }

            return matched_records, sql_info

        except Exception as e:
            logger.error(f"Error executing matched query: {e}")
            return [], None

    def _execute_unmatched_source_query(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule,
        limit: int,
        db_type: str = "mysql"
    ) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Execute query to find unmatched source records. Returns (records, sql_info)."""
        try:
            # Build NOT EXISTS query
            join_conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                if rule.transformation:
                    join_conditions.append(f"{rule.transformation} = t.{tgt_col}")
                else:
                    join_conditions.append(f"s.{src_col} = t.{tgt_col}")

            join_condition = " AND ".join(join_conditions)

            # Normalize and quote identifiers based on database type
            source_schema = self._normalize_schema_name(rule.source_schema, db_type)
            target_schema = self._normalize_schema_name(rule.target_schema, db_type)

            source_schema_quoted = self._quote_identifier(source_schema, db_type)
            source_table_quoted = self._quote_identifier(rule.source_table, db_type)
            target_schema_quoted = self._quote_identifier(target_schema, db_type)
            target_table_quoted = self._quote_identifier(rule.target_table, db_type)

            # Get database-specific limit clause
            limit_clause = self._get_limit_clause(limit, db_type, is_where_clause=False)

            # For SQL Server, TOP goes in SELECT clause
            if db_type.lower() == "sqlserver":
                query = f"""
            SELECT {limit_clause} s.*
            FROM {source_schema_quoted}.{source_table_quoted} s
            WHERE NOT EXISTS (
                SELECT 1
                FROM {target_schema_quoted}.{target_table_quoted} t
                WHERE {join_condition}
            )
            """
            else:
                # For MySQL, Oracle, PostgreSQL, LIMIT goes at the end
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

            self._log_sql_query("UNMATCHED_SOURCE", rule.rule_name, query, "FIRST")

            cursor = source_conn.cursor()
            try:
                cursor.execute(query)
            except Exception as schema_error:
                # If schema prefix fails, try without schema (defaults to dbo in SQL Server)
                logger.warning(f"Query with schema prefix failed: {schema_error}. Trying without schema prefix...")
                query_no_schema = f"""
                SELECT s.*
                FROM {source_table_quoted} s
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM {target_table_quoted} t
                    WHERE {join_condition}
                )
                {limit_clause}
                """
                self._log_sql_query("UNMATCHED_SOURCE", rule.rule_name, query_no_schema, "RETRY")
                cursor.execute(query_no_schema)
                query = query_no_schema  # Use the no-schema version for response

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

            # Prepare SQL info for response
            sql_info = {
                "rule_id": rule.rule_id,
                "rule_name": rule.rule_name,
                "query_type": "unmatched_source",
                "source_sql": query,
                "target_sql": None,
                "description": f"Find records in {rule.source_table} not found in {rule.target_table}"
            }

            return unmatched, sql_info

        except Exception as e:
            logger.error(f"Error executing unmatched source query: {e}")
            return [], None

    def _execute_unmatched_target_query(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule,
        limit: int,
        db_type: str = "mysql"
    ) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Execute query to find unmatched target records. Returns (records, sql_info)."""
        try:
            # Build NOT EXISTS query
            join_conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                if rule.transformation:
                    join_conditions.append(f"{rule.transformation} = t.{tgt_col}")
                else:
                    join_conditions.append(f"s.{src_col} = t.{tgt_col}")

            join_condition = " AND ".join(join_conditions)

            # Normalize and quote identifiers based on database type
            source_schema = self._normalize_schema_name(rule.source_schema, db_type)
            target_schema = self._normalize_schema_name(rule.target_schema, db_type)

            source_schema_quoted = self._quote_identifier(source_schema, db_type)
            source_table_quoted = self._quote_identifier(rule.source_table, db_type)
            target_schema_quoted = self._quote_identifier(target_schema, db_type)
            target_table_quoted = self._quote_identifier(rule.target_table, db_type)

            # Get database-specific limit clause
            limit_clause = self._get_limit_clause(limit, db_type, is_where_clause=False)

            # For SQL Server, TOP goes in SELECT clause
            if db_type.lower() == "sqlserver":
                query = f"""
            SELECT {limit_clause} t.*
            FROM {target_schema_quoted}.{target_table_quoted} t
            WHERE NOT EXISTS (
                SELECT 1
                FROM {source_schema_quoted}.{source_table_quoted} s
                WHERE {join_condition}
            )
            """
            else:
                # For MySQL, Oracle, PostgreSQL, LIMIT goes at the end
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

            self._log_sql_query("UNMATCHED_TARGET", rule.rule_name, query, "FIRST")

            cursor = target_conn.cursor()
            try:
                cursor.execute(query)
            except Exception as schema_error:
                # If schema prefix fails, try without schema (defaults to dbo in SQL Server)
                logger.warning(f"Query with schema prefix failed: {schema_error}. Trying without schema prefix...")
                query_no_schema = f"""
                SELECT t.*
                FROM {target_table_quoted} t
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM {source_table_quoted} s
                    WHERE {join_condition}
                )
                {limit_clause}
                """
                self._log_sql_query("UNMATCHED_TARGET", rule.rule_name, query_no_schema, "RETRY")
                cursor.execute(query_no_schema)
                query = query_no_schema  # Use the no-schema version for response

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

            # Prepare SQL info for response
            sql_info = {
                "rule_id": rule.rule_id,
                "rule_name": rule.rule_name,
                "query_type": "unmatched_target",
                "source_sql": None,
                "target_sql": query,
                "description": f"Find records in {rule.target_table} not found in {rule.source_table}"
            }

            return unmatched, sql_info

        except Exception as e:
            logger.error(f"Error executing unmatched target query: {e}")
            return [], None

    def _store_results_to_file(
        self,
        ruleset_id: str,
        response_data: Dict[str, Any],
        all_matched: List[MatchedRecord],
        all_unmatched_source: List[Dict[str, Any]],
        all_unmatched_target: List[Dict[str, Any]]
    ) -> str:
        """
        Store reconciliation results to a JSON file.

        Args:
            ruleset_id: ID of the ruleset
            response_data: Response data dictionary
            all_matched: List of matched records
            all_unmatched_source: List of unmatched source records
            all_unmatched_target: List of unmatched target records

        Returns:
            Path to the saved file
        """
        # Create results directory if it doesn't exist
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reconciliation_result_{ruleset_id}_{timestamp}.json"
        file_path = results_dir / filename

        # Prepare data for JSON serialization
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

        # Prepare complete result document
        result_document = {
            "ruleset_id": ruleset_id,
            "execution_timestamp": datetime.now().isoformat(),
            "matched_count": response_data["matched_count"],
            "unmatched_source_count": response_data["unmatched_source_count"],
            "unmatched_target_count": response_data["unmatched_target_count"],
            "execution_time_ms": response_data["execution_time_ms"],
            "inactive_count": response_data.get("inactive_count", 0),
            "matched_records": matched_dicts,
            "unmatched_source": all_unmatched_source,
            "unmatched_target": all_unmatched_target,
            "generated_sql": response_data.get("generated_sql", [])
        }

        # Write to file
        with open(file_path, 'w') as f:
            json.dump(result_document, f, indent=2, default=str)

        logger.info(f"Results stored to file: {file_path}")
        return str(file_path)

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
            return f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database};encrypt=true;trustServerCertificate=true"

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
