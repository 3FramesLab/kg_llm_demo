# Multi-Table Column Inclusion - Detailed Implementation Guide

## Overview

This guide provides step-by-step implementation details for the multi-table column inclusion feature.

---

## Phase 1: Data Model Extensions

### Step 1.1: Add AdditionalColumn Dataclass

**File**: `kg_builder/models.py`

Add after the `QueryIntent` class:

```python
from dataclasses import dataclass, field

@dataclass
class AdditionalColumn:
    """Requested column from related table."""
    column_name: str
    source_table: str
    alias: Optional[str] = None
    confidence: float = 0.0
    join_path: Optional[List[Tuple[str, str, Tuple[str, str]]]] = None
    
    def __post_init__(self):
        """Auto-generate alias if not provided."""
        if not self.alias:
            # Format: {table_name}_{column_name}
            table_short = self.source_table.split('_')[-1].lower()
            self.alias = f"{table_short}_{self.column_name.lower()}"
```

### Step 1.2: Extend QueryIntent

**File**: `kg_builder/models.py`

Update the `QueryIntent` dataclass:

```python
@dataclass
class QueryIntent:
    """Parsed intent from NL definition."""
    definition: str
    query_type: str
    source_table: Optional[str] = None
    target_table: Optional[str] = None
    operation: Optional[str] = None
    filters: List[Dict[str, Any]] = None
    join_columns: Optional[List[Tuple[str, str]]] = None
    confidence: float = 0.75
    reasoning: str = ""
    
    # NEW: Additional columns from related tables
    additional_columns: List[AdditionalColumn] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize default values."""
        if self.filters is None:
            self.filters = []
        if self.join_columns is None:
            self.join_columns = []
        if self.additional_columns is None:
            self.additional_columns = []
```

---

## Phase 2: NL Query Parser Enhancement

### Step 2.1: Add LLM Prompt for "Include" Clauses

**File**: `kg_builder/services/nl_query_parser.py`

Add new method to `NLQueryParser` class:

```python
def _extract_additional_columns_prompt(self, definition: str) -> str:
    """Build LLM prompt to extract 'include' clauses."""
    return f"""
=== TASK ===
Extract all "include column from table" clauses from the query definition.

=== DEFINITION ===
{definition}

=== INSTRUCTIONS ===
1. Look for patterns like:
   - "include X from Y"
   - "add X column from Y"
   - "also show X from Y"
   - "with X from Y"
   - "plus X from Y"

2. For each match, extract:
   - column_name: The column being requested
   - source_table: The table it comes from (business term or actual name)

3. Return JSON array:
[
  {{
    "column_name": "planner",
    "source_table": "HANA Master"
  }},
  {{
    "column_name": "category",
    "source_table": "Product Master"
  }}
]

4. If no "include" clauses found, return empty array: []

=== RESPONSE ===
Return ONLY valid JSON, no other text.
"""

def _extract_additional_columns(self, definition: str) -> List[Dict[str, str]]:
    """Extract additional column requests from definition."""
    if not self.llm_service.is_enabled():
        return []
    
    try:
        prompt = self._extract_additional_columns_prompt(definition)
        response = self.llm_service.call_llm(prompt)
        
        # Parse JSON response
        import json
        import re
        
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            columns = json.loads(json_match.group())
            logger.info(f"✓ Extracted {len(columns)} additional column requests")
            return columns
        
        return []
    
    except Exception as e:
        logger.warning(f"Failed to extract additional columns: {e}")
        return []
```

### Step 2.2: Add Column Validation

**File**: `kg_builder/services/nl_query_parser.py`

Add new method:

