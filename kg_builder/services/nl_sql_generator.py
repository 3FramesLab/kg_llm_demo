"""
Natural Language SQL Generator

Generates SQL queries from NL query intents.
Supports:
- Comparison queries (set difference, intersection)
- Filter queries (WHERE clauses)
- Aggregation queries (GROUP BY, COUNT, SUM)
- Multi-table joins
- Additional columns from related tables
"""

import logging
import re
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from kg_builder.services.nl_query_parser import QueryIntent

if TYPE_CHECKING:
    from kg_builder.models import KnowledgeGraph

logger = logging.getLogger(__name__)


class NLSQLGenerator:
    """Generate SQL from NL query intents."""

    def __init__(self, db_type: str = "mysql", kg: Optional["KnowledgeGraph"] = None, use_llm: bool = False):
        """
        Initialize generator.

        Args:
            db_type: Database type (mysql, postgresql, sqlserver, oracle)
            kg: Optional Knowledge Graph for join column resolution
            use_llm: Whether to use LLM-based SQL generation (with Python fallback)
        """
        self.db_type = db_type.lower()
        self.kg = kg  # Store KG reference for join condition resolution
        self.use_llm = use_llm
        self.llm_generator = None

        # Initialize LLM generator if requested
        if use_llm:
            try:
                from kg_builder.services.llm_sql_generator import LLMSQLGenerator
                self.llm_generator = LLMSQLGenerator(db_type, kg)
                logger.info("✓ LLM SQL Generator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM generator: {e}")
                self.use_llm = False

    def generate(self, intent: QueryIntent) -> str:
        """
        Generate SQL from query intent with optional LLM fallback.

        Args:
            intent: QueryIntent object

        Returns:
            str: Generated SQL query
        """
        logger.info(f"🔧 Generating SQL for: {intent.definition}")
        logger.info(f"   Query Type: {intent.query_type}, Operation: {intent.operation}")
        logger.info(f"   Using: {'LLM' if self.use_llm else 'Python'} generator")
        if intent.filters:
            logger.info(f"   Filters: {intent.filters}")
        if intent.additional_columns:
            logger.info(f"   Additional Columns: {len(intent.additional_columns)}")

        # Try LLM generation first if enabled
        if self.use_llm and self.llm_generator:
            try:
                sql = self.llm_generator.generate(intent)
                logger.info(f"✅ SQL Generated Successfully (via LLM)")
                return sql
            except Exception as e:
                logger.warning(f"⚠️ LLM generation failed, falling back to Python: {e}")
                logger.info(f"   Fallback reason: {str(e)[:100]}")
                # Fall through to Python generation

        # Python-based generation (original implementation)
        sql = self._generate_python(intent)
        logger.info(f"✅ SQL Generated Successfully (via Python)")
        return sql

    def _generate_python(self, intent: QueryIntent) -> str:
        """
        Generate SQL using Python-based templates (original implementation).

        Args:
            intent: QueryIntent object

        Returns:
            str: Generated SQL query
        """
        if intent.query_type == "comparison_query":
            sql = self._generate_comparison_query(intent)
        elif intent.query_type == "filter_query":
            sql = self._generate_filter_query(intent)
        elif intent.query_type == "aggregation_query":
            sql = self._generate_aggregation_query(intent)
        elif intent.query_type == "data_query":
            sql = self._generate_data_query(intent)
        else:
            raise ValueError(f"Unsupported query type: {intent.query_type}")

        # Add additional columns if present
        if intent.additional_columns:
            sql = self._add_additional_columns_to_sql(sql, intent)

        return sql

    def _generate_comparison_query(self, intent: QueryIntent) -> str:
        """
        Generate comparison query (set difference, intersection, etc.).

        Examples:
        - NOT_IN: Products in A but not in B
        - IN: Products in both A and B
        """
        if not intent.source_table or not intent.target_table:
            raise ValueError("Comparison query requires both source and target tables")

        source = self._quote_identifier(intent.source_table)
        target = self._quote_identifier(intent.target_table)

        if not intent.join_columns or len(intent.join_columns) == 0:
            error_msg = (
                f"Comparison query requires join columns to compare '{intent.source_table}' and '{intent.target_table}', "
                f"but none were found. "
                f"\n\nTo fix this issue:"
                f"\n1. Ensure your Knowledge Graph has relationships between these tables"
                f"\n2. Use the 'Execute Queries' tab and add explicit relationship pairs:"
                f"\n   Example: {{"
                f"\n     \"source_table\": \"{intent.source_table}\","
                f"\n     \"source_column\": \"<matching_column>\","
                f"\n     \"target_table\": \"{intent.target_table}\","
                f"\n     \"target_column\": \"<matching_column>\","
                f"\n     \"relationship_type\": \"MATCHES\""
                f"\n   }}"
                f"\n3. Or add matching columns to your schema that can be auto-detected"
            )
            raise ValueError(error_msg)

        source_col, target_col = intent.join_columns[0]
        source_col = self._quote_identifier(source_col)
        target_col = self._quote_identifier(target_col)

        if intent.operation == "NOT_IN":
            # Products in source but not in target
            sql = f"""
SELECT DISTINCT s.*
FROM {source} s
LEFT JOIN {target} t ON s.{source_col} = t.{target_col}
WHERE t.{target_col} IS NULL
            """.strip()

        elif intent.operation == "IN":
            # Products in both source and target
            sql = f"""
SELECT DISTINCT s.*
FROM {source} s
INNER JOIN {target} t ON s.{source_col} = t.{target_col}
            """.strip()

        else:
            # Default to INNER JOIN
            sql = f"""
SELECT DISTINCT s.*
FROM {source} s
INNER JOIN {target} t ON s.{source_col} = t.{target_col}
            """.strip()

        # Add filters if present
        # Filters typically apply to the target table in multi-table queries
        if intent.filters:
            logger.info(f"   Adding filters to WHERE clause: {intent.filters}")
            where_clause = self._build_where_clause(intent.filters, "t")
            if intent.operation == "NOT_IN":
                # For NOT_IN, append to existing WHERE clause
                sql += f"\nAND {where_clause}"
                logger.info(f"   WHERE clause (appended): {where_clause}")
            else:
                # For IN and others, add new WHERE clause
                sql += f"\nWHERE {where_clause}"
                logger.info(f"   WHERE clause (new): {where_clause}")
        else:
            logger.debug(f"   No filters to apply")

        return sql

    def _generate_filter_query(self, intent: QueryIntent) -> str:
        """
        Generate filter query with WHERE conditions.

        Examples:
        - Show active products
        - Show products with status = 'active'
        """
        if not intent.source_table:
            raise ValueError("Filter query requires source table")

        source = self._quote_identifier(intent.source_table)

        if intent.target_table:
            # Multi-table filter
            target = self._quote_identifier(intent.target_table)

            if not intent.join_columns:
                raise ValueError("Multi-table filter requires join columns")

            source_col, target_col = intent.join_columns[0]
            source_col = self._quote_identifier(source_col)
            target_col = self._quote_identifier(target_col)

            sql = f"""
SELECT DISTINCT s.*
FROM {source} s
INNER JOIN {target} t ON s.{source_col} = t.{target_col}
            """.strip()
        else:
            # Single table filter
            sql = f"SELECT * FROM {source}"

        # Add filters
        # Filters typically apply to the target table in multi-table queries
        if intent.filters:
            if intent.target_table:
                # For multi-table filters, apply to target table (t)
                where_clause = self._build_where_clause(intent.filters, "t")
                logger.info(f"   Adding filters to target table: {intent.filters}")
            else:
                # For single-table filters, apply to source table (s)
                where_clause = self._build_where_clause(intent.filters, "s")
                logger.info(f"   Adding filters to source table: {intent.filters}")
            sql += f"\nWHERE {where_clause}"

        return sql

    def _generate_aggregation_query(self, intent: QueryIntent) -> str:
        """
        Generate aggregation query (COUNT, SUM, AVG, etc.).

        Examples:
        - Count products by category
        - Total quantity by supplier
        """
        if not intent.source_table:
            raise ValueError("Aggregation query requires source table")

        source = self._quote_identifier(intent.source_table)

        # Default aggregation: COUNT(*)
        sql = f"SELECT COUNT(*) as count FROM {source}"

        # Add filters if present
        if intent.filters:
            where_clause = self._build_where_clause(intent.filters)
            sql += f"\nWHERE {where_clause}"

        return sql

    def _generate_data_query(self, intent: QueryIntent) -> str:
        """
        Generate data query (simple SELECT).

        Examples:
        - Show all products
        - Show products from table X
        """
        if not intent.source_table:
            raise ValueError("Data query requires source table")

        source = self._quote_identifier(intent.source_table)

        if intent.target_table:
            # Multi-table query
            target = self._quote_identifier(intent.target_table)

            if not intent.join_columns:
                raise ValueError("Multi-table query requires join columns")

            source_col, target_col = intent.join_columns[0]
            source_col = self._quote_identifier(source_col)
            target_col = self._quote_identifier(target_col)

            sql = f"""
SELECT DISTINCT s.*
FROM {source} s
INNER JOIN {target} t ON s.{source_col} = t.{target_col}
            """.strip()
        else:
            # Single table query
            sql = f"SELECT * FROM {source}"

        # Add filters if present
        if intent.filters:
            where_clause = self._build_where_clause(intent.filters, "s" if intent.target_table else None)
            sql += f"\nWHERE {where_clause}"

        return sql

    def _build_where_clause(self, filters, table_alias: Optional[str] = None) -> str:
        """
        Build WHERE clause from filters with operator support (Phase 2).

        Args:
            filters: List of Filter objects or filter dictionaries
            table_alias: Optional table alias prefix

        Returns:
            str: WHERE clause conditions
        """
        conditions = []

        for filter_item in filters:
            # Handle both Filter objects and dict format
            if hasattr(filter_item, 'column'):
                # Filter object
                column = filter_item.column
                operator = getattr(filter_item, 'operator', '=')
                value = filter_item.value
                logic = getattr(filter_item, 'logic', 'AND')
            else:
                # Dict format
                column = filter_item.get("column", "")
                operator = filter_item.get("operator", "=")
                value = filter_item.get("value", "")
                logic = filter_item.get("logic", "AND")

            if not column:
                continue

            column = self._quote_identifier(column)

            if table_alias:
                column = f"{table_alias}.{column}"

            # Build condition based on operator (Phase 2 enhancement)
            condition = self._build_condition(column, operator, value)
            conditions.append(condition)

        # Join conditions with logic (default AND)
        if not conditions:
            return "1=1"

        # For now, use AND for all (Phase 2 can enhance to support mixed AND/OR)
        return " AND ".join(conditions)

    def _build_condition(self, column: str, operator: str, value: Any) -> str:
        """
        Build a single condition with operator support (Phase 2).

        Args:
            column: Column name (already quoted)
            operator: Operator (=, >, <, >=, <=, !=, LIKE, IN, BETWEEN, IS NULL, etc.)
            value: Value(s)

        Returns:
            str: SQL condition
        """
        operator = operator.upper().strip()

        # Null checks
        if operator in ("IS NULL", "IS NOT NULL"):
            return f"{column} {operator}"

        # BETWEEN
        if operator == "BETWEEN":
            if isinstance(value, (list, tuple)) and len(value) == 2:
                val1 = self._format_value(value[0])
                val2 = self._format_value(value[1])
                return f"{column} BETWEEN {val1} AND {val2}"
            else:
                # Fallback if value not in correct format
                return f"{column} = {self._format_value(value)}"

        # IN / NOT IN
        if operator in ("IN", "NOT IN"):
            if isinstance(value, (list, tuple)):
                values = ", ".join([self._format_value(v) for v in value])
                return f"{column} {operator} ({values})"
            elif isinstance(value, str) and ',' in value:
                # Handle comma-separated string
                values = ", ".join([self._format_value(v.strip()) for v in value.split(',')])
                return f"{column} {operator} ({values})"
            else:
                # Single value
                return f"{column} {operator} ({self._format_value(value)})"

        # LIKE / NOT LIKE
        if operator in ("LIKE", "NOT LIKE"):
            formatted_value = self._format_value(value)
            # If value doesn't have wildcards, add them
            if isinstance(value, str) and '%' not in value and '_' not in value:
                formatted_value = f"'%{value}%'"
            return f"{column} {operator} {formatted_value}"

        # Standard comparison operators: =, >, <, >=, <=, !=, <>
        if operator in ("=", ">", "<", ">=", "<=", "!=", "<>"):
            formatted_value = self._format_value(value)
            return f"{column} {operator} {formatted_value}"

        # Default fallback to =
        formatted_value = self._format_value(value)
        return f"{column} = {formatted_value}"

    def _format_value(self, value: Any) -> str:
        """
        Format a value for SQL.

        Args:
            value: Value to format

        Returns:
            str: Formatted value
        """
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            # Escape single quotes
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            # Default: convert to string
            escaped = str(value).replace("'", "''")
            return f"'{escaped}'"

    def _add_additional_columns_to_sql(self, base_sql: str, intent: QueryIntent) -> str:
        """
        Add additional columns from related tables to SQL query.

        This method:
        1. Extracts the SELECT clause from base SQL
        2. Adds additional columns with aliases
        3. Adds JOIN clauses for each additional column
        """
        if not intent.additional_columns:
            return base_sql

        logger.info(f"Adding {len(intent.additional_columns)} additional columns to SQL")

        # Extract SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', base_sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            logger.warning("Could not parse SELECT clause, returning base SQL")
            return base_sql

        select_clause = select_match.group(1).strip()

        # Build additional columns list
        additional_cols_sql = []
        for col in intent.additional_columns:
            # Get table alias for the source table
            table_alias = self._get_table_alias(col.source_table)
            col_quoted = self._quote_identifier(col.column_name)
            additional_cols_sql.append(f"{table_alias}.{col_quoted} AS {col.alias}")

        # Add additional columns to SELECT
        new_select = select_clause + ", " + ", ".join(additional_cols_sql)

        # Build JOIN clauses for each additional column
        join_clauses = self._generate_join_clauses_for_columns(intent.additional_columns)

        # Reconstruct SQL
        new_sql = base_sql.replace(select_clause, new_select)

        # Insert JOIN clauses before WHERE clause (if exists) or at the end
        if "WHERE" in new_sql.upper():
            # Insert before WHERE
            where_pos = re.search(r'\bWHERE\b', new_sql, re.IGNORECASE).start()
            new_sql = new_sql[:where_pos] + join_clauses + "\n" + new_sql[where_pos:]
        else:
            # Append at the end
            new_sql = new_sql + "\n" + join_clauses

        logger.info(f"✓ Added {len(intent.additional_columns)} additional columns to SQL")
        return new_sql

    def _generate_join_clauses_for_columns(self, columns: List) -> str:
        """
        Generate LEFT JOIN clauses for additional columns.

        Args:
            columns: List of AdditionalColumn objects

        Returns:
            str: JOIN clauses
        """
        joins = []
        processed_tables = set()

        for col in columns:
            if not col.join_path or len(col.join_path) < 2:
                logger.warning(f"No join path for column {col.column_name}")
                continue

            logger.debug(f"Processing join path for column {col.column_name}: {col.join_path}")

            # Generate JOIN for each step in path
            for i in range(len(col.join_path) - 1):
                table1 = col.join_path[i]
                table2 = col.join_path[i + 1]

                # Skip if same table (self-join not needed)
                if table1.lower() == table2.lower():
                    logger.debug(f"Skipping self-join: {table1} = {table2}")
                    continue

                # Skip if we already joined these tables
                join_key = f"{table1.lower()}_{table2.lower()}"
                if join_key in processed_tables:
                    logger.debug(f"Skipping already processed join: {join_key}")
                    continue

                processed_tables.add(join_key)

                alias1 = self._get_table_alias(table1)
                alias2 = self._get_table_alias(table2)

                table2_quoted = self._quote_identifier(table2)

                # Get actual join condition from KG
                join_condition = self._get_join_condition(table1, table2, alias1, alias2)

                join = f"LEFT JOIN {table2_quoted} {alias2} ON {join_condition}"
                joins.append(join)
                logger.debug(f"Generated join: {join}")

        return "\n".join(joins)

    def _get_join_condition(self, table1: str, table2: str, alias1: str, alias2: str) -> str:
        """
        Get actual join condition from KG relationships.

        Extracts source_column and target_column from KG relationships
        and constructs a proper JOIN condition.

        Args:
            table1: First table name
            table2: Second table name
            alias1: Alias for first table
            alias2: Alias for second table

        Returns:
            str: Join condition like "alias1.col1 = alias2.col2"
        """
        if not self.kg:
            # Fallback to placeholder if KG not available
            logger.warning(f"No KG available for join condition between {table1} and {table2}, using placeholder")
            return f"{alias1}.id = {alias2}.id"

        table1_lower = table1.lower()
        table2_lower = table2.lower()

        # Find relationship between table1 and table2
        for rel in self.kg.relationships:
            source_id = rel.source_id.lower() if rel.source_id else ""
            target_id = rel.target_id.lower() if rel.target_id else ""

            # Check forward direction: table1 → table2
            if (source_id == table1_lower or source_id == f"table_{table1_lower}") and \
               (target_id == table2_lower or target_id == f"table_{table2_lower}"):
                source_col = rel.source_column or (rel.properties.get("source_column") if rel.properties else None)
                target_col = rel.target_column or (rel.properties.get("target_column") if rel.properties else None)
                if source_col and target_col:
                    source_col_quoted = self._quote_identifier(source_col)
                    target_col_quoted = self._quote_identifier(target_col)
                    logger.debug(f"Found forward relationship: {table1}.{source_col} = {table2}.{target_col}")
                    return f"{alias1}.{source_col_quoted} = {alias2}.{target_col_quoted}"

            # Check reverse direction: table2 → table1
            if (source_id == table2_lower or source_id == f"table_{table2_lower}") and \
               (target_id == table1_lower or target_id == f"table_{table1_lower}"):
                source_col = rel.source_column or (rel.properties.get("source_column") if rel.properties else None)
                target_col = rel.target_column or (rel.properties.get("target_column") if rel.properties else None)
                if source_col and target_col:
                    source_col_quoted = self._quote_identifier(source_col)
                    target_col_quoted = self._quote_identifier(target_col)
                    logger.debug(f"Found reverse relationship: {table1}.{target_col} = {table2}.{source_col}")
                    return f"{alias1}.{target_col_quoted} = {alias2}.{source_col_quoted}"

        # Fallback if no relationship found
        logger.warning(f"No relationship found between {table1} and {table2}, using placeholder")
        return f"{alias1}.id = {alias2}.id"

    def _get_table_alias(self, table_name: str) -> str:
        """
        Get or create table alias for a table name.

        Uses first letter or abbreviation of table name.
        """
        # Extract meaningful part of table name
        parts = table_name.split('_')
        if len(parts) > 1:
            # For names like "brz_lnd_RBP_GPU", use last part
            return parts[-1][0].lower()
        else:
            return table_name[0].lower()

    def _quote_identifier(self, identifier: str) -> str:
        """
        Quote identifier based on database type.

        Args:
            identifier: Identifier to quote

        Returns:
            str: Quoted identifier
        """
        if self.db_type == "sqlserver":
            return f"[{identifier}]"
        elif self.db_type == "oracle":
            return f'"{identifier}"'
        else:  # mysql, postgresql
            return f"`{identifier}`"


def get_nl_sql_generator(db_type: str = "mysql", kg: Optional["KnowledgeGraph"] = None, use_llm: bool = False) -> NLSQLGenerator:
    """
    Get or create NL SQL generator instance.

    Args:
        db_type: Database type (mysql, postgresql, sqlserver, oracle)
        kg: Optional Knowledge Graph for join column resolution
        use_llm: Whether to use LLM-based SQL generation (with Python fallback)

    Returns:
        NLSQLGenerator instance
    """
    return NLSQLGenerator(db_type, kg=kg, use_llm=use_llm)

