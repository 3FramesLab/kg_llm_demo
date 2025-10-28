# User-Specific Field Suggestions for Rule Generation

## Overview

Yes, it's absolutely possible to suggest **user-specific fields** for rule generation in the LLM prompt! This allows users to:

- ✅ Specify which fields they want to prioritize for matching
- ✅ Exclude certain fields from rule generation
- ✅ Provide hints about field relationships
- ✅ Reduce rule generation time by focusing on relevant fields
- ✅ Improve rule quality by guiding the LLM

---

## Current Architecture

### How Rule Generation Works

```
User Request
    ↓
RuleGenerationRequest (models.py)
    ↓
ReconciliationRuleGenerator.generate_from_knowledge_graph()
    ↓
_generate_llm_rules()
    ↓
MultiSchemaLLMService.generate_reconciliation_rules()
    ↓
_build_reconciliation_rules_prompt()  ← PROMPT BUILDING
    ↓
OpenAI API
    ↓
Parse Response
    ↓
ReconciliationRuleSet
```

### Current Prompt Parameters

**File**: `kg_builder/services/multi_schema_llm_service.py` (lines 428-490)

**Current inputs**:
- `relationships`: List of detected relationships
- `schemas_info`: Full schema information

**Missing**: User-specific field preferences

---

## Solution: Add User-Specific Field Suggestions

### Step 1: Update Data Models

**File**: `kg_builder/models.py`

Add new model for field preferences:

```python
class FieldPreference(BaseModel):
    """User preference for specific fields in rule generation."""
    table_name: str = Field(..., description="Table name")
    priority_fields: List[str] = Field(
        default=[],
        description="Fields to prioritize for matching (high priority)"
    )
    exclude_fields: List[str] = Field(
        default=[],
        description="Fields to exclude from rule generation"
    )
    field_hints: Dict[str, str] = Field(
        default={},
        description="Hints about field relationships (e.g., {'vendor_id': 'supplier_id'})"
    )


class RuleGenerationRequest(BaseModel):
    """Request model for generating reconciliation rules."""
    schema_names: List[str] = Field(..., description="List of schema names to reconcile")
    kg_name: str = Field(..., description="Knowledge graph to use for rule generation")
    use_llm_enhancement: bool = Field(default=True, description="Use LLM for semantic rule generation")
    min_confidence: float = Field(default=0.7, description="Minimum confidence score for rules")
    match_types: List[ReconciliationMatchType] = Field(
        default=[ReconciliationMatchType.EXACT, ReconciliationMatchType.SEMANTIC],
        description="Types of matches to generate"
    )
    # NEW: Add field preferences
    field_preferences: Optional[List[FieldPreference]] = Field(
        default=None,
        description="User-specific field preferences for rule generation"
    )
```

---

### Step 2: Update Reconciliation Service

**File**: `kg_builder/services/reconciliation_service.py`

Update the `generate_from_knowledge_graph()` method:

```python
def generate_from_knowledge_graph(
    self,
    kg_name: str,
    schema_names: List[str],
    use_llm: bool = True,
    min_confidence: float = 0.7,
    field_preferences: Optional[List[Dict[str, Any]]] = None  # NEW
) -> ReconciliationRuleSet:
    """
    Main entry point for rule generation from a knowledge graph.

    Args:
        kg_name: Name of the knowledge graph to analyze
        schema_names: List of schema names involved
        use_llm: Whether to use LLM for semantic rule generation
        min_confidence: Minimum confidence score for rules (0.0-1.0)
        field_preferences: User-specific field preferences  # NEW
    """
    logger.info(f"Generating reconciliation rules from KG '{kg_name}'")

    # 1. Load schemas
    schemas_info = self._load_schemas(schema_names)

    # 2. Query KG for relationships
    relationships = self._get_kg_relationships(kg_name)

    # 3. Generate basic rules from patterns
    basic_rules = self._generate_pattern_based_rules(
        relationships, schemas_info, schema_names
    )

    # 4. Enhance with LLM if enabled
    if use_llm:
        llm_rules = self._generate_llm_rules(
            relationships, 
            schemas_info,
            field_preferences=field_preferences  # NEW
        )
        all_rules = basic_rules + llm_rules
    else:
        all_rules = basic_rules

    # ... rest of the method
```

---

### Step 3: Update LLM Service

**File**: `kg_builder/services/multi_schema_llm_service.py`

Update the `generate_reconciliation_rules()` method:

```python
def generate_reconciliation_rules(
    self,
    relationships: List[Dict[str, Any]],
    schemas_info: Dict[str, Any],
    field_preferences: Optional[List[Dict[str, Any]]] = None  # NEW
) -> List[Dict[str, Any]]:
    """
    Use LLM to generate reconciliation rules from relationships.

    Args:
        relationships: List of relationships between schemas
        schemas_info: Information about all schemas
        field_preferences: User-specific field preferences  # NEW
    """
    if not self.enabled:
        logger.warning("LLM service disabled, cannot generate reconciliation rules")
        return []

    try:
        prompt = self._build_reconciliation_rules_prompt(
            relationships, 
            schemas_info,
            field_preferences=field_preferences  # NEW
        )

        logger.debug(f"Reconciliation Rules Prompt:\n{prompt}")

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert data integration specialist. Generate reconciliation rules for matching data across different database schemas."
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
```

---