```python
def _validate_additional_columns(
    self, 
    columns: List[Dict[str, str]]
) -> Tuple[List[AdditionalColumn], List[str]]:
    """
    Validate that requested columns exist in schemas.
    
    Returns:
        Tuple of (valid_columns, error_messages)
    """
    valid_columns = []
    errors = []
    
    for col_req in columns:
        col_name = col_req.get("column_name")
        table_name = col_req.get("source_table")
        
        if not col_name or not table_name:
            errors.append(f"Invalid column request: {col_req}")
            continue
        
        # Resolve table name
        resolved_table = self.table_mapper.resolve_table_name(table_name)
        if not resolved_table:
            errors.append(f"Table '{table_name}' not found in schema")
            continue
        
        # Check if column exists in table
        if not self._column_exists_in_table(resolved_table, col_name):
            errors.append(
                f"Column '{col_name}' not found in table '{resolved_table}'"
            )
            continue
        
        # Create AdditionalColumn object
        valid_columns.append(AdditionalColumn(
            column_name=col_name,
            source_table=resolved_table
        ))
    
    return valid_columns, errors

def _column_exists_in_table(self, table_name: str, column_name: str) -> bool:
    """Check if column exists in table schema."""
    if not self.schemas_info:
        return True  # Can't validate without schemas_info
    
    for schema_name, schema in self.schemas_info.items():
        if hasattr(schema, 'tables'):
            for tbl_name, table in schema.tables.items():
                if tbl_name.lower() == table_name.lower():
                    if hasattr(table, 'columns'):
                        col_names = [col.name.lower() for col in table.columns]
                        return column_name.lower() in col_names
    
    return False
```

### Step 2.3: Integrate into Parse Method

**File**: `kg_builder/services/nl_query_parser.py`

Update the `parse` method:

```python
def parse(self, definition: str, use_llm: bool = True) -> QueryIntent:
    """Parse definition into query intent."""
    logger.info(f"Parsing definition: {definition}")
    
    # ... existing code ...
    
    # NEW: Extract additional columns
    if use_llm and self.llm_service.is_enabled():
        col_requests = self._extract_additional_columns(definition)
        valid_cols, errors = self._validate_additional_columns(col_requests)
        
        if errors:
            logger.warning(f"Column validation errors: {errors}")
            # Log but don't fail - continue with valid columns
        
        if valid_cols:
            # Resolve join paths for each column
            intent.additional_columns = self._resolve_join_paths(valid_cols, intent.source_table)
            logger.info(f"✓ Resolved {len(intent.additional_columns)} additional columns")
    
    return intent
```

---

## Phase 3: Join Path Discovery

### Step 3.1: Add JoinPath Model

**File**: `kg_builder/models.py`

```python
@dataclass
class JoinPath:
    """Represents a join path between two tables."""
    source_table: str
    target_table: str
    path: List[Tuple[str, str, Tuple[str, str]]]  # [(table1, table2, (col1, col2)), ...]
    confidence: float
    length: int
    
    def score(self) -> float:
        """Calculate composite score for path selection."""
        # 70% confidence, 30% path length
        return (self.confidence * 0.7) + ((1 / self.length) * 0.3)
```

### Step 3.2: Implement Path Finding Algorithm

**File**: `kg_builder/services/nl_query_parser.py`

