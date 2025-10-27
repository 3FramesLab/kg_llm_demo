# NL Query Generation - Implementation Plan

## Overview

Transform NL definitions from "relationship definitions" to "executable data queries" that leverage the Knowledge Graph.

---

## Phase 1: Definition Classification

### Task 1.1: Create Definition Type Classifier

**File**: `kg_builder/services/nl_query_classifier.py` (NEW)

```python
from enum import Enum
from typing import List, Dict, Any

class DefinitionType(Enum):
    RELATIONSHIP = "relationship"      # "Products are supplied by Vendors"
    DATA_QUERY = "data_query"          # "Show me products not in OPS Excel"
    FILTER_QUERY = "filter_query"      # "Show me active products"
    COMPARISON_QUERY = "comparison"    # "Compare RBP GPU with OPS Excel"
    AGGREGATION_QUERY = "aggregation"  # "Count products by category"

class NLQueryClassifier:
    """Classify NL definitions into different types."""
    
    def classify(self, definition: str) -> DefinitionType:
        """Classify a definition."""
        # Keywords for each type
        relationship_keywords = ["are", "is", "supplied by", "contains", "references"]
        query_keywords = ["show me", "find", "list", "get", "which"]
        filter_keywords = ["active", "inactive", "status", "where"]
        comparison_keywords = ["compare", "difference", "not in", "missing"]
        aggregation_keywords = ["count", "sum", "average", "total"]
        
        text_lower = definition.lower()
        
        if any(kw in text_lower for kw in comparison_keywords):
            return DefinitionType.COMPARISON_QUERY
        elif any(kw in text_lower for kw in aggregation_keywords):
            return DefinitionType.AGGREGATION_QUERY
        elif any(kw in text_lower for kw in query_keywords):
            return DefinitionType.DATA_QUERY
        elif any(kw in text_lower for kw in filter_keywords):
            return DefinitionType.FILTER_QUERY
        else:
            return DefinitionType.RELATIONSHIP
```

---

## Phase 2: Query Intent Parsing

### Task 2.1: Parse Query Intent

**File**: `kg_builder/services/nl_query_parser.py` (NEW)

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class QueryIntent:
    """Parsed intent from NL definition."""
    definition: str
    query_type: DefinitionType
    source_table: str
    target_table: Optional[str]
    operation: str  # "NOT_IN", "IN", "EQUALS", "CONTAINS"
    filters: List[Dict[str, Any]]
    join_columns: Optional[List[tuple]]  # [(source_col, target_col), ...]
    confidence: float

class NLQueryParser:
    """Parse NL definitions into executable query intents."""
    
    def __init__(self, kg: KnowledgeGraph, schemas_info: Dict):
        self.kg = kg
        self.schemas_info = schemas_info
        self.classifier = NLQueryClassifier()
    
    def parse(self, definition: str, use_llm: bool = True) -> QueryIntent:
        """Parse definition into query intent."""
        
        # Step 1: Classify
        def_type = self.classifier.classify(definition)
        
        # Step 2: Extract tables and operation
        if use_llm:
            intent = self._parse_with_llm(definition, def_type)
        else:
            intent = self._parse_rule_based(definition, def_type)
        
        # Step 3: Use KG to find join columns
        if intent.source_table and intent.target_table:
            intent.join_columns = self._find_join_columns_from_kg(
                intent.source_table,
                intent.target_table
            )
        
        return intent
    
    def _find_join_columns_from_kg(self, source: str, target: str) -> List[tuple]:
        """Find join columns using KG relationships."""
        # Query KG for relationships between tables
        for rel in self.kg.relationships:
            if (rel.source_id.lower() == source.lower() and 
                rel.target_id.lower() == target.lower()):
                # Extract column names from relationship properties
                source_col = rel.properties.get('source_column')
                target_col = rel.properties.get('target_column')
                if source_col and target_col:
                    return [(source_col, target_col)]
        
        return []
