"""
Natural Language Query Executor

Executes NL-generated queries and returns results with statistics.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from kg_builder.services.nl_query_parser import QueryIntent
from kg_builder.services.nl_sql_generator import NLSQLGenerator

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result from executing a query."""
    definition: str
    query_type: str
    operation: Optional[str]
    sql: str
    record_count: int
    records: List[Dict[str, Any]]
    join_columns: Optional[List[Tuple[str, str]]]
    confidence: float
    execution_time_ms: float
    error: Optional[str] = None
    source_table: Optional[str] = None
    target_table: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert join_columns tuples to lists for JSON serialization
        if data.get("join_columns"):
            data["join_columns"] = [list(jc) for jc in data["join_columns"]]
        return data


class NLQueryExecutor:
    """Execute NL-generated queries and return results."""

    def __init__(self, db_type: str = "mysql"):
        """
        Initialize executor.

        Args:
            db_type: Database type (mysql, postgresql, sqlserver, oracle)
        """
        self.db_type = db_type.lower()
        self.generator = NLSQLGenerator(db_type)

    def execute(
        self,
        intent: QueryIntent,
        connection: Any,
        limit: int = 1000
    ) -> QueryResult:
        """
        Execute query and return results.

        Args:
            intent: QueryIntent object
            connection: Database connection
            limit: Maximum number of records to return

        Returns:
            QueryResult: Query execution result
        """
        import time

        start_time = time.time()
        result = QueryResult(
            definition=intent.definition,
            query_type=intent.query_type,
            operation=intent.operation,
            sql="",
            record_count=0,
            records=[],
            join_columns=intent.join_columns,
            confidence=intent.confidence,
            execution_time_ms=0.0,
            source_table=intent.source_table,
            target_table=intent.target_table
        )

        try:
            # Generate SQL
            sql = self.generator.generate(intent)
            result.sql = sql

            # Add LIMIT clause
            sql_with_limit = self._add_limit_clause(sql, limit)
            logger.debug(f"Added limit clause (db_type={self.db_type}, limit={limit})")

            # Log to both logger and console to ensure visibility
            log_lines = [
                "="*80,
                f"📝 Query Definition: {intent.definition}",
                f"🔍 Query Type: {intent.query_type}",
                f"⚙️  Operation: {intent.operation}"
            ]
            if intent.join_columns:
                log_lines.append(f"🔗 Join Columns: {intent.join_columns}")
            log_lines.extend([
                "-"*80,
                "🔹 SQL TO BE EXECUTED:",
                f"\n{sql_with_limit}\n",
                "="*80
            ])

            # Log to logger
            for line in log_lines:
                logger.info(line)

            # Also print to console to ensure it's visible
            print("\n" + "\n".join(log_lines))

            # Execute query
            exec_msg = "⏳ Executing SQL query..."
            logger.info(exec_msg)
            print(exec_msg)

            cursor = connection.cursor()
            cursor.execute(sql_with_limit)

            success_msg = "✅ SQL executed successfully"
            logger.info(success_msg)
            print(success_msg)

            # Fetch results
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Convert rows to dictionaries
            records = []
            for row in rows:
                record = {}
                for i, col in enumerate(columns):
                    record[col] = row[i]
                records.append(record)

            result.records = records
            result.record_count = len(records)

            result_msg = f"📊 Query Result: Found {result.record_count} records in {(time.time() - start_time)*1000:.2f}ms"
            logger.info(result_msg)
            print(result_msg)

        except Exception as e:
            error_msg = f"Error executing query: {str(e)}"
            logger.error("="*80)
            logger.error(f"❌ QUERY EXECUTION FAILED")
            logger.error(f"📝 Query: {intent.definition}")
            if result.sql:
                logger.error(f"🔹 SQL that failed:")
                logger.error(f"\n{result.sql}\n")
            logger.error(f"⚠️  Error: {error_msg}")
            logger.error("="*80)
            result.error = error_msg

        finally:
            result.execution_time_ms = (time.time() - start_time) * 1000

        return result

    def execute_batch(
        self,
        intents: List[QueryIntent],
        connection: Any,
        limit: int = 1000
    ) -> List[QueryResult]:
        """
        Execute multiple queries.

        Args:
            intents: List of QueryIntent objects
            connection: Database connection
            limit: Maximum number of records per query

        Returns:
            List[QueryResult]: List of query results
        """
        batch_header = f"\n{'='*80}\n📦 BATCH EXECUTION: Starting {len(intents)} queries\n{'='*80}\n"
        logger.info(batch_header)
        print(batch_header)  # Ensure console visibility

        results = []

        for idx, intent in enumerate(intents, 1):
            query_header = f"\n{'#'*80}\n🔢 Query {idx} of {len(intents)}\n{'#'*80}"
            logger.info(query_header)
            print(query_header)  # Ensure console visibility
            try:
                result = self.execute(intent, connection, limit)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing batch query: {e}")
                results.append(QueryResult(
                    definition=intent.definition,
                    query_type=intent.query_type,
                    operation=intent.operation,
                    sql="",
                    record_count=0,
                    records=[],
                    join_columns=intent.join_columns,
                    confidence=intent.confidence,
                    execution_time_ms=0.0,
                    error=str(e)
                ))

        # Log batch summary
        successful = len([r for r in results if r.error is None])
        failed = len([r for r in results if r.error is not None])
        total_records = sum(r.record_count for r in results)

        summary = (
            f"\n{'='*80}\n"
            f"📦 BATCH EXECUTION SUMMARY\n"
            f"{'='*80}\n"
            f"✅ Successful: {successful}/{len(intents)}\n"
            f"❌ Failed: {failed}/{len(intents)}\n"
            f"📊 Total Records: {total_records}\n"
            f"{'='*80}\n"
        )
        logger.info(summary)
        print(summary)  # Ensure console visibility

        return results

    def _add_limit_clause(self, sql: str, limit: int) -> str:
        """
        Add LIMIT clause to SQL based on database type.

        Args:
            sql: SQL query
            limit: Limit value

        Returns:
            str: SQL with LIMIT clause
        """
        if self.db_type == "sqlserver":
            # SQL Server uses TOP
            # Need to handle: SELECT DISTINCT TOP should be the order
            sql_upper = sql.upper()

            if "SELECT DISTINCT" in sql_upper:
                # Insert TOP after DISTINCT
                # Find the position of DISTINCT
                distinct_pos = sql_upper.find("SELECT DISTINCT")
                if distinct_pos != -1:
                    # Find the end of "SELECT DISTINCT"
                    insert_pos = sql.upper().find("DISTINCT") + len("DISTINCT")
                    sql = sql[:insert_pos] + f" TOP {limit}" + sql[insert_pos:]
            elif "SELECT" in sql_upper:
                # Just add TOP after SELECT
                select_pos = sql_upper.find("SELECT")
                insert_pos = select_pos + len("SELECT")
                sql = sql[:insert_pos] + f" TOP {limit}" + sql[insert_pos:]

            return sql
        else:
            # MySQL, PostgreSQL, Oracle use LIMIT
            return f"{sql}\nLIMIT {limit}"

    def get_statistics(self, results: List[QueryResult]) -> Dict[str, Any]:
        """
        Get statistics from query results.

        Args:
            results: List of QueryResult objects

        Returns:
            Dict: Statistics
        """
        total_records = sum(r.record_count for r in results)
        successful = len([r for r in results if r.error is None])
        failed = len([r for r in results if r.error is not None])
        total_time_ms = sum(r.execution_time_ms for r in results)
        avg_confidence = sum(r.confidence for r in results) / len(results) if results else 0

        return {
            "total_queries": len(results),
            "successful": successful,
            "failed": failed,
            "total_records": total_records,
            "total_execution_time_ms": total_time_ms,
            "average_confidence": avg_confidence,
            "records_by_query": [
                {
                    "definition": r.definition,
                    "record_count": r.record_count,
                    "execution_time_ms": r.execution_time_ms
                }
                for r in results
            ]
        }


def get_nl_query_executor(db_type: str = "mysql") -> NLQueryExecutor:
    """Get or create NL query executor instance."""
    return NLQueryExecutor(db_type)

