"""
Natural Language SQL Generator

Generates SQL queries from NL query intents.
Supports:
- Comparison queries (set difference, intersection)
- Filter queries (WHERE clauses)
- Aggregation queries (GROUP BY, COUNT, SUM)
- Multi-table joins
"""

import logging
from typing import Optional, List, Dict, Any

from kg_builder.services.nl_query_parser import QueryIntent

logger = logging.getLogger(__name__)


class NLSQLGenerator:
    """Generate SQL from NL query intents."""

    def __init__(self, db_type: str = "mysql"):
        """
        Initialize generator.

        Args:
            db_type: Database type (mysql, postgresql, sqlserver, oracle)
        """
        self.db_type = db_type.lower()

    def generate(self, intent: QueryIntent) -> str:
        """
        Generate SQL from query intent.

        Args:
            intent: QueryIntent object

        Returns:
            str: Generated SQL query
        """
        logger.info(f"🔧 Generating SQL for: {intent.definition}")
        logger.info(f"   Query Type: {intent.query_type}, Operation: {intent.operation}")
        if intent.filters:
            logger.info(f"   Filters: {intent.filters}")

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

        logger.info(f"✅ SQL Generated Successfully")
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

    def _build_where_clause(self, filters: List[Dict[str, Any]], table_alias: Optional[str] = None) -> str:
        """
        Build WHERE clause from filters.

        Args:
            filters: List of filter dictionaries
            table_alias: Optional table alias prefix

        Returns:
            str: WHERE clause conditions
        """
        conditions = []

        for filter_item in filters:
            column = filter_item.get("column", "")
            value = filter_item.get("value", "")

            if not column:
                continue

            column = self._quote_identifier(column)

            if table_alias:
                column = f"{table_alias}.{column}"

            # Handle different value types
            if isinstance(value, str):
                value = f"'{value}'"
            elif value is None:
                value = "NULL"

            conditions.append(f"{column} = {value}")

        return " AND ".join(conditions) if conditions else "1=1"

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


def get_nl_sql_generator(db_type: str = "mysql") -> NLSQLGenerator:
    """Get or create NL SQL generator instance."""
    return NLSQLGenerator(db_type)

