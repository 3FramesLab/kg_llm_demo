"""
Natural Language Relationship Parser Service

Parses natural language relationship definitions and converts them to structured
relationship definitions that can be added to the knowledge graph.

Supports multiple input formats:
1. Natural Language: "Products are supplied by Vendors"
2. Semi-Structured: "catalog.product_id → vendor.vendor_id (SUPPLIED_BY)"
3. Pseudo-SQL: "SELECT * FROM products JOIN vendors ON ..."
4. Business Rules: "IF product.status='active' THEN ..."
"""

import json
import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from kg_builder.models import RelationshipDefinition, NLInputFormat
from kg_builder.services.multi_schema_llm_service import get_multi_schema_llm_service

logger = logging.getLogger(__name__)


class NaturalLanguageRelationshipParser:
    """Parse natural language relationship definitions."""

    def __init__(self):
        """Initialize the parser."""
        self.llm_service = get_multi_schema_llm_service()
        self.relationship_verbs = {
            "supplied by": "SUPPLIED_BY",
            "supplies": "SUPPLIES",
            "contains": "CONTAINS",
            "has": "HAS",
            "belongs to": "BELONGS_TO",
            "references": "REFERENCES",
            "places": "PLACES",
            "placed by": "PLACED_BY",
            "sold by": "SOLD_BY",
            "sells": "SELLS",
            "created by": "CREATED_BY",
            "creates": "CREATES",
            "managed by": "MANAGED_BY",
            "manages": "MANAGES",
        }

    def parse(
        self,
        input_text: str,
        schemas_info: Dict[str, Any],
        use_llm: bool = True
    ) -> List[RelationshipDefinition]:
        """
        Parse natural language input and return relationship definitions.

        Args:
            input_text: The input text to parse
            schemas_info: Dictionary with schema information
            use_llm: Whether to use LLM for parsing

        Returns:
            List of parsed relationship definitions
        """
        try:
            # Detect input format
            input_format = self._detect_format(input_text)
            logger.debug(f"Detected input format: {input_format}")

            # Parse based on format
            if input_format == NLInputFormat.NATURAL_LANGUAGE:
                relationships = self._parse_natural_language(input_text, schemas_info, use_llm)
            elif input_format == NLInputFormat.SEMI_STRUCTURED:
                relationships = self._parse_semi_structured(input_text, schemas_info)
            elif input_format == NLInputFormat.PSEUDO_SQL:
                relationships = self._parse_pseudo_sql(input_text, schemas_info)
            elif input_format == NLInputFormat.BUSINESS_RULES:
                relationships = self._parse_business_rules(input_text, schemas_info, use_llm)
            else:
                logger.warning(f"Unknown format: {input_format}")
                return []

            # Validate relationships
            validated_relationships = []
            for rel in relationships:
                is_valid, errors = self._validate_relationship(rel, schemas_info)
                rel.validation_status = "VALID" if is_valid else "INVALID"
                rel.validation_errors = errors
                validated_relationships.append(rel)

            logger.info(f"Parsed {len(validated_relationships)} relationships from input")
            return validated_relationships

        except Exception as e:
            logger.error(f"Error parsing natural language input: {e}")
            return []

    def _detect_format(self, text: str) -> NLInputFormat:
        """Detect the input format."""
        text_lower = text.lower().strip()

        # Check for semi-structured format (contains → or JOIN)
        if "→" in text or "->" in text:
            return NLInputFormat.SEMI_STRUCTURED

        # Check for pseudo-SQL format (contains SELECT or JOIN)
        if text_lower.startswith("select") or " join " in text_lower:
            return NLInputFormat.PSEUDO_SQL

        # Check for business rules format (contains IF/THEN)
        if text_lower.startswith("if ") or " then " in text_lower:
            return NLInputFormat.BUSINESS_RULES

        # Default to natural language
        return NLInputFormat.NATURAL_LANGUAGE

    def _parse_natural_language(
        self,
        text: str,
        schemas_info: Dict[str, Any],
        use_llm: bool = True
    ) -> List[RelationshipDefinition]:
        """Parse natural language using LLM or rule-based approach."""
        if use_llm and self.llm_service.is_enabled():
            return self._parse_nl_with_llm(text, schemas_info)
        else:
            return self._parse_nl_rule_based(text, schemas_info)

    def _parse_nl_with_llm(
        self,
        text: str,
        schemas_info: Dict[str, Any]
    ) -> List[RelationshipDefinition]:
        """Parse natural language using LLM."""
        try:
            prompt = self._build_nl_parsing_prompt(text, schemas_info)
            logger.debug(f"NL Parsing Prompt:\n{prompt}")

            response = self.llm_service.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert data modeler. Parse natural language relationship definitions and extract structured information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.llm_service.max_tokens
            )

            result_text = response.choices[0].message.content
            logger.debug(f"LLM Response:\n{result_text}")

            return self._parse_llm_response(result_text)

        except Exception as e:
            logger.error(f"Error in LLM-based NL parsing: {e}")
            return []

    def _parse_nl_rule_based(
        self,
        text: str,
        schemas_info: Dict[str, Any]
    ) -> List[RelationshipDefinition]:
        """Parse natural language using rule-based approach."""
        relationships = []

        # Extract entities and relationship type
        for verb, rel_type in self.relationship_verbs.items():
            if verb in text.lower():
                # Simple pattern: "Entity1 [verb] Entity2"
                pattern = r"(\w+)\s+" + re.escape(verb) + r"\s+(\w+)"
                matches = re.finditer(pattern, text, re.IGNORECASE)

                for match in matches:
                    source = match.group(1).lower()
                    target = match.group(2).lower()

                    # Find matching tables in schemas
                    source_table = self._find_matching_table(source, schemas_info)
                    target_table = self._find_matching_table(target, schemas_info)

                    if source_table and target_table and source_table != target_table:
                        rel = RelationshipDefinition(
                            source_table=source_table,
                            target_table=target_table,
                            relationship_type=rel_type,
                            properties=[],
                            cardinality="1:N",
                            confidence=0.75,
                            reasoning=f"Extracted from natural language: '{text}'",
                            input_format=NLInputFormat.NATURAL_LANGUAGE
                        )
                        relationships.append(rel)

        return relationships

    def _parse_semi_structured(
        self,
        text: str,
        schemas_info: Dict[str, Any]
    ) -> List[RelationshipDefinition]:
        """Parse semi-structured format: 'table1.col1 → table2.col2 (TYPE)'"""
        relationships = []

        # Pattern: table1.col1 → table2.col2 (RELATIONSHIP_TYPE)
        pattern = r"(\w+)\.(\w+)\s*(?:→|->)\s*(\w+)\.(\w+)\s*\((\w+)\)"
        matches = re.finditer(pattern, text)

        for match in matches:
            source_table = match.group(1).lower()
            source_col = match.group(2).lower()
            target_table = match.group(3).lower()
            target_col = match.group(4).lower()
            rel_type = match.group(5).upper()

            rel = RelationshipDefinition(
                source_table=source_table,
                target_table=target_table,
                relationship_type=rel_type,
                properties=[target_col],
                cardinality="1:N",
                confidence=0.85,
                reasoning=f"Extracted from semi-structured format: {source_table}.{source_col} → {target_table}.{target_col}",
                input_format=NLInputFormat.SEMI_STRUCTURED
            )
            relationships.append(rel)

        return relationships

    def _parse_pseudo_sql(
        self,
        text: str,
        schemas_info: Dict[str, Any]
    ) -> List[RelationshipDefinition]:
        """Parse pseudo-SQL format: 'SELECT * FROM t1 JOIN t2 ON t1.id = t2.id'"""
        relationships = []

        # Pattern: FROM table1 JOIN table2 ON table1.col = table2.col
        pattern = r"FROM\s+(\w+)\s+JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)"
        matches = re.finditer(pattern, text, re.IGNORECASE)

        for match in matches:
            source_table = match.group(1).lower()
            target_table = match.group(2).lower()
            source_col = match.group(4).lower()
            target_col = match.group(6).lower()

            rel = RelationshipDefinition(
                source_table=source_table,
                target_table=target_table,
                relationship_type="REFERENCES",
                properties=[target_col],
                cardinality="1:N",
                confidence=0.80,
                reasoning=f"Extracted from SQL JOIN: {source_table} JOIN {target_table} ON {source_table}.{source_col} = {target_table}.{target_col}",
                input_format=NLInputFormat.PSEUDO_SQL
            )
            relationships.append(rel)

        return relationships

    def _parse_business_rules(
        self,
        text: str,
        schemas_info: Dict[str, Any],
        use_llm: bool = True
    ) -> List[RelationshipDefinition]:
        """Parse business rules format: 'IF condition THEN relationship'"""
        if use_llm and self.llm_service.is_enabled():
            return self._parse_business_rules_with_llm(text, schemas_info)
        else:
            return []

    def _parse_business_rules_with_llm(
        self,
        text: str,
        schemas_info: Dict[str, Any]
    ) -> List[RelationshipDefinition]:
        """Parse business rules using LLM."""
        try:
            prompt = self._build_business_rules_prompt(text, schemas_info)

            response = self.llm_service.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert data modeler. Parse business rules and extract relationships."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.llm_service.max_tokens
            )

            result_text = response.choices[0].message.content
            return self._parse_llm_response(result_text)

        except Exception as e:
            logger.error(f"Error parsing business rules: {e}")
            return []

    def _build_nl_parsing_prompt(self, text: str, schemas_info: Dict[str, Any]) -> str:
        """Build prompt for NL parsing."""
        schemas_str = json.dumps(schemas_info, indent=2)

        return f"""Parse this natural language relationship definition:

"{text}"

Available schemas and tables:
{schemas_str}

Extract and return as JSON array with this structure:
{{
    "relationships": [
        {{
            "source_table": "table_name",
            "target_table": "table_name",
            "relationship_type": "RELATIONSHIP_TYPE",
            "properties": ["prop1", "prop2"],
            "cardinality": "1:N",
            "confidence": 0.85,
            "reasoning": "Why this relationship makes sense"
        }}
    ]
}}

Return ONLY valid JSON, no other text."""

    def _build_business_rules_prompt(self, text: str, schemas_info: Dict[str, Any]) -> str:
        """Build prompt for business rules parsing."""
        schemas_str = json.dumps(schemas_info, indent=2)

        return f"""Parse this business rule and extract relationships:

"{text}"

Available schemas and tables:
{schemas_str}

Extract and return as JSON array with this structure:
{{
    "relationships": [
        {{
            "source_table": "table_name",
            "target_table": "table_name",
            "relationship_type": "RELATIONSHIP_TYPE",
            "properties": [],
            "cardinality": "1:N",
            "confidence": 0.80,
            "reasoning": "How this rule creates a relationship"
        }}
    ]
}}

Return ONLY valid JSON, no other text."""

    def _parse_llm_response(self, response_text: str) -> List[RelationshipDefinition]:
        """Parse LLM response and extract relationships."""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)

            relationships = []
            for rel_dict in data.get('relationships', []):
                rel = RelationshipDefinition(
                    source_table=rel_dict.get('source_table', '').lower(),
                    target_table=rel_dict.get('target_table', '').lower(),
                    relationship_type=rel_dict.get('relationship_type', 'REFERENCES').upper(),
                    properties=rel_dict.get('properties', []),
                    cardinality=rel_dict.get('cardinality', '1:N'),
                    confidence=float(rel_dict.get('confidence', 0.75)),
                    reasoning=rel_dict.get('reasoning', 'LLM-inferred relationship'),
                    input_format=NLInputFormat.NATURAL_LANGUAGE
                )
                relationships.append(rel)

            return relationships

        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return []

    def _validate_relationship(
        self,
        rel: RelationshipDefinition,
        schemas_info: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate parsed relationship against schema."""
        errors = []

        # Check source table exists
        if rel.source_table not in schemas_info:
            errors.append(f"Source table '{rel.source_table}' not found in schemas")

        # Check target table exists
        if rel.target_table not in schemas_info:
            errors.append(f"Target table '{rel.target_table}' not found in schemas")

        # Check properties exist in target table
        if rel.source_table in schemas_info and rel.target_table in schemas_info:
            target_schema = schemas_info[rel.target_table]
            target_columns = target_schema.get('columns', [])

            for prop in rel.properties:
                if prop and prop not in target_columns:
                    errors.append(f"Property '{prop}' not found in target table '{rel.target_table}'")

        # Check relationship type is valid
        valid_types = [
            "FOREIGN_KEY", "REFERENCES", "BELONGS_TO", "SUPPLIED_BY", "SUPPLIES",
            "CONTAINS", "PLACES", "PLACED_BY", "SOLD_BY", "SELLS", "HAS",
            "CREATED_BY", "CREATES", "MANAGED_BY", "MANAGES", "CROSS_SCHEMA_REFERENCE",
            "SEMANTIC_REFERENCE", "BUSINESS_LOGIC"
        ]
        if rel.relationship_type not in valid_types:
            errors.append(f"Invalid relationship type: {rel.relationship_type}")

        return len(errors) == 0, errors

    def _find_matching_table(self, entity_name: str, schemas_info: Dict[str, Any]) -> Optional[str]:
        """Find matching table name in schemas."""
        entity_lower = entity_name.lower()

        # Exact match
        if entity_lower in schemas_info:
            return entity_lower

        # Fuzzy match (contains)
        for table_name in schemas_info.keys():
            if entity_lower in table_name.lower() or table_name.lower() in entity_lower:
                return table_name

        return None


# Singleton instance
_nl_parser_instance: Optional[NaturalLanguageRelationshipParser] = None


def get_nl_relationship_parser() -> NaturalLanguageRelationshipParser:
    """Get or create NL relationship parser instance."""
    global _nl_parser_instance
    if _nl_parser_instance is None:
        _nl_parser_instance = NaturalLanguageRelationshipParser()
    return _nl_parser_instance

