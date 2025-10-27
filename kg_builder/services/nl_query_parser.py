"""
Natural Language Query Parser

Parses NL definitions into executable query intents.
Uses Knowledge Graph to infer join columns.
"""

import json
import logging
import re
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, Tuple

from kg_builder.models import KnowledgeGraph
from kg_builder.services.nl_query_classifier import (
    NLQueryClassifier, DefinitionType, get_nl_query_classifier
)
from kg_builder.services.llm_service import get_llm_service
from kg_builder.services.table_name_mapper import get_table_name_mapper

logger = logging.getLogger(__name__)


@dataclass
class QueryIntent:
    """Parsed intent from NL definition."""
    definition: str
    query_type: str  # DefinitionType.value
    source_table: Optional[str] = None
    target_table: Optional[str] = None
    operation: Optional[str] = None  # NOT_IN, IN, EQUALS, CONTAINS, AGGREGATE
    filters: List[Dict[str, Any]] = None
    join_columns: Optional[List[Tuple[str, str]]] = None  # [(source_col, target_col), ...]
    confidence: float = 0.75
    reasoning: str = ""

    def __post_init__(self):
        """Initialize default values."""
        if self.filters is None:
            self.filters = []
        if self.join_columns is None:
            self.join_columns = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class NLQueryParser:
    """Parse NL definitions into executable query intents."""

    def __init__(self, kg: Optional[KnowledgeGraph] = None, schemas_info: Optional[Dict] = None):
        """
        Initialize parser.

        Args:
            kg: Knowledge graph for join inference
            schemas_info: Schema information
        """
        self.kg = kg
        self.schemas_info = schemas_info or {}
        self.classifier = get_nl_query_classifier()
        self.llm_service = get_llm_service()
        self.table_mapper = get_table_name_mapper(schemas_info)

    def parse(self, definition: str, use_llm: bool = True) -> QueryIntent:
        """
        Parse definition into query intent.

        Args:
            definition: Natural language definition
            use_llm: Whether to use LLM for parsing

        Returns:
            QueryIntent: Parsed query intent
        """
        logger.info(f"Parsing definition: {definition}")

        # Step 1: Classify
        def_type = self.classifier.classify(definition)
        operation = self.classifier.get_operation_type(definition)

        # Step 2: Extract tables and details
        if use_llm and self.llm_service.is_enabled():
            intent = self._parse_with_llm(definition, def_type, operation)
        else:
            intent = self._parse_rule_based(definition, def_type, operation)

        # Step 2.5: Resolve table names using mapper (business terms → actual table names)
        intent = self._resolve_table_names(intent)

        # Step 3: Use KG and schemas to find join columns
        if intent.source_table and intent.target_table:
            if not intent.join_columns or len(intent.join_columns) == 0:
                join_cols = self._find_join_columns_from_kg(
                    intent.source_table,
                    intent.target_table
                )
                if join_cols:
                    intent.join_columns = join_cols
                    intent.confidence = min(0.95, intent.confidence + 0.1)
                    logger.info(f"✓ Successfully found join columns: {join_cols}")
                else:
                    logger.warning(f"⚠ No join columns found for {intent.source_table} ←→ {intent.target_table}")

                    # For comparison queries, this is critical
                    if intent.query_type == "comparison_query":
                        logger.error(
                            f"CRITICAL: Comparison query requires join columns but none were found. "
                            f"Please ensure the KG has relationships between '{intent.source_table}' and '{intent.target_table}' "
                            f"with 'source_column' and 'target_column' properties."
                        )
                        intent.confidence = 0.3  # Very low confidence

        logger.info(f"Parsed intent: query_type={intent.query_type}, source={intent.source_table}, target={intent.target_table}, join_cols={intent.join_columns}")
        return intent

    def _parse_with_llm(
        self,
        definition: str,
        def_type: DefinitionType,
        operation: Optional[str]
    ) -> QueryIntent:
        """Parse using LLM."""
        try:
            prompt = self._build_parsing_prompt(definition, def_type, operation)
            logger.debug(f"LLM Parsing Prompt:\n{prompt}")

            # Use the LLM service's helper method that handles parameter compatibility
            response = self.llm_service.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert data analyst. Parse natural language queries and extract structured information. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )

            result_text = response.choices[0].message.content
            logger.debug(f"LLM Response:\n{result_text}")

            return self._parse_llm_response(result_text, def_type, operation)

        except Exception as e:
            logger.error(f"Error in LLM-based parsing: {e}")
            return self._parse_rule_based(definition, def_type, operation)

    def _parse_rule_based(
        self,
        definition: str,
        def_type: DefinitionType,
        operation: Optional[str]
    ) -> QueryIntent:
        """Parse using rule-based approach."""
        intent = QueryIntent(
            definition=definition,
            query_type=def_type.value,
            operation=operation or "IN"
        )

        # Common English words to exclude from table name extraction
        common_words = {
            "show", "me", "all", "the", "which", "are", "is", "a", "an",
            "and", "or", "not", "be", "have", "has", "do", "does", "did",
            "can", "could", "will", "would", "should", "may", "might",
            "active", "inactive", "status", "where", "that", "this", "these",
            "those", "from", "to", "for", "with", "by", "on", "at", "of",
            "find", "get", "list", "display", "retrieve", "fetch", "select",
            "give", "compare", "difference", "missing", "mismatch", "unmatched",
            "count", "sum", "average", "total", "group", "aggregate", "statistics",
            "in", "products", "product", "data", "records", "items", "entries"
        }

        # Extract table names from known tables in schemas
        potential_tables = []

        if self.schemas_info:
            # Collect all known table names from schemas
            known_tables = []
            for schema_name, schema in self.schemas_info.items():
                if hasattr(schema, 'tables'):
                    for table_name in schema.tables.keys():
                        known_tables.append(table_name)

            # Find which known tables appear in the definition
            definition_lower = definition.lower()
            for table_name in known_tables:
                if table_name.lower() in definition_lower:
                    potential_tables.append(table_name)
                    logger.info(f"Found table in definition: {table_name}")

        # Fallback: Look for capitalized words or quoted strings, but exclude common words
        if not potential_tables:
            words = definition.split()
            for w in words:
                cleaned = w.strip('",')
                if len(cleaned) > 0 and (cleaned[0].isupper() or w.startswith('"')):
                    # Exclude common English words
                    if cleaned.lower() not in common_words:
                        potential_tables.append(cleaned)
            logger.info(f"Fallback table extraction found: {potential_tables}")

        if len(potential_tables) >= 1:
            intent.source_table = potential_tables[0].lower()
            logger.info(f"Set source_table: {intent.source_table}")
        if len(potential_tables) >= 2:
            intent.target_table = potential_tables[1].lower()
            logger.info(f"Set target_table: {intent.target_table}")

        # Extract filters (simple pattern)
        if "active" in definition.lower():
            intent.filters.append({"column": "status", "value": "active"})
        if "inactive" in definition.lower():
            intent.filters.append({"column": "status", "value": "inactive"})

        # Reclassify if we have two tables and IN/NOT_IN operation
        if intent.source_table and intent.target_table and operation in ["IN", "NOT_IN"]:
            logger.info(f"Reclassifying as comparison_query: has 2 tables and operation={operation}")
            intent.query_type = "comparison_query"
            intent.confidence = 0.7
        else:
            intent.confidence = 0.6

        intent.reasoning = "Extracted using rule-based pattern matching"

        logger.info(f"Rule-based parsing result: query_type={intent.query_type}, source={intent.source_table}, target={intent.target_table}, operation={intent.operation}")

        return intent

    def _parse_llm_response(
        self,
        response_text: str,
        def_type: DefinitionType,
        operation: Optional[str]
    ) -> QueryIntent:
        """Parse LLM response."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in LLM response")
                return QueryIntent(
                    definition="",
                    query_type=def_type.value,
                    operation=operation or "IN",
                    confidence=0.5
                )

            data = json.loads(json_match.group())

            intent = QueryIntent(
                definition=data.get("definition", ""),
                query_type=def_type.value,
                source_table=data.get("source_table", "").lower() if data.get("source_table") else None,
                target_table=data.get("target_table", "").lower() if data.get("target_table") else None,
                operation=operation or data.get("operation", "IN"),
                filters=data.get("filters", []),
                confidence=float(data.get("confidence", 0.75)),
                reasoning=data.get("reasoning", "LLM-inferred query intent")
            )

            return intent

        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return QueryIntent(
                definition="",
                query_type=def_type.value,
                operation=operation or "IN",
                confidence=0.5
            )

    def _resolve_table_names(self, intent: QueryIntent) -> QueryIntent:
        """
        Resolve business terms to actual table names.

        Args:
            intent: Query intent with potentially unresolved table names

        Returns:
            Query intent with resolved table names
        """
        if intent.source_table:
            resolved = self.table_mapper.resolve_table_name(intent.source_table)
            if resolved and resolved != intent.source_table:
                logger.info(f"Resolved source table: '{intent.source_table}' → '{resolved}'")
                intent.source_table = resolved
                intent.confidence = min(0.95, intent.confidence + 0.05)

        if intent.target_table:
            resolved = self.table_mapper.resolve_table_name(intent.target_table)
            if resolved and resolved != intent.target_table:
                logger.info(f"Resolved target table: '{intent.target_table}' → '{resolved}'")
                intent.target_table = resolved
                intent.confidence = min(0.95, intent.confidence + 0.05)

        return intent

    def _find_join_columns_from_kg(self, source: str, target: str) -> Optional[List[Tuple[str, str]]]:
        """
        Find join columns using KG relationships.

        Args:
            source: Source table name
            target: Target table name

        Returns:
            List of (source_col, target_col) tuples
        """
        if not self.kg:
            logger.warning("No KG available for join column inference")
            return None

        try:
            logger.info(f"Searching KG for join columns between '{source}' and '{target}'")
            logger.debug(f"KG has {len(self.kg.relationships)} relationships")

            # Query KG for relationships between tables
            for rel in self.kg.relationships:
                source_id = rel.source_id.lower() if rel.source_id else ""
                target_id = rel.target_id.lower() if rel.target_id else ""

                if (source_id == source.lower() and target_id == target.lower()) or \
                   (source_id == target.lower() and target_id == source.lower()):

                    logger.debug(f"Found matching relationship: {rel.source_id} → {rel.target_id} (type: {rel.relationship_type})")
                    logger.debug(f"Relationship properties: {rel.properties}")

                    # Extract column names from relationship properties
                    source_col = rel.properties.get("source_column") if rel.properties else None
                    target_col = rel.properties.get("target_column") if rel.properties else None

                    if source_col and target_col:
                        logger.info(f"✓ Found join columns from KG: {source_col} ←→ {target_col}")
                        return [(source_col, target_col)]
                    else:
                        logger.warning(f"Relationship found but missing columns: source_column={source_col}, target_column={target_col}")

            logger.warning(f"No join columns found in KG for {source} ←→ {target}")
            logger.info("Attempting to infer join columns from schema...")

            # Fallback: Try to infer from schema
            inferred_cols = self._infer_join_columns_from_schema(source, target)
            if inferred_cols:
                logger.info(f"✓ Inferred join columns from schema: {inferred_cols}")
                return inferred_cols

            return None

        except Exception as e:
            logger.error(f"Error finding join columns from KG: {e}")
            return None

    def _infer_join_columns_from_schema(self, source: str, target: str) -> Optional[List[Tuple[str, str]]]:
        """
        Infer join columns by looking for matching column names in schemas.

        Args:
            source: Source table name
            target: Target table name

        Returns:
            List of (source_col, target_col) tuples
        """
        if not self.schemas_info:
            return None

        try:
            source_cols = []
            target_cols = []

            # Find columns in source and target tables
            for schema_name, schema in self.schemas_info.items():
                if hasattr(schema, 'tables') and schema.tables:
                    for table_name, table in schema.tables.items():
                        if table_name.lower() == source.lower():
                            source_cols = [col.name for col in table.columns] if hasattr(table, 'columns') else []
                        elif table_name.lower() == target.lower():
                            target_cols = [col.name for col in table.columns] if hasattr(table, 'columns') else []

            if not source_cols or not target_cols:
                logger.debug(f"Could not find columns for {source} or {target}")
                return None

            # Look for matching column names (case-insensitive)
            source_cols_lower = {col.lower(): col for col in source_cols}
            target_cols_lower = {col.lower(): col for col in target_cols}

            # Find exact matches
            matching_cols = []
            for src_col_lower, src_col in source_cols_lower.items():
                if src_col_lower in target_cols_lower:
                    matching_cols.append((src_col, target_cols_lower[src_col_lower]))

            if matching_cols:
                logger.info(f"Found {len(matching_cols)} matching column(s)")
                return matching_cols

            # Look for common ID patterns
            id_patterns = ['_id', '_uid', '_key', '_code', 'id', 'uid', 'code', 'key']
            for src_col_lower, src_col in source_cols_lower.items():
                if any(pattern in src_col_lower for pattern in id_patterns):
                    for tgt_col_lower, tgt_col in target_cols_lower.items():
                        if any(pattern in tgt_col_lower for pattern in id_patterns):
                            # Check if they share a base name
                            src_base = src_col_lower.replace('_id', '').replace('_uid', '').replace('_key', '').replace('_code', '')
                            tgt_base = tgt_col_lower.replace('_id', '').replace('_uid', '').replace('_key', '').replace('_code', '')
                            if src_base and tgt_base and (src_base == tgt_base or src_base in tgt_base or tgt_base in src_base):
                                logger.info(f"Found potential ID match: {src_col} ←→ {tgt_col}")
                                return [(src_col, tgt_col)]

            return None

        except Exception as e:
            logger.error(f"Error inferring join columns from schema: {e}")
            return None

    def _build_parsing_prompt(
        self,
        definition: str,
        def_type: DefinitionType,
        operation: Optional[str]
    ) -> str:
        """Build prompt for LLM parsing."""
        # Convert schemas_info to JSON-serializable format
        if self.schemas_info:
            schemas_dict = {}
            table_names_list = []
            for schema_name, schema in self.schemas_info.items():
                if hasattr(schema, 'tables'):
                    # Extract table names and columns
                    tables = {}
                    for table_name, table in schema.tables.items():
                        table_names_list.append(table_name)
                        if hasattr(table, 'columns'):
                            columns = [col.name for col in table.columns]
                            tables[table_name] = {"columns": columns}
                        else:
                            tables[table_name] = {"columns": []}
                    schemas_dict[schema_name] = {"tables": tables}
                else:
                    schemas_dict[schema_name] = {}
            schemas_str = json.dumps(schemas_dict, indent=2)
            table_names_str = ", ".join(table_names_list)
        else:
            schemas_str = "No schemas provided"
            table_names_str = "No tables available"

        # Build list of common English words to exclude
        common_words = [
            "show", "me", "all", "the", "which", "are", "in", "is", "a", "an",
            "and", "or", "not", "be", "have", "has", "do", "does", "did",
            "can", "could", "will", "would", "should", "may", "might",
            "active", "inactive", "status", "where", "that", "this", "these",
            "those", "from", "to", "for", "with", "by", "on", "at", "of",
            "find", "get", "list", "display", "retrieve", "fetch", "select",
            "give", "compare", "difference", "missing", "mismatch", "unmatched",
            "count", "sum", "average", "total", "group", "aggregate", "statistics"
        ]
        common_words_str = ", ".join(common_words)

        return f"""You are an expert data analyst. Parse this natural language query and extract table names and filters.

