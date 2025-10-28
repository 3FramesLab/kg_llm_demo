"""
LLM-based SQL Generator

Generates SQL queries using LLM instead of hardcoded templates.
Supports complex queries with proper validation and fallback mechanisms.
"""

import json
import logging
import re
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from kg_builder.services.nl_query_parser import QueryIntent
from kg_builder.services.llm_service import get_llm_service

if TYPE_CHECKING:
    from kg_builder.models import KnowledgeGraph

logger = logging.getLogger(__name__)


class LLMSQLGenerator:
    """Generate SQL queries using LLM instead of hardcoded templates."""

    def __init__(self, db_type: str = "mysql", kg: Optional["KnowledgeGraph"] = None):
        """
        Initialize LLM SQL generator.

        Args:
            db_type: Database type (mysql, postgresql, sqlserver, oracle)
            kg: Optional Knowledge Graph for join column resolution
        """
        self.db_type = db_type.lower()
        self.kg = kg
        self.llm_service = get_llm_service()

        if not self.llm_service.is_enabled():
            logger.warning("LLM service not enabled - LLMSQLGenerator will fail on generate()")

    def generate(self, intent: QueryIntent) -> str:
        """
        Generate SQL using LLM.

        Args:
            intent: QueryIntent object

        Returns:
            str: Generated SQL query

        Raises:
            ValueError: If LLM service not enabled or validation fails
        """
        if not self.llm_service.is_enabled():
            raise ValueError("LLM service not enabled")

        logger.info(f"🤖 Generating SQL via LLM for: {intent.definition}")
        logger.info(f"   Query Type: {intent.query_type}, Operation: {intent.operation}")

        # Build prompt with context
        prompt = self._build_sql_generation_prompt(intent)

        try:
            # Call LLM to generate SQL
            response = self.llm_service.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.1  # Low temperature for consistent SQL generation
            )

            sql = response.choices[0].message.content.strip()

            # Clean up SQL (remove markdown code blocks if present)
            sql = self._clean_sql_response(sql)

            # Validate SQL
            self._validate_sql(sql, intent)

            logger.info(f"✅ LLM SQL Generated Successfully")
            logger.debug(f"Generated SQL:\n{sql}")

            return sql

        except Exception as e:
            logger.error(f"❌ LLM SQL generation failed: {e}")
            raise

    def _get_system_prompt(self) -> str:
        """Get system prompt for SQL generation."""
        return f"""You are an expert SQL developer specializing in {self.db_type.upper()} databases.

Your task is to generate precise, efficient SQL queries based on structured query intents and knowledge graph relationships.

KEY RULES:
1. Generate ONLY valid {self.db_type.upper()} SQL syntax
2. Use exact table names and column names provided in the context
3. Use proper join conditions from the Knowledge Graph relationships
4. Support complex WHERE clauses with multiple operators (=, >, <, >=, <=, LIKE, IN, BETWEEN, IS NULL)
5. Use appropriate quoting for identifiers based on database type
6. Return ONLY the SQL query - no explanations, no markdown, no additional text
7. Never use DROP, DELETE, TRUNCATE, ALTER, or other destructive operations
8. Always use LEFT JOIN for additional columns to avoid losing rows
9. Use DISTINCT when comparing sets or when joins might create duplicates
10. Apply filters to the appropriate table alias in multi-table queries"""

    def _build_sql_generation_prompt(self, intent: QueryIntent) -> str:
        """
        Build comprehensive prompt for SQL generation.

        Args:
            intent: QueryIntent object

        Returns:
            str: Complete prompt for LLM
        """
        # Format Knowledge Graph context
        kg_context = self._format_kg_context(intent)

        # Format filters (use filters_v2 if available, else fallback to legacy filters)
        filters_to_use = intent.filters_v2 if hasattr(intent, 'filters_v2') and intent.filters_v2 else intent.filters
        filters_context = self._format_filters(filters_to_use) if filters_to_use else "None"

        # Format additional columns
        additional_cols_context = self._format_additional_columns(intent.additional_columns) if intent.additional_columns else "None"

        # Format complex query features (Phase 4)
        group_by_context = ", ".join(intent.group_by_columns) if hasattr(intent, 'group_by_columns') and intent.group_by_columns else "None"
        having_context = self._format_filters(intent.having_conditions) if hasattr(intent, 'having_conditions') and intent.having_conditions else "None"
        order_by_context = self._format_order_by(intent.order_by) if hasattr(intent, 'order_by') and intent.order_by else "None"
        limit_context = str(intent.limit) if hasattr(intent, 'limit') and intent.limit else "None"
        offset_context = str(intent.offset) if hasattr(intent, 'offset') and intent.offset else "None"

        # Build the prompt
        prompt = f"""Generate a SQL query for the following intent:

NATURAL LANGUAGE DEFINITION:
{intent.definition}

QUERY INTENT:
- Query Type: {intent.query_type}
- Source Table: {intent.source_table or 'N/A'}
- Target Table: {intent.target_table or 'N/A'}
- Operation: {intent.operation or 'N/A'}

FILTERS (WHERE Clause):
{filters_context}

ADDITIONAL COLUMNS:
{additional_cols_context}

GROUP BY:
{group_by_context}

HAVING (Aggregate Filters):
{having_context}

ORDER BY:
{order_by_context}

LIMIT:
{limit_context}

OFFSET:
{offset_context}

KNOWLEDGE GRAPH RELATIONSHIPS:
{kg_context}

DATABASE TYPE: {self.db_type.upper()}

QUERY TYPE SPECIFICATIONS:

1. COMPARISON_QUERY (Operation: NOT_IN or IN):
   - NOT_IN: Find records in source table but NOT in target table
     Use: SELECT DISTINCT s.* FROM source s LEFT JOIN target t ON s.join_col = t.join_col WHERE t.join_col IS NULL
   - IN: Find records that exist in BOTH source and target tables
     Use: SELECT DISTINCT s.* FROM source s INNER JOIN target t ON s.join_col = t.join_col

2. FILTER_QUERY:
   - Apply WHERE clause filters to source table
   - If target table present, join source and target, apply filters to target
   - Use: SELECT * FROM source WHERE conditions
   - Or: SELECT DISTINCT s.* FROM source s INNER JOIN target t ON join_cond WHERE t.filter_conditions

3. AGGREGATION_QUERY:
   - Use COUNT(*), SUM(), AVG(), MIN(), MAX() for aggregations
   - Apply filters in WHERE clause if present
   - Use GROUP BY for grouping
   - Use HAVING for aggregate conditions
   - Use: SELECT col, COUNT(*) as count FROM source WHERE conditions GROUP BY col HAVING count > 10

4. DATA_QUERY:
   - Simple SELECT all columns from source table
   - If target table present, join tables
   - Apply filters if present
   - Use: SELECT * FROM source WHERE conditions

OPERATOR SUPPORT (Phase 2):
- Comparison: =, >, <, >=, <=, !=, <>
- Pattern matching: LIKE (use % wildcards), NOT LIKE
- List matching: IN (value1, value2, ...), NOT IN (...)
- Range: BETWEEN value1 AND value2
- Null checks: IS NULL, IS NOT NULL
- Logic: AND, OR (combine multiple conditions)

Examples:
- price > 100
- status LIKE 'active%'
- category IN ('A', 'B', 'C')
- created_date BETWEEN '2024-01-01' AND '2024-12-31'
- deleted_at IS NULL

COMPLEX QUERY SUPPORT (Phase 4):
- GROUP BY: Group results by columns
  Example: SELECT category, COUNT(*) FROM products GROUP BY category
- HAVING: Filter on aggregated values
  Example: SELECT category, COUNT(*) as cnt FROM products GROUP BY category HAVING cnt > 10
- ORDER BY: Sort results (ASC or DESC)
  Example: SELECT * FROM products ORDER BY price DESC, name ASC
- LIMIT: Limit number of results
  Example: SELECT * FROM products LIMIT 100
- OFFSET: Skip rows (for pagination)
  Example: SELECT * FROM products LIMIT 100 OFFSET 50

IDENTIFIER QUOTING:
{self._get_quoting_rules()}

IMPORTANT:
- Use the EXACT table names provided above
- Use the EXACT column names from the Knowledge Graph
- Use proper join conditions from KG relationships
- Apply filters to the correct table alias (typically 't' for target in multi-table queries)
- Support all operators: =, >, <, >=, <=, LIKE, IN, BETWEEN, IS NULL
- Use GROUP BY when grouping is specified
- Use ORDER BY when sorting is specified
- Use LIMIT and OFFSET when specified
- Return ONLY the SQL query - no explanations or markdown

SQL QUERY:"""

        return prompt

    def _format_kg_context(self, intent: QueryIntent) -> str:
        """
        Format Knowledge Graph relationships for the prompt.

        Args:
            intent: QueryIntent object

        Returns:
            str: Formatted KG context
        """
        if not self.kg:
            # If no KG but we have join_columns from intent, format those
            if intent.join_columns and len(intent.join_columns) > 0:
                join_info = []
                for source_col, target_col in intent.join_columns:
                    join_info.append({
                        "source_table": intent.source_table,
                        "source_column": source_col,
                        "target_table": intent.target_table,
                        "target_column": target_col,
                        "relationship_type": "MATCHES"
                    })
                return json.dumps(join_info, indent=2)
            return "No Knowledge Graph available. Use standard join patterns."

        # Extract relevant relationships for the source and target tables
        relevant_relationships = []

        source_lower = intent.source_table.lower() if intent.source_table else ""
        target_lower = intent.target_table.lower() if intent.target_table else ""

        for rel in self.kg.relationships:
            source_id = rel.source_id.lower() if rel.source_id else ""
            target_id = rel.target_id.lower() if rel.target_id else ""

            # Check if this relationship involves our tables
            if source_lower and target_lower:
                if (source_lower in source_id or f"table_{source_lower}" == source_id) and \
                   (target_lower in target_id or f"table_{target_lower}" == target_id):
                    relevant_relationships.append(self._format_relationship(rel))
                elif (target_lower in source_id or f"table_{target_lower}" == source_id) and \
                     (source_lower in target_id or f"table_{source_lower}" == target_id):
                    relevant_relationships.append(self._format_relationship(rel))
            elif source_lower and (source_lower in source_id or source_lower in target_id or
                                   f"table_{source_lower}" == source_id or f"table_{source_lower}" == target_id):
                relevant_relationships.append(self._format_relationship(rel))

        # Also include join paths if we have additional columns
        if intent.additional_columns:
            for col in intent.additional_columns:
                if col.join_path and len(col.join_path) > 1:
                    for i in range(len(col.join_path) - 1):
                        table1 = col.join_path[i].lower()
                        table2 = col.join_path[i + 1].lower()

                        # Find relationship for this path segment
                        for rel in self.kg.relationships:
                            source_id = rel.source_id.lower() if rel.source_id else ""
                            target_id = rel.target_id.lower() if rel.target_id else ""

                            if (table1 in source_id or f"table_{table1}" == source_id) and \
                               (table2 in target_id or f"table_{table2}" == target_id):
                                formatted_rel = self._format_relationship(rel)
                                if formatted_rel not in relevant_relationships:
                                    relevant_relationships.append(formatted_rel)

        if not relevant_relationships:
            return "No relevant relationships found in Knowledge Graph."

        return json.dumps(relevant_relationships, indent=2)

    def _format_relationship(self, rel) -> Dict[str, Any]:
        """Format a relationship for the prompt."""
        return {
            "source": rel.source_id,
            "target": rel.target_id,
            "source_column": rel.source_column or rel.properties.get("source_column") if rel.properties else None,
            "target_column": rel.target_column or rel.properties.get("target_column") if rel.properties else None,
            "relationship_type": rel.relationship_type
        }

    def _format_filters(self, filters) -> str:
        """
        Format filters for the prompt.

        Args:
            filters: List of Filter objects or filter dictionaries

        Returns:
            str: Formatted filters
        """
        if not filters:
            return "None"

        formatted_filters = []
        for f in filters:
            if hasattr(f, 'to_dict'):
                # Filter object (Phase 2)
                formatted_filters.append(f.to_dict())
            elif isinstance(f, dict):
                # Legacy dict format
                formatted_filters.append({
                    "column": f.get("column", ""),
                    "operator": f.get("operator", "="),
                    "value": f.get("value", ""),
                    "logic": f.get("logic", "AND")
                })

        return json.dumps(formatted_filters, indent=2)

    def _format_order_by(self, order_by_list) -> str:
        """
        Format ORDER BY clause for the prompt.

        Args:
            order_by_list: List of OrderBy objects

        Returns:
            str: Formatted ORDER BY
        """
        if not order_by_list:
            return "None"

        formatted = []
        for ob in order_by_list:
            if hasattr(ob, 'to_dict'):
                formatted.append(ob.to_dict())
            elif isinstance(ob, dict):
                formatted.append(ob)

        return json.dumps(formatted, indent=2)

    def _format_additional_columns(self, columns) -> str:
        """
        Format additional columns for the prompt.

        Args:
            columns: List of AdditionalColumn objects

        Returns:
            str: Formatted additional columns
        """
        if not columns:
            return "None"

        formatted_cols = []
        for col in columns:
            formatted_cols.append({
                "column_name": col.column_name,
                "source_table": col.source_table,
                "alias": col.alias,
                "join_path": col.join_path
            })

        return json.dumps(formatted_cols, indent=2)

    def _get_quoting_rules(self) -> str:
        """Get identifier quoting rules based on database type."""
        if self.db_type == "sqlserver":
            return "Use square brackets: [table_name], [column_name]"
        elif self.db_type == "oracle":
            return 'Use double quotes: "table_name", "column_name"'
        else:  # mysql, postgresql
            return "Use backticks: `table_name`, `column_name`"

    def _clean_sql_response(self, sql: str) -> str:
        """
        Clean SQL response from LLM (remove markdown, extra whitespace, etc.).

        Args:
            sql: Raw SQL from LLM

        Returns:
            str: Cleaned SQL
        """
        # Remove markdown code blocks
        sql = re.sub(r'^```sql\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'^```\s*', '', sql)
        sql = re.sub(r'\s*```$', '', sql)

        # Remove leading/trailing whitespace
        sql = sql.strip()

        # Remove any explanatory text after the SQL (look for common patterns)
        # Stop at lines that look like explanations
        lines = sql.split('\n')
        sql_lines = []
        for line in lines:
            # Skip empty lines at the start
            if not sql_lines and not line.strip():
                continue
            # Stop if we hit an explanation line
            if line.strip().startswith(('Note:', 'Explanation:', 'This query', 'The query')):
                break
            sql_lines.append(line)

        sql = '\n'.join(sql_lines).strip()

        return sql

    def _validate_sql(self, sql: str, intent: QueryIntent) -> None:
        """
        Validate generated SQL for security and correctness.

        Args:
            sql: Generated SQL query
            intent: Original query intent

        Raises:
            ValueError: If validation fails
        """
        # Check for required tables
        sql_upper = sql.upper()

        if intent.source_table:
            source_table_upper = intent.source_table.upper()
            if source_table_upper not in sql_upper:
                raise ValueError(f"Generated SQL missing source table: {intent.source_table}")

        if intent.target_table:
            target_table_upper = intent.target_table.upper()
            if target_table_upper not in sql_upper:
                raise ValueError(f"Generated SQL missing target table: {intent.target_table}")

        # Check for dangerous SQL patterns (security)
        dangerous_patterns = [
            "DROP TABLE", "DROP DATABASE", "DROP SCHEMA",
            "DELETE FROM", "TRUNCATE", "ALTER TABLE",
            "CREATE TABLE", "CREATE DATABASE",
            "GRANT ", "REVOKE ",
            "EXEC ", "EXECUTE ",
            "UNION ALL SELECT", "UNION SELECT",  # Potential SQL injection
            "INFORMATION_SCHEMA",  # Schema introspection
            "SYS.", "MYSQL.", "PG_"  # System tables
        ]

        for pattern in dangerous_patterns:
            if pattern in sql_upper:
                raise ValueError(f"Dangerous SQL pattern detected: {pattern}")

        # Check SQL starts with SELECT
        if not sql_upper.strip().startswith("SELECT"):
            raise ValueError("Generated SQL must be a SELECT query")

        # Check for balanced quotes and parentheses
        if sql.count("'") % 2 != 0:
            raise ValueError("Unbalanced single quotes in generated SQL")

        if sql.count("(") != sql.count(")"):
            raise ValueError("Unbalanced parentheses in generated SQL")

        # Check SQL has required clauses for comparison queries
        if intent.query_type == "comparison_query":
            if "JOIN" not in sql_upper:
                raise ValueError("Comparison query must include JOIN clause")

        logger.debug("✓ SQL validation passed")


def get_llm_sql_generator(db_type: str = "mysql", kg: Optional["KnowledgeGraph"] = None) -> LLMSQLGenerator:
    """Get or create LLM SQL generator instance."""
    return LLMSQLGenerator(db_type, kg=kg)
