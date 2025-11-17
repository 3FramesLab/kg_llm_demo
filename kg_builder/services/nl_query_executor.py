"""
Natural Language Query Executor

Executes NL-generated queries and returns results with statistics.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass, asdict

from kg_builder.services.nl_query_parser import QueryIntent
from kg_builder.services.nl_sql_generator import NLSQLGenerator

if TYPE_CHECKING:
    from kg_builder.models import KnowledgeGraph

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

    def __init__(self, db_type: str = "mysql", kg: Optional["KnowledgeGraph"] = None, use_llm: bool = True, excluded_fields: Optional[List[str]] = None):
        """
        Initialize executor.

        Args:
            db_type: Database type (mysql, postgresql, sqlserver, oracle)
            kg: Optional Knowledge Graph for join column resolution
            use_llm: Whether to use LLM for SQL generation (default: True for LLM-only)
            excluded_fields: List of field names to avoid in joins (optional)
        """
        self.db_type = db_type.lower()
        self.kg = kg
        self.use_llm = use_llm
        self.excluded_fields = set(excluded_fields) if excluded_fields else None
        self.generator = NLSQLGenerator(db_type, kg=kg, use_llm=use_llm)  # Pass use_llm to generator

        # Store reference to query parser for excluded fields configuration
        self.query_parser = None

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

        logger.info("="*120)
        logger.info(f"🤖 NL QUERY EXECUTOR: STARTING QUERY EXECUTION")
        logger.info(f"   Intent Definition: '{intent.definition}'")
        logger.info(f"   Query Type: {intent.query_type}")
        logger.info(f"   Operation: {intent.operation}")
        logger.info(f"   Source Table: {intent.source_table}")
        logger.info(f"   Target Table: {intent.target_table}")
        logger.info(f"   Join Columns: {intent.join_columns}")
        logger.info(f"   Filters: {intent.filters}")
        logger.info(f"   Confidence: {intent.confidence}")
        logger.info(f"   Limit: {limit}")
        logger.info(f"   Connection Type: {type(connection).__name__}")
        logger.info(f"   Use LLM: {self.use_llm}")
        logger.info(f"   DB Type: {self.db_type}")
        if self.kg:
            logger.info(f"   KG Name: {self.kg.name}")
            logger.info(f"   KG Nodes: {len(self.kg.nodes)}")
        logger.info("="*120)

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
            # STEP 1: Generate SQL (enhancement is already applied in the generator)
            logger.info(f"🔧 STEP 1: GENERATING SQL FROM INTENT")
            sql_gen_start = time.time()

            logger.info(f"   Generator Type: {type(self.generator).__name__}")
            logger.info(f"   Generating SQL for intent...")
            logger.info(f"   Intent Source Table: {intent.source_table}")
            logger.info(f"   Intent Target Table: {intent.target_table}")
            logger.info(f"   Intent Operation: {intent.operation}")

            sql = self.generator.generate(intent)
            result.sql = sql
            sql_gen_time = (time.time() - sql_gen_start) * 1000

            logger.info(f"✅ SQL generated in {sql_gen_time:.2f}ms")
            logger.info(f"   Generated SQL Length: {len(sql) if sql else 0} characters")
            if sql:
                # Log first 300 characters for debugging
                sql_preview = sql[:300] + "..." if len(sql) > 300 else sql
                logger.info(f"   Generated SQL Preview: {sql_preview}")
            else:
                logger.warning(f"   ⚠️ Generated SQL is empty!")

            # STEP 2: Add LIMIT clause
            logger.info(f"📏 STEP 2: ADDING LIMIT CLAUSE")
            limit_start = time.time()

            logger.info(f"   Original SQL length: {len(sql) if sql else 0}")
            logger.info(f"   Adding limit: {limit}")
            logger.info(f"   Database type: {self.db_type}")

            sql_with_limit = self._add_limit_clause(sql, limit)
            limit_time = (time.time() - limit_start) * 1000

            logger.info(f"✅ Limit clause added in {limit_time:.2f}ms")
            logger.info(f"   Final SQL length: {len(sql_with_limit) if sql_with_limit else 0}")

            # STEP 3: Log final SQL for execution
            logger.info("="*120)
            logger.info(f"📝 FINAL SQL TO BE EXECUTED:")
            logger.info(f"   Query Definition: {intent.definition}")
            logger.info(f"   Query Type: {intent.query_type}")
            logger.info(f"   Operation: {intent.operation}")
            if intent.join_columns:
                logger.info(f"   Join Columns: {intent.join_columns}")
            if intent.filters:
                logger.info(f"   Filters: {intent.filters}")
            logger.info(f"   Confidence: {intent.confidence}")
            logger.info("-"*120)
            logger.info(f"🔹 COMPLETE SQL QUERY:")
            logger.info(f"{sql_with_limit}")
            logger.info("="*120)

            # STEP 4: Execute SQL query
            logger.info(f"💾 STEP 4: EXECUTING SQL QUERY")
            db_exec_start = time.time()

            logger.info(f"   Connection Type: {type(connection).__name__}")
            logger.info(f"   SQL Length: {len(sql_with_limit)} characters")
            logger.info(f"   Expected Limit: {limit} records")
            logger.info(f"   Starting database execution...")

            cursor = connection.cursor()

            # Execute the query
            logger.info(f"   Executing SQL query...")
            cursor.execute(sql_with_limit)
            db_exec_time = (time.time() - db_exec_start) * 1000

            logger.info(f"✅ SQL executed successfully in {db_exec_time:.2f}ms")

            # STEP 5: Fetch and process results
            logger.info(f"📊 STEP 5: FETCHING AND PROCESSING RESULTS")
            fetch_start = time.time()

            logger.info(f"   Fetching all rows...")
            rows = cursor.fetchall()

            logger.info(f"   Processing column descriptions...")
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            fetch_time = (time.time() - fetch_start) * 1000
            logger.info(f"✅ Results fetched in {fetch_time:.2f}ms")
            logger.info(f"   Raw Rows Count: {len(rows)}")
            logger.info(f"   Columns Count: {len(columns)}")
            logger.info(f"   Column Names: {columns}")

            # STEP 6: Convert rows to dictionaries with Java type conversion
            logger.info(f"🔄 STEP 6: CONVERTING ROWS TO DICTIONARIES")
            convert_start = time.time()

            from kg_builder.utils.java_type_converter import convert_jdbc_results
            records = convert_jdbc_results(rows, columns)

            # Log first few records for debugging
            for i, record in enumerate(records[:3]):
                logger.info(f"   Record {i+1}: {record}")
            if len(records) > 3:
                logger.info(f"   ... and {len(records)-3} more records")

            convert_time = (time.time() - convert_start) * 1000
            logger.info(f"✅ Rows converted in {convert_time:.2f}ms")
            logger.info(f"   Final Records Count: {len(records)}")

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

    def execute_query(
        self,
        query: str,
        kg_name: str,
        select_schema: str,
        limit_records: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a natural language query using the full NL processing pipeline.

        This method provides a high-level interface that:
        1. Loads the Knowledge Graph
        2. Parses the NL query into intent
        3. Generates SQL from intent
        4. Executes the SQL and returns results

        Args:
            query: Natural language query definition
            kg_name: Name of the Knowledge Graph to use
            select_schema: Database schema to query
            limit_records: Maximum number of records to return
            **kwargs: Additional parameters

        Returns:
            Dict containing execution results with keys:
            - generated_sql: The generated SQL query
            - number_of_records: Number of records returned
            - execution_status: 'success' or 'failed'
            - execution_time_ms: Execution time in milliseconds
            - confidence_score: Confidence score of the query
            - data: List of result records
            - error_message: Error message if failed
        """
        import time
        from kg_builder.services.graphiti_backend import GraphitiBackend
        from kg_builder.services.nl_query_parser import NLQueryParser
        from kg_builder.services.landing_db_connector import get_db_connection

        start_time = time.time()

        logger.info(f"🚀 Starting NL query execution")
        logger.info(f"   Query: {query}")
        logger.info(f"   KG Name: {kg_name}")
        logger.info(f"   Schema: {select_schema}")
        logger.info(f"   Limit: {limit_records}")

        try:
            # Step 1: Load Knowledge Graph
            logger.info(f"📊 Loading Knowledge Graph: {kg_name}")
            backend = GraphitiBackend()
            kg = backend.get_graph(kg_name)

            if not kg:
                raise ValueError(f"Knowledge Graph '{kg_name}' not found")

            logger.info(f"✅ KG loaded: {len(kg.nodes)} nodes, {len(kg.relationships)} relationships")

            # Step 2: Extract excluded fields from KG metadata
            excluded_fields = None
            if hasattr(kg, 'metadata') and kg.metadata:
                excluded_fields = kg.metadata.get('excluded_fields', [])
                if excluded_fields:
                    logger.info(f"📋 Using {len(excluded_fields)} excluded fields from KG")
                    logger.debug(f"Excluded fields: {excluded_fields}")

            # Step 3: Parse NL query into intent with excluded fields awareness
            logger.info(f"🔍 Parsing NL query into intent")
            parser = NLQueryParser(kg=kg, excluded_fields=excluded_fields)
            intent = parser.parse(query, use_llm=True)

            logger.info(f"✅ Intent parsed: {intent.query_type}, confidence: {intent.confidence:.2f}")

            # Step 4: Generate SQL with excluded fields awareness
            logger.info(f"🔧 Generating SQL from intent")
            if hasattr(self, 'sql_generator') and self.sql_generator:
                # Use the assigned SQL generator (e.g., enhanced generator)
                sql = self.sql_generator.generate(intent)
            else:
                # Use the default generator
                sql = self.generator.generate(intent)

            logger.info(f"✅ SQL generated: {len(sql)} characters")
            logger.debug(f"Generated SQL: {sql}")

            # Step 5: Execute SQL
            logger.info(f"⚡ Executing SQL query")
            with get_db_connection() as connection:
                result = self.execute(intent, connection, limit=limit_records)

            execution_time_ms = (time.time() - start_time) * 1000

            logger.info(f"✅ Query execution completed in {execution_time_ms:.2f}ms")
            logger.info(f"   Records returned: {result.record_count}")

            # Format response
            return {
                'generated_sql': result.sql,
                'number_of_records': result.record_count,
                'execution_status': 'success' if not result.error else 'failed',
                'execution_time_ms': execution_time_ms,
                'confidence_score': result.confidence,
                'data': result.records,
                'error_message': result.error,
                'join_columns': result.join_columns,
                'source_table': result.source_table,
                'target_table': result.target_table
            }

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = str(e)

            logger.error(f"❌ Query execution failed: {error_msg}")
            logger.error(f"   Execution time: {execution_time_ms:.2f}ms")

            return {
                'generated_sql': None,
                'number_of_records': 0,
                'execution_status': 'failed',
                'execution_time_ms': execution_time_ms,
                'confidence_score': 0.0,
                'data': [],
                'error_message': error_msg,
                'join_columns': None,
                'source_table': None,
                'target_table': None
            }

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

    def execute_direct_sql(
        self,
        sql: str,
        kg_name: str,
        select_schema: str,
        limit_records: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute SQL directly without LLM processing.

        This method bypasses the NL parsing and SQL generation pipeline,
        executing the provided SQL directly against the target database.

        Args:
            sql: SQL query to execute directly
            kg_name: Name of the Knowledge Graph (for connection context)
            select_schema: Database schema to query
            limit_records: Maximum number of records to return
            **kwargs: Additional parameters

        Returns:
            Dict containing execution results with keys:
            - generated_sql: The executed SQL query
            - number_of_records: Number of records returned
            - execution_status: 'success' or 'failed'
            - execution_time_ms: Execution time in milliseconds
            - confidence_score: Always 1.0 for direct SQL
            - data: List of result records
            - error_message: Error message if failed
        """
        import time
        from kg_builder.services.landing_db_connector import get_db_connection

        start_time = time.time()

        logger.info(f"🚀 DIRECT SQL EXECUTION")
        logger.info(f"   SQL Length: {len(sql)} characters")
        logger.info(f"   Schema: {select_schema}")
        logger.info(f"   Limit: {limit_records}")

        try:
            # Add limit clause if not already present
            sql_with_limit = self._add_limit_clause(sql, limit_records)

            logger.info(f"⚡ Executing SQL directly against database")
            db_exec_start = time.time()

            # Execute SQL
            with get_db_connection() as connection:
                logger.info(f"   Connection Type: {type(connection).__name__}")
                logger.info(f"   Starting database execution...")

                cursor = connection.cursor()
                cursor.execute(sql_with_limit)

                db_exec_time = (time.time() - db_exec_start) * 1000
                logger.info(f"✅ SQL executed successfully in {db_exec_time:.2f}ms")

                # Fetch results
                logger.info(f"📊 Fetching results...")
                fetch_start = time.time()

                rows = cursor.fetchall()
                fetch_time = (time.time() - fetch_start) * 1000

                logger.info(f"✅ Fetched {len(rows)} rows in {fetch_time:.2f}ms")

                # Convert rows to list of dictionaries
                if rows and hasattr(cursor, 'description') and cursor.description:
                    column_names = [desc[0] for desc in cursor.description]
                    records = [dict(zip(column_names, row)) for row in rows]
                else:
                    records = []
                    column_names = []

                execution_time_ms = (time.time() - start_time) * 1000

                logger.info(f"✅ Direct SQL execution completed in {execution_time_ms:.2f}ms")
                logger.info(f"   Records returned: {len(records)}")

                # Format response
                return {
                    'generated_sql': sql,
                    'number_of_records': len(records),
                    'execution_status': 'success',
                    'execution_time_ms': execution_time_ms,
                    'confidence_score': 1.0,  # Direct SQL has 100% confidence
                    'data': records,
                    'error_message': None,
                    'join_columns': [],
                    'source_table': '',
                    'target_table': '',
                    'column_names': column_names
                }

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = str(e)

            logger.error(f"❌ Direct SQL execution failed: {error_msg}")
            logger.error(f"   Execution time: {execution_time_ms:.2f}ms")
            logger.error(f"   SQL that failed:")
            logger.error(f"\n{sql}\n")

            return {
                'generated_sql': sql,
                'number_of_records': 0,
                'execution_status': 'failed',
                'execution_time_ms': execution_time_ms,
                'confidence_score': 1.0,  # SQL was provided, failure is execution issue
                'data': [],
                'error_message': error_msg,
                'join_columns': [],
                'source_table': '',
                'target_table': '',
                'column_names': []
            }


def get_nl_query_executor(db_type: str = "mysql", kg: Optional["KnowledgeGraph"] = None, use_llm: bool = True, excluded_fields: Optional[List[str]] = None) -> NLQueryExecutor:
    """
    Get or create NL query executor instance.

    Args:
        db_type: Database type (mysql, postgresql, sqlserver, oracle)
        kg: Optional Knowledge Graph for join column resolution
        use_llm: Whether to use LLM for SQL generation (default: True for LLM-only)
        excluded_fields: List of field names to avoid in joins (optional)
    """
    return NLQueryExecutor(db_type, kg=kg, use_llm=use_llm, excluded_fields=excluded_fields)

