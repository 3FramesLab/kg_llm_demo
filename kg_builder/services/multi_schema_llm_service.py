"""
LLM service for multi-schema relationship analysis and enhancement.
Provides intelligent relationship inference, descriptions, and confidence scoring.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from kg_builder.config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS
)

logger = logging.getLogger(__name__)


class MultiSchemaLLMService:
    """Service for LLM-based multi-schema relationship analysis."""
    
    def __init__(self, use_enhanced_prompts: bool = True):
        """Initialize the LLM service."""
        self.enabled = bool(OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.temperature = OPENAI_TEMPERATURE
        self.max_tokens = OPENAI_MAX_TOKENS
        self.use_enhanced_prompts = use_enhanced_prompts

        if self.enabled:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info(f"MultiSchemaLLMService initialized with model: {self.model}, enhanced_prompts: {use_enhanced_prompts}")
        else:
            logger.warning("MultiSchemaLLMService disabled: OPENAI_API_KEY not set")
    
    def is_enabled(self) -> bool:
        """Check if LLM service is enabled."""
        return self.enabled
    
    def infer_relationships(
        self,
        schemas_info: Dict[str, Any],
        detected_relationships: List[Dict[str, Any]],
        field_preferences: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to infer additional relationships beyond pattern matching.

        Args:
            schemas_info: Information about all schemas
            detected_relationships: Relationships already detected by pattern matching
            field_preferences: User-specific field hints to guide inference

        Returns:
            Enhanced relationships with inferred ones added
        """
        if not self.enabled:
            logger.warning("LLM service disabled, returning original relationships")
            return detected_relationships

        try:
            prompt = self._build_inference_prompt(schemas_info, detected_relationships, field_preferences=field_preferences)

            logger.debug(f"Inference Prompt:\n{prompt}")

            # Filter temperature parameter for GPT-5 compatibility
            api_params = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert database analyst. Analyze database schemas and infer relationships between tables across different schemas based on semantic meaning and naming conventions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Only add temperature if not a GPT-5 model (GPT-5 only supports default temperature=1)
            if not self.model.startswith('gpt-5'):
                api_params["temperature"] = self.temperature

            response = self.client.chat.completions.create(**api_params)

            result_text = response.choices[0].message.content
            logger.debug(f"LLM Inference Response:\n{result_text}")

            inferred = self._parse_inferred_relationships(result_text)

            # Combine detected and inferred relationships
            all_relationships = detected_relationships + inferred

            logger.info(f"LLM inferred {len(inferred)} additional relationships")
            return all_relationships
            
        except Exception as e:
            logger.error(f"Error in relationship inference: {e}")
            return detected_relationships
    
    def enhance_relationships(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to generate meaningful descriptions for relationships.
        
        Args:
            relationships: List of relationships to enhance
            schemas_info: Information about schemas
            
        Returns:
            Relationships with enhanced descriptions
        """
        if not self.enabled:
            logger.warning("LLM service disabled, returning original relationships")
            return relationships
        
        try:
            prompt = self._build_enhancement_prompt(relationships, schemas_info)

            logger.debug(f"Enhancement Prompt:\n{prompt}")

            # Filter temperature parameter for GPT-5 compatibility
            api_params = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert database analyst. Generate clear, concise business descriptions for database relationships."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Only add temperature if not a GPT-5 model (GPT-5 only supports default temperature=1)
            if not self.model.startswith('gpt-5'):
                api_params["temperature"] = self.temperature

            response = self.client.chat.completions.create(**api_params)

            result_text = response.choices[0].message.content
            logger.debug(f"LLM Enhancement Response:\n{result_text}")

            enhanced = self._parse_enhanced_relationships(result_text)

            logger.info(f"LLM enhanced {len(enhanced)} relationships with descriptions")
            return enhanced
            
        except Exception as e:
            logger.error(f"Error in relationship enhancement: {e}")
            return relationships
    
    def score_relationships(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to assess confidence in detected relationships.

        Args:
            relationships: List of relationships to score
            schemas_info: Information about schemas

        Returns:
            Relationships with confidence scores
        """
        if not self.enabled:
            logger.warning("LLM service disabled, returning original relationships")
            return relationships

        try:
            prompt = self._build_scoring_prompt(relationships, schemas_info)

            logger.debug(f"Scoring Prompt:\n{prompt}")

            # Filter temperature parameter for GPT-5 compatibility
            api_params = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert database analyst. Assess the confidence and validity of database relationships."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Only add temperature if not a GPT-5 model (GPT-5 only supports default temperature=1)
            if not self.model.startswith('gpt-5'):
                api_params["temperature"] = self.temperature

            response = self.client.chat.completions.create(**api_params)

            result_text = response.choices[0].message.content
            logger.debug(f"LLM Scoring Response:\n{result_text}")

            scored = self._parse_scored_relationships(result_text)

            logger.info(f"LLM scored {len(scored)} relationships with confidence")
            return scored

        except Exception as e:
            logger.error(f"Error in relationship scoring: {e}")
            return relationships

    def generate_reconciliation_rules(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, Any],
        field_preferences: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to generate reconciliation rules from relationships.

        This method analyzes cross-schema relationships and generates actionable
        reconciliation rules that can be used to match, link, and validate data.

        Args:
            relationships: List of relationships between schemas
            schemas_info: Information about all schemas
            field_preferences: User-specific field preferences for rule generation

        Returns:
            List of reconciliation rules with match strategies and confidence scores
        """
        if not self.enabled:
            logger.warning("LLM service disabled, cannot generate reconciliation rules")
            return []

        try:
            # Determine if this is a single-schema or multi-schema generation
            is_single_schema = isinstance(schemas_info, dict) and len(schemas_info) == 1

            prompt = self._build_reconciliation_rules_prompt(relationships, schemas_info, field_preferences=field_preferences)

            logger.debug(f"Reconciliation Rules Prompt:\n{prompt}")

            # Use a dynamic system instruction that matches single vs multi schema
            system_message = (
                "You are an expert data integration specialist. Generate reconciliation rules for matching data within a single database schema (intra-schema joins). Use the same schema name for both source_schema and target_schema."
                if is_single_schema
                else "You are an expert data integration specialist. Generate reconciliation rules for matching data across different database schemas."
            )

            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            result_text = response.choices[0].message.content
            logger.debug(f"LLM Reconciliation Rules Response:\n{result_text}")

            rules = self._parse_reconciliation_rules(result_text)

            logger.info(f"LLM generated {len(rules)} reconciliation rules")
            return rules

        except Exception as e:
            logger.error(f"Error in reconciliation rule generation: {e}")
            return []
    
    def _get_pref_value(self, pref: Any, key: str, default: Any = None) -> Any:
        """
        Helper to get value from either dict or Pydantic object.

        Args:
            pref: Either a dict or Pydantic FieldPreference object
            key: The key/attribute to retrieve
            default: Default value if key doesn't exist

        Returns:
            The value or default
        """
        if isinstance(pref, dict):
            return pref.get(key, default)
        else:
            # Pydantic object
            return getattr(pref, key, default)

    def _build_inference_prompt(
        self,
        schemas_info: Dict[str, Any],
        detected_relationships: List[Dict[str, Any]],
        field_preferences: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build prompt for relationship inference."""
        schemas_str = json.dumps(schemas_info, indent=2)
        detected_str = json.dumps(detected_relationships, indent=2)

        # Detect if single schema or multiple schemas
        is_single_schema = len(schemas_info) == 1

        # Build field preferences section
        # For single-schema: interpret field_hints as intra-table mappings (table1.field → table2.field)
        # For multi-schema: interpret field_hints as cross-schema mappings (schema1.table.field → schema2.table.field)
        field_preferences_str = ""
        if field_preferences:
            field_preferences_str = "\n\n=== USER-SPECIFIC FIELD PREFERENCES ===\n"
            for pref in field_preferences:
                table_name = self._get_pref_value(pref, 'table_name', 'N/A')
                field_preferences_str += f"\nTable: {table_name}\n"

                priority_fields = self._get_pref_value(pref, 'priority_fields', [])
                if priority_fields:
                    field_preferences_str += f"  ✓ PRIORITY FIELDS (focus on these): {', '.join(priority_fields)}\n"

                exclude_fields = self._get_pref_value(pref, 'exclude_fields', [])
                if exclude_fields:
                    field_preferences_str += f"  ✗ EXCLUDE FIELDS (skip these): {', '.join(exclude_fields)}\n"

                field_hints = self._get_pref_value(pref, 'field_hints', {})
                if field_hints:
                    field_preferences_str += f"  → FIELD HINTS (suggested matches):\n"
                    for source, target in field_hints.items():
                        if is_single_schema:
                            # For single-schema: hints are intra-table mappings
                            field_preferences_str += f"    - {table_name}.{source} → (other_table).{target}\n"
                        else:
                            # For multi-schema: hints are cross-schema mappings
                            field_preferences_str += f"    - {source} → {target}\n"

        schema_context = "within a single database schema (intra-schema)" if is_single_schema else "across different database schemas (cross-schema)"

        return f"""You are a data architect discovering comprehensive relationships between database schemas.

CONTEXT: Analyzing schemas {schema_context}. Find ALL types of relationships beyond simple pattern matching.

SCHEMAS:
{schemas_str}

DETECTED RELATIONSHIPS:
{detected_str}
{field_preferences_str}

TASK: Infer additional {"intra-schema" if is_single_schema else "cross-schema"} relationships (confidence >= 0.7).

=== ENHANCED RELATIONSHIP TYPES ===

**SEMANTIC_REFERENCE**: Different names, same meaning
- Examples: customer_id ↔ client_uid, product_code ↔ item_code
- Look for: Similar business concepts with different naming conventions

**BUSINESS_LOGIC**: Business rule relationships
- Examples: order.product_code ↔ catalog.code, invoice.customer ↔ customer.name
- Look for: Operational dependencies, business process flows

**HIERARCHICAL**: Parent-child relationships
- Examples: category_uid ↔ sub_cat_uid, manager_id ↔ employee_id
- Look for: Organizational structures, taxonomies, nested data

**TEMPORAL**: Time-based relationships
- Examples: created_time ↔ order_date, modified_date ↔ last_updated
- Look for: Audit trails, event sequences, lifecycle tracking

**LOOKUP**: Master data relationships
- Examples: status_code ↔ status_master.code, country_code ↔ countries.iso_code
- Look for: Reference data, code tables, standardized values

**REFERENCES**: Implicit foreign key relationships
- Examples: material_number ↔ materials.number, product_id ↔ products.id
- Look for: ID-like fields without explicit FK constraints

**CONTAINS**: Composition relationships
- Examples: order ↔ order_items, document ↔ document_sections
- Look for: Parent tables that logically contain child records

**BELONGS_TO**: Ownership relationships
- Examples: employee ↔ department, product ↔ category
- Look for: Child entities that belong to parent entities

=== ENHANCED MATCHING CRITERIA ===

**1. Semantic Analysis:**
- Business domain similarity (Material, Product, Item = same concept)
- Functional equivalence (ID, UID, Key, Code = identifiers)
- Contextual meaning (Customer, Client, Account = same entity)

**2. Structural Patterns:**
- Naming conventions: _id, _uid, _key, _code, _number, _ref
- Data type compatibility: NVARCHAR ↔ VARCHAR, BIGINT ↔ INTEGER
- Length compatibility: Similar or compatible field lengths

**3. Business Logic Indicators:**
- Master-detail relationships (master tables ↔ transaction tables)
- Reference data patterns (code tables ↔ operational tables)
- Audit trail patterns (created_by, modified_by, timestamps)

**4. Domain-Specific Patterns:**
- Material/Product hierarchies (Material ↔ Product ↔ SKU ↔ Item)
- Organizational structures (Company ↔ Division ↔ Department)
- Geographic relationships (Country ↔ Region ↔ City)

**5. Cross-Schema Integration:**
- ETL source-target relationships (staging ↔ warehouse ↔ mart)
- System integration points (ERP ↔ CRM ↔ Analytics)
- Data lineage patterns (raw ↔ processed ↔ aggregated)

RULES:
✓ Only use columns that EXIST in schemas above
✓ Verify data type compatibility
✓ Confidence: 0.85+ (exact), 0.7-0.84 (semantic)
✓ PRIORITIZE user priority fields, EXCLUDE excluded fields
✓ Use user field hints as strong suggestions (0.9+ confidence)
✓ Provide clear reasoning

=== BUSINESS CONTEXT ANALYSIS ===
Consider these business scenarios when detecting relationships:

**Manufacturing/Supply Chain Context:**
- Material Master tables contain product specifications
- BOM (Bill of Materials) references materials and components
- Production orders consume materials and produce finished goods
- Quality control tracks material batches and test results
- Vendor tables supply materials to manufacturing processes

**Sales/Customer Context:**
- Customer master data drives sales transactions
- Orders contain multiple line items referencing products
- Pricing tables link products to customer-specific prices
- Shipments fulfill orders and update inventory
- Invoices are generated from completed orders

**Financial Context:**
- Cost centers track departmental expenses
- GL accounts categorize all financial transactions
- Budgets are allocated across cost centers and time periods
- Actuals are compared against budgets for variance analysis

**Organizational Context:**
- Company → Division → Department → Cost Center hierarchy
- Employee assignments to departments and cost centers
- Plant/Location assignments for materials and operations
- Business unit segmentation for reporting and analysis

**ENHANCED DETECTION PRIORITY:**
1. **Explicit Relationships**: Foreign key constraints (highest confidence)
2. **Structural Relationships**: Naming patterns (_id, _uid, _key, _code)
3. **Business Logic Relationships**: Domain-specific connections
4. **Semantic Relationships**: Similar meaning, different names
5. **Hierarchical Relationships**: Parent-child, category structures
6. **Temporal Relationships**: Time-based connections and audit trails

**BIDIRECTIONAL GUIDELINES:**
- **REFERENCES**: bidirectional = false (directional dependency)
- **MATCHES**: bidirectional = true (symmetric equivalence)
- **FOREIGN_KEY**: bidirectional = false (explicit constraint direction)
- **CONTAINS/HAS**: bidirectional = false (hierarchical)
- **BELONGS_TO**: bidirectional = false (hierarchical)
- **SEMANTIC_REFERENCE**: bidirectional = true (same concept)
- **HIERARCHICAL**: bidirectional = false (parent-child)
- **TEMPORAL**: bidirectional = false (time flows one way)
- **LOOKUP**: bidirectional = false (lookup direction)

OUTPUT (JSON ONLY):
{{{{
    "inferred_relationships": [
        {{{{
            "source_table": "table1",
            "target_table": "table2",
            "source_column": "col1",
            "target_column": "col2",
            "relationship_type": "SEMANTIC_REFERENCE",
            "reasoning": "Why this relationship exists",
            "confidence": 0.82,
            "data_type_match": "VARCHAR ↔ VARCHAR"
        }}}}
    ]
}}}}

Return ONLY valid JSON, confidence >= 0.7.
"""

    def _build_enhancement_prompt(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, Any]
    ) -> str:
        """Build prompt for relationship description enhancement."""
        rels_str = json.dumps(relationships, indent=2)
        schemas_str = json.dumps(schemas_info, indent=2)

        return f"""Translate database relationships into clear business language.

SCHEMAS:
{schemas_str}

RELATIONSHIPS:
{rels_str}

TASK: For each relationship, write a 1-2 sentence business description explaining:
- What entities are connected
- Why this relationship exists
- Business impact

GUIDELINES:
- Use business terminology, not technical jargon
- Start with business purpose (e.g., "Tracks which vendor supplies each product")
- Explain cardinality in business terms (e.g., "Each order belongs to one customer")
- Keep concise (1-2 sentences)

OUTPUT (JSON ONLY):
{{{{
    "enhanced_relationships": [
        {{{{
            "source_table": "catalog",
            "target_table": "suppliers",
            "description": "Links products to vendors. Each product is supplied by one vendor, enabling vendor performance tracking.",
            "business_value": "Vendor performance analysis and supply chain optimization"
        }}}}
    ]
}}}}

Return ONLY valid JSON.
"""

    def _build_scoring_prompt(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, Any]
    ) -> str:
        """Build prompt for relationship confidence scoring."""
        rels_str = json.dumps(relationships, indent=2)
        schemas_str = json.dumps(schemas_info, indent=2)

        return f"""Score database relationships for validity and confidence.

SCHEMAS:
{schemas_str}

RELATIONSHIPS:
{rels_str}

TASK: Score each relationship's confidence (0.0-1.0) and validation status.

SCORING CRITERIA:
- 0.90-1.0 (VALID): Exact name match, identical types, clear FK pattern
- 0.75-0.89 (LIKELY): Semantic similarity, compatible types, business logic support
- 0.60-0.74 (UNCERTAIN): Weak similarity, loose compatibility, needs validation
- 0.0-0.59 (QUESTIONABLE): No connection, incompatible types, likely false positive

OUTPUT (JSON ONLY):
{{
    "scored_relationships": [
        {{
            "source_table": "table1",
            "target_table": "table2",
            "source_column": "col1",
            "target_column": "col2",
            "confidence": 0.85,
            "reasoning": "Why this score",
            "validation_status": "LIKELY",
            "risk_factors": ["concerns"],
            "recommendation": "Use/Validate/Reject"
        }}
    ]
}}

Return ONLY valid JSON.
"""

    def _parse_inferred_relationships(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse inferred relationships from LLM response."""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)

            relationships = []
            for rel in data.get('inferred_relationships', []):
                relationships.append({
                    'source_table': rel.get('source_table'),
                    'target_table': rel.get('target_table'),
                    'source_column': rel.get('source_column'),
                    'target_column': rel.get('target_column'),
                    'relationship_type': rel.get('relationship_type'),
                    'reasoning': rel.get('reasoning'),
                    'confidence': rel.get('confidence', 0.0),
                    'data_type_match': rel.get('data_type_match'),
                    'inferred_by_llm': True
                })

            return relationships
        except Exception as e:
            logger.error(f"Error parsing inferred relationships: {e}")
            return []
    
    def _parse_enhanced_relationships(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse enhanced relationships from LLM response."""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            relationships = []
            for rel in data.get('enhanced_relationships', []):
                relationships.append({
                    'source_table': rel.get('source_table'),
                    'target_table': rel.get('target_table'),
                    'description': rel.get('description')
                })
            
            return relationships
        except Exception as e:
            logger.error(f"Error parsing enhanced relationships: {e}")
            return []
    
    def _parse_scored_relationships(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse scored relationships from LLM response."""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)

            relationships = []
            for rel in data.get('scored_relationships', []):
                relationships.append({
                    'source_table': rel.get('source_table'),
                    'target_table': rel.get('target_table'),
                    'source_column': rel.get('source_column'),
                    'target_column': rel.get('target_column'),
                    'confidence': rel.get('confidence', 0.0),
                    'reasoning': rel.get('reasoning'),
                    'validation_status': rel.get('validation_status'),
                    'risk_factors': rel.get('risk_factors', []),
                    'recommendation': rel.get('recommendation')
                })

            return relationships
        except Exception as e:
            logger.error(f"Error parsing scored relationships: {e}")
            return []

    def _build_reconciliation_rules_prompt(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, Any],
        field_preferences: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build prompt for reconciliation rule generation."""
        schemas_str = json.dumps(schemas_info, indent=2)
        relationships_str = json.dumps(relationships, indent=2)

        # Detect if single schema or multiple schemas
        is_single_schema = len(schemas_info) == 1
        schema_list = list(schemas_info.keys())

        # Build field preferences section
        # For single-schema: interpret field_hints as intra-table mappings (table1.field → table2.field)
        # For multi-schema: interpret field_hints as cross-schema mappings (schema1.table.field → schema2.table.field)
        field_preferences_str = ""
        if field_preferences:
            field_preferences_str = "\n\n=== USER-SPECIFIC FIELD PREFERENCES ===\n"
            for pref in field_preferences:
                table_name = self._get_pref_value(pref, 'table_name', 'N/A')
                field_preferences_str += f"\nTable: {table_name}\n"

                priority_fields = self._get_pref_value(pref, 'priority_fields', [])
                if priority_fields:
                    field_preferences_str += f"  ✓ PRIORITY FIELDS (focus on these): {', '.join(priority_fields)}\n"

                exclude_fields = self._get_pref_value(pref, 'exclude_fields', [])
                if exclude_fields:
                    field_preferences_str += f"  ✗ EXCLUDE FIELDS (skip these): {', '.join(exclude_fields)}\n"

                field_hints = self._get_pref_value(pref, 'field_hints', {})
                if field_hints:
                    field_preferences_str += f"  → FIELD HINTS (suggested matches):\n"
                    for source, target in field_hints.items():
                        if is_single_schema:
                            # For single-schema: hints are intra-table mappings
                            # Format: source_field → target_field (both in same schema, different tables)
                            field_preferences_str += f"    - {table_name}.{source} → (other_table).{target}\n"
                        else:
                            # For multi-schema: hints are cross-schema mappings
                            # Format: source_field → target_field (across different schemas)
                            field_preferences_str += f"    - {source} → {target}\n"

                filter_hints = self._get_pref_value(pref, 'filter_hints', None)
                if filter_hints:
                    field_preferences_str += f"  🔍 FILTER CONDITIONS (apply to {table_name}):\n"
                    for column, value in filter_hints.items():
                        field_preferences_str += f"    - {column} = {value!r}\n"

        if is_single_schema:
            objective_text = """Generate actionable reconciliation rules (join/query rules) for connecting tables within the database.

For a SINGLE SCHEMA, generate rules that can be used to:
1. JOIN tables together (referential integrity)
2. Validate foreign key relationships
3. Build complex queries across related tables
4. Check data quality and consistency

IMPORTANT FOR SINGLE-SCHEMA:
- Field hints specify which fields in different tables should be matched
- Example: If hint says "MATERIAL → PLANNING_SKU", find which table has MATERIAL and which has PLANNING_SKU
- Generate rules that JOIN these tables on these field mappings
- Use the SAME schema name for both source_schema and target_schema
"""
            relationship_header = "=== DETECTED INTRA-SCHEMA RELATIONSHIPS ==="
        else:
            objective_text = """Generate actionable reconciliation rules that can be executed as SQL queries to:
1. Find matched records (exist in both source and target)
2. Identify unmatched records (exist in only one system)
3. Detect mismatched records (same key, different values)
4. Enable data quality analysis and synchronization

IMPORTANT FOR MULTI-SCHEMA:
- Field hints specify which fields across different schemas should be matched
- Example: If hint says "MATERIAL → PLANNING_SKU", match MATERIAL in source schema with PLANNING_SKU in target schema
"""
            relationship_header = "=== DETECTED CROSS-SCHEMA RELATIONSHIPS ==="

        return f"""You are a data integration specialist generating reconciliation rules for matching records {"within a single database schema" if is_single_schema else "across different database schemas"}.

=== OBJECTIVE ===
{objective_text}

=== SCHEMAS ===
{schemas_str}

{relationship_header}
{relationships_str}
{field_preferences_str}

=== MATCH TYPES ===
1. exact: Direct column-to-column equality (identical names/types)
2. fuzzy: Approximate string matching (typos, variations)
3. composite: Multi-column matching (composite keys)
4. transformation: Data format conversion needed (dates, timestamps)
5. semantic: Business logic-based matching (indirect relationships)

=== GUIDELINES ===
✓ ONLY use columns that EXIST in schemas above
✓ Verify data type compatibility
✓ Prefer unique identifiers (IDs, UIDs, codes)
✓ Confidence: 0.95-1.0 (exact), 0.85-0.94 (strong), 0.75-0.84 (good), 0.70-0.74 (weak), <0.70 (skip)
✓ PRIORITIZE user priority fields, EXCLUDE excluded fields
✓ Use user field hints as strong suggestions
✓ Apply user filter conditions to appropriate tables in filter_conditions field
✓ Generate 3-10 high-quality rules
{"✓ SINGLE SCHEMA: source_schema = target_schema = '" + schema_list[0] + "'" if is_single_schema else "✓ MULTI-SCHEMA: different source and target schemas"}

=== OUTPUT FORMAT (JSON ONLY) ===
{{
  "rules": [
    {{
      "rule_name": "Descriptive_Name",
      "source_schema": "schema_name",
      "source_table": "table_name",
      "source_columns": ["col1"],
      "target_schema": "schema_name",
      "target_table": "table_name",
      "target_columns": ["col1"],
      "match_type": "exact|fuzzy|composite|transformation|semantic",
      "transformation": null,
      "filter_conditions": {{"Active_Inactive": "Active", "deleted": false}},
      "confidence": 0.85,
      "reasoning": "Why this rule works",
      "validation_status": "VALID|LIKELY|UNCERTAIN",
      "example_match": "Example of matching records",
      "sql_template": "SELECT * FROM table1 t1 JOIN table2 t2 ON t1.col1 = t2.col1 WHERE t1.Active_Inactive = 'Active'"
    }}
  ]
}}

Return ONLY valid JSON, no additional text.
"""

    def _parse_reconciliation_rules(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse reconciliation rules from LLM response."""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)

            rules = []
            for rule in data.get('rules', []):
                rules.append({
                    'rule_name': rule.get('rule_name', ''),
                    'source_schema': rule.get('source_schema', ''),
                    'source_table': rule.get('source_table', ''),
                    'source_columns': rule.get('source_columns', []),
                    'target_schema': rule.get('target_schema', ''),
                    'target_table': rule.get('target_table', ''),
                    'target_columns': rule.get('target_columns', []),
                    'match_type': rule.get('match_type', 'semantic'),
                    'transformation': rule.get('transformation'),
                    'filter_conditions': rule.get('filter_conditions'),  # ✅ Parse filter conditions
                    'confidence': rule.get('confidence', 0.7),
                    'reasoning': rule.get('reasoning', ''),
                    'validation_status': rule.get('validation_status', 'UNCERTAIN'),
                    'example_match': rule.get('example_match', '')
                })

            return rules
        except Exception as e:
            logger.error(f"Error parsing reconciliation rules: {e}")
            logger.debug(f"Response text: {response_text}")
            return []


# Singleton instance
_multi_schema_llm_service = None


def get_multi_schema_llm_service() -> MultiSchemaLLMService:
    """Get or create the multi-schema LLM service singleton."""
    global _multi_schema_llm_service
    if _multi_schema_llm_service is None:
        _multi_schema_llm_service = MultiSchemaLLMService()
    return _multi_schema_llm_service