### Step 4: Update Prompt Builder

**File**: `kg_builder/services/multi_schema_llm_service.py` (lines 428-490)

Update the `_build_reconciliation_rules_prompt()` method:

```python
def _build_reconciliation_rules_prompt(
    self,
    relationships: List[Dict[str, Any]],
    schemas_info: Dict[str, Any],
    field_preferences: Optional[List[Dict[str, Any]]] = None  # NEW
) -> str:
    """Build prompt for reconciliation rule generation."""
    schemas_str = json.dumps(schemas_info, indent=2)
    relationships_str = json.dumps(relationships, indent=2)

    # NEW: Build field preferences section
    field_preferences_str = ""
    if field_preferences:
        field_preferences_str = "\n\nUSER-SPECIFIC FIELD PREFERENCES:\n"
        for pref in field_preferences:
            field_preferences_str += f"\nTable: {pref.get('table_name', 'N/A')}\n"
            
            if pref.get('priority_fields'):
                field_preferences_str += f"  PRIORITY FIELDS (focus on these): {', '.join(pref['priority_fields'])}\n"
            
            if pref.get('exclude_fields'):
                field_preferences_str += f"  EXCLUDE FIELDS (skip these): {', '.join(pref['exclude_fields'])}\n"
            
            if pref.get('field_hints'):
                field_preferences_str += f"  FIELD HINTS (suggested matches):\n"
                for source, target in pref['field_hints'].items():
                    field_preferences_str += f"    - {source} → {target}\n"

    return f"""Given these cross-schema relationships and schemas, generate reconciliation rules
that would allow matching records between these schemas.

IMPORTANT: Only use columns that ACTUALLY EXIST in the provided schemas below.
Do NOT invent or hallucinate column names. Verify each column exists in the schema before using it.

SCHEMAS:
{schemas_str}

RELATIONSHIPS:
{relationships_str}
{field_preferences_str}

For each rule, provide:
1. rule_name: Descriptive name for the rule
2. source_schema: Name of the source schema (must match schema names above)
3. source_table: Source table name (must exist in source schema)
4. source_columns: Array of source column names (must ALL exist in the table schema)
5. target_schema: Name of the target schema (must match schema names above)
6. target_table: Target table name (must exist in target schema)
7. target_columns: Array of target column names (must ALL exist in the table schema)
8. match_type: One of "exact", "fuzzy", "composite", "transformation", "semantic"
9. transformation: SQL or Python code for data matching (if needed, null otherwise)
10. confidence: Confidence score (0.0-1.0) for this rule
11. reasoning: Why this rule would work
12. validation_status: "VALID", "LIKELY", or "UNCERTAIN"
13. example_match: Sample matching scenario

Return JSON:
{{
  "rules": [
    {{
      "rule_name": "Vendor_UID_Match",
      "source_schema": "orderMgmt",
      "source_table": "catalog",
      "source_columns": ["vendor_uid"],
      "target_schema": "vendorDB",
      "target_table": "suppliers",
      "target_columns": ["supplier_id"],
      "match_type": "exact",
      "transformation": null,
      "confidence": 0.95,
      "reasoning": "Both fields are UIDs representing vendors",
      "validation_status": "VALID",
      "example_match": "vendor_uid='VND123' matches supplier_id='VND123'"
    }}
  ]
}}

CRITICAL RULES:
- Only generate rules with confidence >= 0.7
- Focus on cross-schema relationships
- ONLY use columns that exist in the provided schemas
- Double-check each column name against the schema before including it
- If you cannot find a valid matching column, do not create a rule for it
- PRIORITIZE user-specified priority fields when available
- EXCLUDE user-specified exclude fields from rule generation
- CONSIDER user-provided field hints as strong suggestions"""
```

---

## Usage Example

### API Call with Field Preferences

```bash
curl -X POST http://localhost:8000/api/v1/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
    "kg_name": "demo_reconciliation_kg",
    "use_llm_enhancement": true,
    "min_confidence": 0.7,
    "field_preferences": [
      {
        "table_name": "catalog",
        "priority_fields": ["vendor_uid", "product_id", "design_code"],
        "exclude_fields": ["internal_notes", "temp_field"],
        "field_hints": {
          "vendor_uid": "supplier_id",
          "product_id": "item_id",
          "design_code": "design_id"
        }
      },
      {
        "table_name": "designcode",
        "priority_fields": ["design_id", "design_name"],
        "exclude_fields": ["deprecated_field"],
        "field_hints": {}
      }
    ]
  }'
```

---

## Benefits

✅ **Reduced Rule Count**: Focus on relevant fields only
✅ **Better Quality**: User guidance improves LLM suggestions
✅ **Faster Execution**: Fewer rules to process
✅ **User Control**: Users can guide rule generation
✅ **Flexible**: Optional parameter (backward compatible)

---

## Implementation Effort

- **Models Update**: 10 minutes
- **Service Update**: 10 minutes
- **Prompt Update**: 5 minutes
- **Testing**: 10 minutes
- **Total**: ~35 minutes

---

## Next Steps

1. Update `kg_builder/models.py` with `FieldPreference` model
2. Update `kg_builder/services/reconciliation_service.py`
3. Update `kg_builder/services/multi_schema_llm_service.py`
4. Update API endpoint in `kg_builder/routes.py`
5. Test with field preferences
6. Document in API documentation