```python
def _find_join_path_to_table(
    self, 
    source: str, 
    target: str
) -> Optional[JoinPath]:
    """
    Find optimal join path between source and target tables using BFS.
    
    Returns:
        JoinPath with highest composite score
    """
    if not self.kg:
        logger.warning("No KG available for path finding")
        return None
    
    from collections import deque
    
    # BFS to find all paths
    queue = deque([(source, [source], 1.0)])  # (current_table, path, confidence)
    all_paths = []
    visited_at_depth = {}
    
    while queue:
        current, path, conf = queue.popleft()
        
        if current.lower() == target.lower():
            all_paths.append((path, conf))
            continue
        
        # Limit search depth to avoid infinite loops
        if len(path) > 5:
            continue
        
        # Find relationships from current table
        for rel in self.kg.relationships:
            source_id = rel.source_id.lower() if rel.source_id else ""
            target_id = rel.target_id.lower() if rel.target_id else ""
            
            next_table = None
            join_cols = None
            rel_conf = rel.properties.get("llm_confidence", 0.75)
            
            if source_id == f"table_{current.lower()}":
                next_table = target_id.replace("table_", "")
                join_cols = (rel.source_column, rel.target_column)
            elif target_id == f"table_{current.lower()}":
                next_table = source_id.replace("table_", "")
                join_cols = (rel.target_column, rel.source_column)
            
            if next_table and next_table not in [t.lower() for t in path]:
                new_path = path + [next_table]
                new_conf = conf * rel_conf  # Multiply confidences
                queue.append((next_table, new_path, new_conf))
    
    if not all_paths:
        logger.warning(f"No join path found between {source} and {target}")
        return None
    
    # Score and select best path
    best_path = max(
        all_paths,
        key=lambda p: (p[1] * 0.7) + ((1 / len(p[0])) * 0.3)
    )
    
    path_tables, confidence = best_path
    
    logger.info(f"✓ Found join path: {' → '.join(path_tables)}")
    logger.info(f"  Confidence: {confidence:.2f}, Length: {len(path_tables)-1}")
    
    return JoinPath(
        source_table=source,
        target_table=target,
        path=path_tables,
        confidence=confidence,
        length=len(path_tables) - 1
    )

def _resolve_join_paths(
    self, 
    columns: List[AdditionalColumn],
    source_table: str
) -> List[AdditionalColumn]:
    """Resolve join paths for each additional column."""
    resolved = []
    
    for col in columns:
        path = self._find_join_path_to_table(source_table, col.source_table)
        
        if path:
            col.confidence = path.confidence
            col.join_path = path.path
            resolved.append(col)
        else:
            logger.warning(
                f"Could not find join path for column '{col.column_name}' "
                f"from table '{col.source_table}'"
            )
    
    return resolved
```

---

## Phase 4: SQL Generator Updates

### Step 4.1: Update SQL Generation for Additional Columns

**File**: `kg_builder/services/nl_sql_generator.py`

```python
def generate(self, intent: QueryIntent) -> str:
    """Generate SQL from query intent."""
    logger.info(f"🔧 Generating SQL for: {intent.definition}")
    
    # Generate base SQL
    if intent.query_type == "comparison_query":
        sql = self._generate_comparison_query(intent)
    # ... other query types ...
    
    # NEW: Add additional columns if present
    if intent.additional_columns:
        sql = self._add_additional_columns_to_sql(sql, intent)
    
    return sql

def _add_additional_columns_to_sql(
    self, 
    base_sql: str, 
    intent: QueryIntent
) -> str:
    """Add additional columns to SQL query."""
    if not intent.additional_columns:
        return base_sql
    
    # Extract SELECT clause
    select_match = re.search(r'SELECT\s+(.*?)\s+FROM', base_sql, re.IGNORECASE)
    if not select_match:
        logger.warning("Could not parse SELECT clause")
        return base_sql
    
    select_clause = select_match.group(1)
    
    # Add additional columns to SELECT
    additional_cols = []
    for col in intent.additional_columns:
        # Use table alias from join path
        table_alias = self._get_table_alias(col.source_table)
        additional_cols.append(f"{table_alias}.{self._quote_identifier(col.column_name)} AS {col.alias}")
    
    new_select = select_clause + ", " + ", ".join(additional_cols)
    
    # Add JOIN clauses
    join_clauses = self._generate_join_clauses(intent.additional_columns)
    
    # Reconstruct SQL
    new_sql = base_sql.replace(select_clause, new_select)
    new_sql = new_sql.replace("FROM", join_clauses + "\nFROM")
    
    logger.info(f"✓ Added {len(intent.additional_columns)} additional columns")
    return new_sql

def _generate_join_clauses(self, columns: List[AdditionalColumn]) -> str:
    """Generate JOIN clauses for additional columns."""
    joins = []
    
    for col in columns:
        if not col.join_path or len(col.join_path) < 2:
            continue
        
        # Generate JOIN for each step in path
        for i in range(len(col.join_path) - 1):
            table1 = col.join_path[i]
            table2 = col.join_path[i + 1]
            
            # Find relationship in KG to get join columns
            # (Implementation depends on KG structure)
            
            alias1 = self._get_table_alias(table1)
            alias2 = self._get_table_alias(table2)
            
            join = f"LEFT JOIN {self._quote_identifier(table2)} {alias2} ON {alias1}.col1 = {alias2}.col2"
            joins.append(join)
    
    return "\n".join(joins)

def _get_table_alias(self, table_name: str) -> str:
    """Get or create table alias."""
    # Use first letter or abbreviation
    return table_name[0].lower()
```

