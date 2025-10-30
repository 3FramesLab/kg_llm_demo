"""
LLM SQL Generator

Generates SQL queries directly from natural language using LLM with full schema context.
Provides intelligent SQL generation with automatic fallback to Python templates.
"""

import logging
import json
import re
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from kg_builder.services.llm_service import get_llm_service
from kg_builder.services.nl_query_parser import QueryIntent

if TYPE_CHECKING:
    from kg_builder.models import KnowledgeGraph

logger = logging.getLogger(__name__)


class LLMSQLGenerator:
    """Generate SQL directly using LLM with full schema context."""

    def __init__(self, db_type: str = "mysql", kg: Optional["KnowledgeGraph"] = None):
        """
        Initialize LLM SQL generator.

        Args:
            db_type: Database type (mysql, postgresql, sqlserver, oracle)
            kg: Knowledge Graph with schema and relationships
        """
        self.db_type = db_type.lower()
        self.kg = kg
        self.llm_service = get_llm_service()

        if not self.llm_service.is_enabled():
            raise ValueError("LLM service is not enabled. Please configure OPENAI_API_KEY.")

        logger.info(f"✓ LLM SQL Generator initialized for {self.db_type}")

    def generate(self, intent: QueryIntent) -> str:
        """
        Generate SQL from query intent using LLM.

        Args:
            intent: QueryIntent object with parsed query information

        Returns:
            str: Generated SQL query

        Raises:
            ValueError: If SQL generation fails
        """
        try:
            logger.info(f"🤖 Generating SQL with LLM for: {intent.definition}")

            # Build schema context for LLM
            schema_context = self._build_schema_context(intent)

            # Build the LLM prompt
            prompt = self._build_sql_generation_prompt(intent, schema_context)

            # Call LLM
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
                temperature=0.1,  # Low temperature for consistent SQL generation
                max_tokens=1500
            )

            # Log the raw response for debugging
            raw_response = response.choices[0].message.content
            logger.info(f"🔍 GPT-5 Response: {raw_response[:200]}...")

            # Extract SQL from response
            sql = self._extract_sql_from_response(raw_response)

            # Validate SQL for security
            self._validate_sql_security(sql, intent)

            logger.info(f"✅ LLM SQL generation successful")
            logger.debug(f"Generated SQL:\n{sql}")

            return sql

        except Exception as e:
            logger.error(f"❌ LLM SQL generation failed: {e}")
            raise

    def _get_system_prompt(self) -> str:
        """Get the system prompt for SQL generation."""
        return f"""You are an expert SQL query generator for {self.db_type.upper()} databases.

Your task is to generate ONLY the SQL query based on the provided context and requirements.

CRITICAL RULES:
1. Return ONLY the SQL query - no explanations, no markdown, no code blocks
2. Use the exact table and column names provided in the schema context
3. Follow {self.db_type.upper()} syntax rules strictly
4. Generate safe, read-only SELECT queries only
5. Never use DROP, DELETE, UPDATE, INSERT, TRUNCATE, ALTER, or other destructive operations
6. Use proper JOINs based on the relationships provided
7. Apply filters exactly as specified in the requirements
8. Use appropriate column quoting for {self.db_type}

SPECIAL ATTENTION - Additional Columns:
When the query asks to "also show X from Y" or "include X from Y":
• This means ADD a column from another table
• You MUST add a LEFT JOIN to that table
• Use the relationships provided to find the correct JOIN condition
• Add the column to the SELECT clause
• NEVER skip the JOIN - the column requires it

Example:
Query: "Show products in A not in B, also show vendor from C"
→ Need 2 JOINs: One for A↔B comparison, one for A↔C column
→ SELECT s.*, c.vendor FROM A s LEFT JOIN B t ... LEFT JOIN C c ..."""

    def _build_schema_context(self, intent: QueryIntent) -> Dict[str, Any]:
        """
        Build comprehensive schema context for LLM.

        Args:
            intent: QueryIntent with table and column information

        Returns:
            Dictionary with schema context
        """
        context = {
            "database_type": self.db_type,
            "tables": {},
            "relationships": [],
            "table_aliases": {}
        }

        if not self.kg:
            logger.warning("No Knowledge Graph provided - limited schema context")
            return context

        # Extract table information from KG
        for node in self.kg.nodes:
            if node.properties.get("type") == "Table":
                table_name = node.label
                columns = []

                # Extract column names
                for col in node.properties.get("columns", []):
                    if isinstance(col, dict):
                        col_name = col.get("name")
                        if col_name:
                            columns.append(col_name)
                    elif hasattr(col, 'name'):
                        columns.append(col.name)

                context["tables"][table_name] = {
                    "columns": columns,
                    "description": node.properties.get("description", "")
                }

        # Extract relationships from KG
        for rel in self.kg.relationships:
            if rel.source_column and rel.target_column:
                context["relationships"].append({
                    "source_table": rel.source_id,
                    "target_table": rel.target_id,
                    "source_column": rel.source_column,
                    "target_column": rel.target_column,
                    "relationship_type": rel.relationship_type
                })

        # Extract table aliases from KG
        if self.kg.table_aliases:
            context["table_aliases"] = self.kg.table_aliases

        logger.debug(f"Schema context: {len(context['tables'])} tables, {len(context['relationships'])} relationships")
        return context

    def _build_sql_generation_prompt(self, intent: QueryIntent, schema_context: Dict[str, Any]) -> str:
        """
        Build the LLM prompt for SQL generation.

        Args:
            intent: QueryIntent object
            schema_context: Schema context dictionary

        Returns:
            str: Formatted prompt for LLM
        """
        # Format tables
        tables_info = []
        for table_name, table_data in schema_context["tables"].items():
            columns_str = ", ".join(table_data["columns"][:20])  # Limit to first 20 columns
            if len(table_data["columns"]) > 20:
                columns_str += f", ... ({len(table_data['columns']) - 20} more)"
            tables_info.append(f"  • {table_name}: [{columns_str}]")

        tables_str = "\n".join(tables_info) if tables_info else "  (No tables available)"

        # Format relationships
        relationships_info = []
        for rel in schema_context["relationships"][:15]:  # Limit to 15 relationships
            relationships_info.append(
                f"  • {rel['source_table']}.{rel['source_column']} ↔ "
                f"{rel['target_table']}.{rel['target_column']} ({rel['relationship_type']})"
            )

        relationships_str = "\n".join(relationships_info) if relationships_info else "  (No relationships available)"

        # Format table aliases
        aliases_info = []
        for business_name, actual_table in schema_context["table_aliases"].items():
            aliases_info.append(f"  • \"{business_name}\" → {actual_table}")

        aliases_str = "\n".join(aliases_info) if aliases_info else "  (No aliases available)"

        # Format filters
        filters_info = []
        if intent.filters:
            for f in intent.filters:
                if isinstance(f, dict):
                    # Dictionary format
                    column = f.get('column', '')
                    operator = f.get('operator', '=')
                    value = f.get('value', '')
                    table_hint = f.get('table', '')  # Check if filter specifies which table
                    if table_hint:
                        filters_info.append(f"  • {table_hint}.{column} {operator} {value}")
                    else:
                        filters_info.append(f"  • {column} {operator} {value}")
                elif hasattr(f, 'column'):
                    # Object format (Filter dataclass)
                    filters_info.append(f"  • {f.column} {f.operator} {f.value}")

        filters_str = "\n".join(filters_info) if filters_info else "  (No filters)"

        # Format additional columns
        additional_columns_info = []
        if intent.additional_columns:
            additional_columns_info.append("  ⚠️ IMPORTANT: Each column below REQUIRES a LEFT JOIN to its source table!")
            for col in intent.additional_columns:
                additional_columns_info.append(f"  • Column: '{col.column_name}' from Table: '{col.source_table}'")
                additional_columns_info.append(f"    → Must add: LEFT JOIN {col.source_table} <alias> ON ...")

        additional_columns_str = "\n".join(additional_columns_info) if additional_columns_info else "  (No additional columns requested)"

        # Database-specific quoting rules
        quoting_rules = {
            "mysql": "Use backticks for identifiers: `table_name`, `column_name`",
            "postgresql": "Use double quotes for identifiers: \"table_name\", \"column_name\"",
            "sqlserver": "Use square brackets for identifiers: [table_name], [column_name]",
            "oracle": "Use double quotes for identifiers: \"table_name\", \"column_name\""
        }
        quoting_rule = quoting_rules.get(self.db_type, "Use appropriate quoting for identifiers")

        # Build the complete prompt
        prompt = f"""Generate a SQL query for the following natural language request:

"{intent.definition}"

=== QUERY REQUIREMENTS ===

Query Type: {intent.query_type}
Operation: {intent.operation or 'N/A'}
Source Table: {intent.source_table or 'N/A'}
Target Table: {intent.target_table or 'N/A'}

Filters:
{filters_str}

Additional Columns:
{additional_columns_str}

=== DATABASE SCHEMA ===

Available Tables:
{tables_str}

Table Relationships (for JOINs):
{relationships_str}

Table Aliases (Business Names → Actual Tables):
{aliases_str}

=== DATABASE RULES ===

Database Type: {self.db_type.upper()}
Identifier Quoting: {quoting_rule}

=== SQL GENERATION INSTRUCTIONS ===

1. **Table Resolution**:
   - If the query mentions business names (e.g., "RBP GPU", "OPS Excel"), use the Table Aliases section to resolve them to actual table names.
   - Business names are case-insensitive and may contain spaces.
   - Example: "RBP GPU" → brz_lnd_RBP_GPU

2. **JOIN Logic (Base Query)**:
   - For query_type = "comparison_query":
     * If operation = "NOT_IN": Use LEFT JOIN with WHERE target IS NULL
     * If operation = "IN": Use INNER JOIN
   - IMPORTANT - Understand the intent:
     * "products NOT IN table" → LEFT JOIN + WHERE target IS NULL
     * "products IN table" → INNER JOIN
     * "products IN [status] table" → INNER JOIN + WHERE status filter
     * "products matching [status] table" → INNER JOIN + WHERE status filter
   - Use the relationships provided above for JOIN conditions
   - Join on the exact column pairs specified in relationships
   - Main query uses aliases: s (source), t (target)

   **EXAMPLES:**
   • "products in RBP not in OPS" → LEFT JOIN + WHERE OPS IS NULL
   • "products in RBP in active OPS" → INNER JOIN + WHERE status = 'Active'
   • "products in RBP which are inactive OPS" → INNER JOIN + WHERE status = 'Inactive'
   • "products in RBP matching inactive OPS" → INNER JOIN + WHERE status = 'Inactive'

3. **Additional Columns - STEP-BY-STEP**:
   IF additional columns are specified, follow these steps CAREFULLY:

   Step 1 - Identify the Column Table:
   • Each additional column has format: "column_name from table_name"
   • Example: "planner from hana master"
     - Column: planner
     - Source Table: hana master (resolve to actual: hana_master_table)

   Step 2 - Find the JOIN Path:
   • Look in the "Table Relationships" section
   • Find a relationship between the main source table and the column's table
   • If direct relationship exists: Use it
   • If no direct relationship: Look for intermediate tables (multi-hop)
   • Example:
     - Main table: brz_lnd_RBP_GPU
     - Column table: hana_master
     - Relationship: brz_lnd_RBP_GPU.Material ↔ hana_master.material_id

   Step 3 - Generate the JOIN:
   • Use LEFT JOIN (not INNER) for additional columns (to avoid filtering records)
   • Use a new table alias (h, v, p, etc.)
   • Join on the relationship columns found in Step 2
   • Example:
     LEFT JOIN hana_master h ON s.Material = h.material_id

   Step 4 - Add Column to SELECT:
   • Add the column to SELECT clause after the main columns
   • Use the table alias from Step 3
   • Use the exact column name (not business name)
   • Add an alias for clarity
   • Example:
     SELECT DISTINCT s.*, h.planner AS planner

   **COMPLETE EXAMPLE for Additional Columns:**
   ```
   Input: "Show products in RBP GPU not in OPS Excel, also show planner from hana master"

   Base Query (without additional column):
   SELECT DISTINCT s.*
   FROM brz_lnd_RBP_GPU s
   LEFT JOIN brz_lnd_OPS_EXCEL_GPU t ON s.Material = t.PLANNING_SKU
   WHERE t.PLANNING_SKU IS NULL

   After adding "planner from hana master":
   1. Resolve "hana master" → hana_master (from aliases)
   2. Find relationship: brz_lnd_RBP_GPU.Material ↔ hana_master.material_id
   3. Add LEFT JOIN: LEFT JOIN hana_master h ON s.Material = h.material_id
   4. Update SELECT: SELECT DISTINCT s.*, h.planner AS planner

   Final Query:
   SELECT DISTINCT s.*, h.planner AS planner
   FROM brz_lnd_RBP_GPU s
   LEFT JOIN brz_lnd_OPS_EXCEL_GPU t ON s.Material = t.PLANNING_SKU
   LEFT JOIN hana_master h ON s.Material = h.material_id
   WHERE t.PLANNING_SKU IS NULL
   ```

4. **Filter Logic**:
   - Apply all filters specified in the Filters section
   - Use AND logic unless specified otherwise
   - Apply filters to the correct table (use table alias)
   - Handle NULL checks appropriately
   - Example: "where status is active" → WHERE s.status = 'active'

5. **Query Structure Rules**:
   - Use DISTINCT for comparison queries (to avoid duplicates from JOINs)
   - Apply WHERE clauses after all JOIN clauses
   - Use correct identifier quoting for {self.db_type.upper()}
   - Table aliases: s (source), t (target), h/v/p/m (additional tables)
   - JOIN order: Main JOIN first, then additional column JOINs

6. **Multi-Table JOINs**:
   - If query needs 3+ tables, add them sequentially
   - Always use relationship columns from the "Table Relationships" section
   - Example for 3 tables:
     FROM table1 s
     JOIN table2 t ON s.col1 = t.col2
     LEFT JOIN table3 h ON s.col3 = h.col4

Generate ONLY the SQL query, no explanations, no markdown formatting."""

        return prompt

    def _extract_sql_from_response(self, response_text: str) -> str:
        """
        Extract SQL from LLM response.

        Args:
            response_text: Raw LLM response

        Returns:
            str: Extracted SQL query

        Raises:
            ValueError: If SQL extraction fails
        """
        logger.debug(f"🔍 Extracting SQL from response (length: {len(response_text)})")
        logger.debug(f"🔍 First 200 chars: {response_text[:200]}")

        # Remove markdown code blocks if present
        sql = response_text.strip()
        logger.debug(f"🔍 After strip: '{sql[:100]}...'")

        # Remove ```sql or ``` markers
        original_sql = sql
        sql = re.sub(r'^```sql\s*\n?', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'^```\s*\n?', '', sql)
        sql = re.sub(r'\n?```$', '', sql)

        if sql != original_sql:
            logger.debug(f"🔍 After removing markdown: '{sql[:100]}...'")

        # Clean up
        sql = sql.strip()
        logger.debug(f"🔍 Final cleaned SQL: '{sql[:100]}...'")

        if not sql:
            logger.error(f"❌ LLM returned empty SQL after processing")
            logger.error(f"❌ Original response was: '{response_text}'")
            raise ValueError("LLM returned empty SQL")

        # Basic validation - must start with SELECT
        if not sql.upper().startswith('SELECT'):
            logger.error(f"❌ Generated SQL does not start with SELECT: '{sql[:100]}'")
            raise ValueError(f"Generated SQL does not start with SELECT: {sql[:100]}")

        logger.debug(f"✅ Successfully extracted SQL: {len(sql)} characters")
        return sql

    def _validate_sql_security(self, sql: str, intent: QueryIntent):
        """
        Validate generated SQL for security issues.

        Args:
            sql: Generated SQL query
            intent: Original query intent

        Raises:
            ValueError: If SQL contains dangerous operations
        """
        sql_upper = sql.upper()

        # Block dangerous operations
        dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE',
            'ALTER', 'CREATE', 'GRANT', 'REVOKE', 'EXEC',
            'EXECUTE', 'UNION', 'DECLARE', '--', '/*', 'xp_', 'sp_'
        ]

        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise ValueError(f"SQL contains dangerous keyword: {keyword}")

        # Must have source table
        if intent.source_table and intent.source_table not in sql:
            logger.warning(f"Generated SQL missing source table: {intent.source_table}")

        # For comparison queries, should have JOIN
        if intent.query_type == "comparison_query" and intent.target_table:
            if 'JOIN' not in sql_upper:
                raise ValueError("Comparison query missing JOIN clause")

        logger.debug("✓ SQL security validation passed")


def get_llm_sql_generator(db_type: str = "mysql", kg: Optional["KnowledgeGraph"] = None) -> LLMSQLGenerator:
    """
    Get LLM SQL generator instance.

    Args:
        db_type: Database type
        kg: Knowledge Graph

    Returns:
        LLMSQLGenerator instance
    """
    return LLMSQLGenerator(db_type, kg)
