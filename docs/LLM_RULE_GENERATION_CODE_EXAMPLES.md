# LLM Rule Generation - Code Examples

## 🔍 Main Entry Point

### How to Generate Rules

```python
from kg_builder.services.reconciliation_service import get_reconciliation_service

# Get the service
recon_service = get_reconciliation_service()

# Generate rules from knowledge graph
ruleset = recon_service.generate_from_knowledge_graph(
    kg_name="kg_20251024_005324",
    schema_names=["orderMgmt-catalog", "qinspect-designcode"],
    use_llm=True,                    # Enable LLM-based rules
    min_confidence=0.7               # Filter rules with confidence ≥ 0.7
)

# Result
print(f"Generated {len(ruleset.rules)} rules")
print(f"Ruleset ID: {ruleset.ruleset_id}")
```

---

## 📊 Step 1: Load Schemas

```python
def _load_schemas(self, schema_names: List[str]) -> Dict[str, DatabaseSchema]:
    """Load schema information from JSON files."""
    schemas_info = {}
    
    for schema_name in schema_names:
        # Load from: schemas/{schema_name}.json
        schema_file = f"schemas/{schema_name}.json"
        
        with open(schema_file, 'r') as f:
            schema_data = json.load(f)
        
        # Parse into DatabaseSchema object
        schema = DatabaseSchema(
            name=schema_name,
            database=schema_data['database'],
            tables={...}  # Parse tables and columns
        )
        
        schemas_info[schema_name] = schema
    
    return schemas_info
```

**Output Example:**
```python
{
    "orderMgmt-catalog": DatabaseSchema(
        name="orderMgmt-catalog",
        database="mysql+mysqlconnector://...",
        tables={
            "catalog": Table(
                columns=[
                    Column(name="id", type="INT"),
                    Column(name="code", type="VARCHAR"),
                    Column(name="name", type="VARCHAR")
                ]
            )
        }
    ),
    "qinspect-designcode": DatabaseSchema(...)
}
```

---

## 🔗 Step 2: Query Knowledge Graph

```python
def _get_kg_relationships(self, kg_name: str) -> List[Dict[str, Any]]:
    """Query knowledge graph for relationships."""
    try:
        # Connect to FalkorDB
        kg_backend = FalkorDBBackend()
        
        # Query relationships
        query = """
        MATCH (source)-[rel]->(target)
        RETURN source, rel, target
        """
        
        relationships = kg_backend.query(query)
        
        return relationships
    
    except Exception as e:
        logger.warning(f"Failed to query KG: {e}")
        return []
```

**Output Example:**
```python
[
    {
        "source_table": "catalog",
        "target_table": "design_code_master",
        "relationship_type": "MATCHES",
        "confidence": 0.85
    }
]
```

---

## 🎯 Step 3: Generate Pattern-Based Rules

```python
def _generate_pattern_based_rules(
    self,
    relationships: List[Dict[str, Any]],
    schemas_info: Dict[str, DatabaseSchema]
) -> List[ReconciliationRule]:
    """Generate rules by matching column names."""
    
    rules = []
    
    # Get all schemas
    schema_names = list(schemas_info.keys())
    
    # Compare schemas pairwise
    for i, schema1_name in enumerate(schema_names):
        for schema2_name in schema_names[i+1:]:
            schema1 = schemas_info[schema1_name]
            schema2 = schemas_info[schema2_name]
            
            # Compare tables
            for table1_name, table1 in schema1.tables.items():
                for table2_name, table2 in schema2.tables.items():
                    
                    # Compare columns
                    for col1 in table1.columns:
                        for col2 in table2.columns:
                            
                            # If column names match
                            if col1.name == col2.name:
                                rule = ReconciliationRule(
                                    rule_id=f"RULE_{generate_uid()}",
                                    rule_name=f"Match_{table1_name}_{col1.name}",
                                    source_schema=schema1_name,
                                    source_table=table1_name,
                                    source_columns=[col1.name],
                                    target_schema=schema2_name,
                                    target_table=table2_name,
                                    target_columns=[col2.name],
                                    match_type="exact",
                                    confidence_score=0.75,
                                    reasoning=f"Column names match: {col1.name}",
                                    llm_generated=False
                                )
                                rules.append(rule)
    
    return rules
```

---

## 🤖 Step 4: Generate LLM-Based Rules

```python
def _generate_llm_rules(
    self,
    relationships: List[Dict[str, Any]],
    schemas_info: Dict[str, DatabaseSchema]
) -> List[ReconciliationRule]:
    """Generate semantic rules using LLM."""
    
    # Get LLM service
    llm_service = get_multi_schema_llm_service()
    
    # Check if enabled
    if not llm_service.is_enabled():
        logger.info("LLM service not enabled")
        return []
    
    # Prepare schemas for LLM
    schemas_dict = SchemaParser._prepare_schemas_info(schemas_info)
    
    # Call LLM to generate rules
    llm_rules_dict = llm_service.generate_reconciliation_rules(
        relationships, 
        schemas_dict
    )
    
    # Convert to ReconciliationRule objects
    rules = []
    for rule_dict in llm_rules_dict:
        rule = ReconciliationRule(
            rule_id=f"RULE_{generate_uid()}",
            rule_name=rule_dict.get('rule_name'),
            source_schema=rule_dict.get('source_schema'),
            source_table=rule_dict.get('source_table'),
            source_columns=rule_dict.get('source_columns'),
            target_schema=rule_dict.get('target_schema'),
            target_table=rule_dict.get('target_table'),
            target_columns=rule_dict.get('target_columns'),
            match_type=rule_dict.get('match_type'),
            confidence_score=rule_dict.get('confidence', 0.7),
            reasoning=rule_dict.get('reasoning'),
            llm_generated=True
        )
        rules.append(rule)
    
    return rules
```