---

## Phase 5: Error Handling & Validation

### Step 5.1: Add Comprehensive Error Handling

**File**: `kg_builder/services/nl_query_parser.py`

```python
class ColumnInclusionError(Exception):
    """Error during column inclusion processing."""
    pass

def _validate_and_resolve_columns(
    self,
    columns: List[Dict[str, str]],
    source_table: str
) -> Tuple[List[AdditionalColumn], List[str]]:
    """
    Validate and resolve all additional columns.
    
    Returns:
        Tuple of (valid_columns, error_messages)
    """
    valid_columns = []
    errors = []
    
    for col_req in columns:
        try:
            col_name = col_req.get("column_name", "").strip()
            table_name = col_req.get("source_table", "").strip()
            
            if not col_name:
                errors.append("Column name is empty")
                continue
            
            if not table_name:
                errors.append(f"Table name is empty for column '{col_name}'")
                continue
            
            # Resolve table name
            resolved_table = self.table_mapper.resolve_table_name(table_name)
            if not resolved_table:
                errors.append(f"Table '{table_name}' not found in schema")
                continue
            
            # Check column exists
            if not self._column_exists_in_table(resolved_table, col_name):
                errors.append(
                    f"Column '{col_name}' not found in table '{resolved_table}'"
                )
                continue
            
            # Find join path
            path = self._find_join_path_to_table(source_table, resolved_table)
            if not path:
                errors.append(
                    f"No relationship path found between '{source_table}' "
                    f"and '{resolved_table}' for column '{col_name}'"
                )
                continue
            
            # Create valid column
            col = AdditionalColumn(
                column_name=col_name,
                source_table=resolved_table,
                confidence=path.confidence,
                join_path=path.path
            )
            valid_columns.append(col)
        
        except Exception as e:
            errors.append(f"Error processing column request {col_req}: {str(e)}")
    
    return valid_columns, errors
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_additional_columns.py

def test_extract_additional_columns():
    """Test extraction of 'include' clauses."""
    parser = get_nl_query_parser(kg, schemas_info)
    
    definition = "Show products in RBP not in OPS, include planner from HANA"
    columns = parser._extract_additional_columns(definition)
    
    assert len(columns) == 1
    assert columns[0]["column_name"] == "planner"
    assert columns[0]["source_table"] == "HANA"

def test_validate_columns():
    """Test column validation."""
    parser = get_nl_query_parser(kg, schemas_info)
    
    columns = [{"column_name": "planner", "source_table": "hana_material_master"}]
    valid, errors = parser._validate_additional_columns(columns)
    
    assert len(valid) == 1
    assert len(errors) == 0

def test_find_join_path():
    """Test join path finding."""
    parser = get_nl_query_parser(kg, schemas_info)
    
    path = parser._find_join_path_to_table("brz_lnd_RBP_GPU", "hana_material_master")
    
    assert path is not None
    assert path.confidence > 0
    assert len(path.path) >= 2
```

---

## Deployment Checklist

- [ ] Code review completed
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Performance tests completed
- [ ] Documentation updated
- [ ] Feature flag added (optional)
- [ ] Backward compatibility verified
- [ ] Error messages reviewed
- [ ] Logging reviewed
- [ ] Deployed to staging
- [ ] User acceptance testing
- [ ] Deployed to production