QUERY: "{definition}"

IMPORTANT RULES:
1. ONLY extract table names from this list: {table_names_str}
2. NEVER treat common English words as table names. Exclude: {common_words_str}
3. Look for business terms that might map to table names (e.g., "RBP" → "brz_lnd_RBP_GPU", "OPS Excel" → "brz_lnd_OPS_EXCEL_GPU")
4. Extract filters like "active", "inactive", status conditions, etc.
5. Identify the operation: NOT_IN (not in), IN (in), EQUALS (equals), CONTAINS (contains), AGGREGATE (count/sum/etc)

EXAMPLES:
- Query: "Show me all products in RBP which are not in OPS Excel"
  → source_table: "brz_lnd_RBP_GPU", target_table: "brz_lnd_OPS_EXCEL_GPU", operation: "NOT_IN", filters: []

- Query: "Show me all active products in RBP GPU"
  → source_table: "brz_lnd_RBP_GPU", target_table: null, operation: "IN", filters: [{{"column": "status", "value": "active"}}]

- Query: "Show me products in RBP which are in active OPS Excel"
  → source_table: "brz_lnd_RBP_GPU", target_table: "brz_lnd_OPS_EXCEL_GPU", operation: "IN", filters: [{{"column": "status", "value": "active"}}]

Definition Type: {def_type.value}
Operation Type: {operation or "Unknown"}

Available schemas and tables:
{schemas_str}

Extract and return ONLY valid JSON with this structure (no other text):
{{
    "definition": "original definition",
    "source_table": "table_name from the list above",
    "target_table": "table_name from the list above or null",
    "operation": "NOT_IN|IN|EQUALS|CONTAINS|AGGREGATE",
    "filters": [
        {{"column": "column_name", "value": "value"}},
        ...
    ],
    "confidence": 0.85,
    "reasoning": "Why this parsing makes sense"
}}"""


def get_nl_query_parser(
    kg: Optional[KnowledgeGraph] = None,
    schemas_info: Optional[Dict] = None
) -> NLQueryParser:
    """Get or create NL query parser instance."""
    return NLQueryParser(kg, schemas_info)