---

## 🧠 LLM Service - Generate Rules

```python
def generate_reconciliation_rules(
    self,
    relationships: List[Dict[str, Any]],
    schemas_info: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Use LLM to generate reconciliation rules."""
    
    # Build prompt
    prompt = self._build_reconciliation_rules_prompt(
        relationships, 
        schemas_info
    )
    
    # Call OpenAI API
    response = self.client.chat.completions.create(
        model=self.model,                    # gpt-3.5-turbo
        max_tokens=self.max_tokens,          # 2000
        temperature=self.temperature,        # 0.7
        messages=[
            {
                "role": "system",
                "content": "You are an expert data integration specialist. "
                          "Generate reconciliation rules for matching data "
                          "across different database schemas."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    # Parse response
    result_text = response.choices[0].message.content
    rules = self._parse_reconciliation_rules(result_text)
    
    return rules
```

---

## 📝 Build Prompt for LLM

```python
def _build_reconciliation_rules_prompt(
    self,
    relationships: List[Dict[str, Any]],
    schemas_info: Dict[str, Any]
) -> str:
    """Build prompt for LLM."""
    
    schemas_str = json.dumps(schemas_info, indent=2)
    relationships_str = json.dumps(relationships, indent=2)
    
    prompt = f"""Given these cross-schema relationships and schemas, 
generate reconciliation rules that would allow matching records 
between these schemas.

SCHEMAS:
{schemas_str}

RELATIONSHIPS:
{relationships_str}

For each rule, provide:
1. rule_name: Descriptive name
2. source_table: Source table name
3. source_columns: List of source columns
4. target_table: Target table name
5. target_columns: List of target columns
6. match_type: exact, fuzzy, semantic, or pattern
7. confidence: 0.0 to 1.0
8. reasoning: Why this rule works

Return as JSON array of rules."""
    
    return prompt
```

---

## 🔄 Parse LLM Response

```python
def _parse_reconciliation_rules(
    self, 
    response_text: str
) -> List[Dict[str, Any]]:
    """Parse rules from LLM response."""
    
    try:
        # Extract JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        json_str = response_text[json_start:json_end]
        
        # Parse JSON
        data = json.loads(json_str)
        
        # Extract rules
        rules = []
        for rule in data.get('rules', []):
            rules.append({
                'rule_name': rule.get('rule_name'),
                'source_table': rule.get('source_table'),
                'source_columns': rule.get('source_columns'),
                'target_table': rule.get('target_table'),
                'target_columns': rule.get('target_columns'),
                'match_type': rule.get('match_type'),
                'confidence': rule.get('confidence', 0.7),
                'reasoning': rule.get('reasoning')
            })
        
        return rules
    
    except Exception as e:
        logger.error(f"Error parsing rules: {e}")
        return []
```

---

## 📊 Final Ruleset Creation

```python
def generate_from_knowledge_graph(
    self,
    kg_name: str,
    schema_names: List[str],
    use_llm: bool = True,
    min_confidence: float = 0.7
) -> ReconciliationRuleSet:
    """Main entry point for rule generation."""
    
    # 1. Load schemas
    schemas_info = self._load_schemas(schema_names)
    
    # 2. Query KG
    relationships = self._get_kg_relationships(kg_name)
    
    # 3. Generate pattern-based rules
    basic_rules = self._generate_pattern_based_rules(
        relationships, schemas_info, schema_names
    )
    
    # 4. Generate LLM rules if enabled
    if use_llm:
        llm_rules = self._generate_llm_rules(relationships, schemas_info)
        all_rules = basic_rules + llm_rules
    else:
        all_rules = basic_rules
    
    # 5. Filter by confidence
    filtered_rules = [r for r in all_rules 
                     if r.confidence_score >= min_confidence]
    
    # 6. Remove duplicates
    unique_rules = self._deduplicate_rules(filtered_rules)
    
    # 7. Create ruleset
    ruleset = ReconciliationRuleSet(
        ruleset_id=f"RECON_{generate_uid()}",
        ruleset_name=f"Reconciliation_{kg_name}",
        schemas=schema_names,
        rules=unique_rules,
        created_at=datetime.utcnow(),
        generated_from_kg=kg_name
    )
    
    logger.info(
        f"Generated {len(unique_rules)} rules "
        f"({len(basic_rules)} pattern-based, "
        f"{len(llm_rules) if use_llm else 0} LLM-based)"
    )
    
    return ruleset
```

---

**Version**: 1.0  
**Date**: 2025-10-24  
**Status**: ✅ Complete