```

---

## Phase 3: SQL Generation

### Task 3.1: Generate SQL from Query Intent

**File**: `kg_builder/services/nl_sql_generator.py` (NEW)

```python
class NLSQLGenerator:
    """Generate SQL from NL query intents."""
    
    def generate(self, intent: QueryIntent, db_type: str = "mysql") -> str:
        """Generate SQL from query intent."""
        
        if intent.query_type == DefinitionType.COMPARISON_QUERY:
            return self._generate_comparison_query(intent, db_type)
        elif intent.query_type == DefinitionType.DATA_QUERY:
            return self._generate_data_query(intent, db_type)
        elif intent.query_type == DefinitionType.FILTER_QUERY:
            return self._generate_filter_query(intent, db_type)
        else:
            raise ValueError(f"Unsupported query type: {intent.query_type}")
    
    def _generate_comparison_query(self, intent: QueryIntent, db_type: str) -> str:
        """Generate comparison query (set difference, intersection, etc.)"""
        
        source = intent.source_table
        target = intent.target_table
        source_col, target_col = intent.join_columns[0]
        
        if intent.operation == "NOT_IN":
            # Products in source but not in target
            return f"""
            SELECT DISTINCT s.* 
            FROM {source} s
            LEFT JOIN {target} t ON s.{source_col} = t.{target_col}
            WHERE t.{target_col} IS NULL
            """
        
        elif intent.operation == "IN":
            # Products in both source and target
            return f"""
            SELECT DISTINCT s.* 
            FROM {source} s
            INNER JOIN {target} t ON s.{source_col} = t.{target_col}
            """
        
        return ""
    
    def _generate_data_query(self, intent: QueryIntent, db_type: str) -> str:
        """Generate data query with filters."""
        
        source = intent.source_table
        target = intent.target_table
        
        if not target:
            # Single table query
            sql = f"SELECT * FROM {source}"
        else:
            # Multi-table query
            source_col, target_col = intent.join_columns[0]
            sql = f"""
            SELECT DISTINCT s.* 
            FROM {source} s
            INNER JOIN {target} t ON s.{source_col} = t.{target_col}
            """
        
        # Add filters
        if intent.filters:
            where_clauses = []
            for filter_item in intent.filters:
                where_clauses.append(
                    f"{filter_item['column']} = '{filter_item['value']}'"
                )
            sql += " WHERE " + " AND ".join(where_clauses)
        
        return sql
```

---

## Phase 4: Query Execution & Results

### Task 4.1: Execute Queries and Return Results

**File**: `kg_builder/services/nl_query_executor.py` (NEW)

```python
class NLQueryExecutor:
    """Execute NL-generated queries and return results."""
    
    def execute(self, intent: QueryIntent, connection) -> Dict[str, Any]:
        """Execute query and return results."""
        
        generator = NLSQLGenerator()
        sql = generator.generate(intent)
        
        # Execute query
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        return {
            "definition": intent.definition,
            "query_type": intent.query_type.value,
            "sql": sql,
            "record_count": len(rows),
            "records": rows,
            "join_columns": intent.join_columns,
            "confidence": intent.confidence
        }
```

---

## Phase 5: API Integration

### Task 5.1: Update API Endpoint

**File**: `kg_builder/routes.py`

```python
@router.post("/kg/nl-queries/execute")
async def execute_nl_queries(request: NLQueryExecutionRequest):
    """
    Execute NL definitions as data queries.
    
    Each definition generates a separate query and returns results.
    """
    
    # Load KG
    kg = get_knowledge_graph(request.kg_name)
    
    # Parse each definition
    parser = NLQueryParser(kg, schemas_info)
    executor = NLQueryExecutor()
    
    results = []
    for definition in request.definitions:
        try:
            # Parse
            intent = parser.parse(definition, use_llm=request.use_llm)
            
            # Execute
            result = executor.execute(intent, connection)
            results.append(result)
        
        except Exception as e:
            results.append({
                "definition": definition,
                "error": str(e)
            })
    
    return {
        "kg_name": request.kg_name,
        "total_definitions": len(request.definitions),
        "successful": len([r for r in results if "error" not in r]),
        "results": results
    }
```

---

## Implementation Order

1. **Week 1**: Classification & Intent Parsing
   - Create classifier
   - Create parser
   - Test with examples

2. **Week 2**: SQL Generation
   - Create SQL generator
   - Support all query types
   - Test SQL generation

3. **Week 3**: Execution & Integration
   - Create executor
   - Update API endpoint
   - End-to-end testing

4. **Week 4**: Optimization & Documentation
   - Performance tuning
   - Error handling
   - Documentation

---

## Testing Strategy

### Test Cases

```python
# Test 1: Set Difference Query
definition = "Show me all products in RBP GPU which are not in OPS Excel"
expected_sql = "SELECT ... LEFT JOIN ... WHERE IS NULL"

# Test 2: Set Intersection Query
definition = "Show me all products in RBP GPU which are in OPS Excel"
expected_sql = "SELECT ... INNER JOIN ..."

# Test 3: Filtered Query
definition = "Show me all products in RBP GPU which are in active OPS Excel"
expected_sql = "SELECT ... INNER JOIN ... WHERE status = 'active'"

# Test 4: Multi-table Query
definition = "Show me products from RBP GPU that match OPS Excel and are in SKU LIFNR"
expected_sql = "SELECT ... JOIN ... JOIN ..."
```

---

## Success Criteria

- ✅ Each definition generates separate SQL query
- ✅ KG relationships used to infer join columns
- ✅ Queries execute and return actual data
- ✅ Support set operations (difference, intersection)
- ✅ Support filtered queries
- ✅ Support multi-table queries
- ✅ Confidence scores for each query
- ✅ Error handling and reporting


