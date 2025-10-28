# Excluded Fields Bug: Not Filtering All Relationships

## Problem Statement

**Issue:** Excluded fields are NOT being properly filtered during KG creation. Some relationships with excluded fields are still appearing in the Knowledge Graph.

**Root Cause:** The filtering logic only checks `rel.properties` but NOT the direct `rel.source_column` and `rel.target_column` fields.

---

## Current Implementation (BUGGY)

**File:** `kg_builder/routes.py:250-282`

```python
# Final step: Filter ALL relationships in KG to remove excluded fields
if request.excluded_fields:
    excluded_fields_set = set(request.excluded_fields)
    logger.info(f"Applying final filter to remove relationships with excluded fields: {len(excluded_fields_set)} fields")

    from kg_builder.services.schema_parser import is_excluded_field

    original_count = len(kg.relationships)
    filtered_relationships = []

    for rel in kg.relationships:
        # Check if relationship has column properties
        if rel.properties:
            source_col = rel.properties.get("source_column")
            target_col = rel.properties.get("target_column")

            if source_col and target_col:
                # Check if either column is excluded
                if is_excluded_field(source_col, excluded_fields_set) or is_excluded_field(target_col, excluded_fields_set):
                    logger.debug(f"⛔ Removing relationship from KG (excluded field): {rel.source_id} ({source_col}) → {rel.target_id} ({target_col})")
                    continue  # Skip this relationship

        # Keep this relationship
        filtered_relationships.append(rel)

    kg.relationships = filtered_relationships
```

---

## The Bug Explained

The `GraphRelationship` model stores column names in **TWO places**:

**File:** `kg_builder/models.py:89-96`
```python
class GraphRelationship(BaseModel):
    """Represents a relationship between nodes."""
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = {}
    source_column: Optional[str] = None  # ❌ NOT CHECKED!
    target_column: Optional[str] = None  # ❌ NOT CHECKED!
```

### Where Columns Can Be Stored:

1. **Direct fields (NEW):**
   - `rel.source_column = "Material"`
   - `rel.target_column = "PLANNING_SKU"`

2. **Properties dict (OLD):**
   - `rel.properties = {"source_column": "Material", "target_column": "PLANNING_SKU"}`

### Current Filter Logic:
```python
# ❌ ONLY checks properties dict
if rel.properties:
    source_col = rel.properties.get("source_column")
    target_col = rel.properties.get("target_column")
    # ... check excluded fields
```

**Result:** If a relationship stores columns in **direct fields** (`rel.source_column`), they are **NOT filtered** even if they're in the excluded list!

---

## Example: Bug in Action

### Scenario:
```
Excluded Fields: ["Product_Line", "Business_Unit"]

Relationship 1 (from explicit pairs):
  source_id: "table_brz_lnd_RBP_GPU"
  target_id: "table_brz_lnd_OPS_EXCEL_GPU"
  source_column: "Product_Line"  # ← Stored in DIRECT field
  target_column: "Product_Line"
  properties: {}

Relationship 2 (from LLM):
  source_id: "table_brz_lnd_RBP_GPU"
  target_id: "table_brz_lnd_OPS_EXCEL_GPU"
  source_column: None
  target_column: None
  properties: {
    "source_column": "Business_Unit",  # ← Stored in PROPERTIES
    "target_column": "Business_Unit"
  }
```

### Current Filter Behavior:
```
✅ Relationship 2 REMOVED (found in properties dict)
❌ Relationship 1 KEPT (direct fields not checked!)
```

**Result:** Relationship 1 with excluded field "Product_Line" stays in the KG!

---

## The Fix

### Corrected Code (check BOTH locations):

```python
# Final step: Filter ALL relationships in KG to remove excluded fields
if request.excluded_fields:
    excluded_fields_set = set(request.excluded_fields)
    logger.info(f"Applying final filter to remove relationships with excluded fields: {len(excluded_fields_set)} fields")

    from kg_builder.services.schema_parser import is_excluded_field

    original_count = len(kg.relationships)
    filtered_relationships = []

    for rel in kg.relationships:
        # Check BOTH direct fields AND properties dict
        source_col = rel.source_column or (rel.properties.get("source_column") if rel.properties else None)
        target_col = rel.target_column or (rel.properties.get("target_column") if rel.properties else None)

        if source_col and target_col:
            # Check if either column is excluded
            if is_excluded_field(source_col, excluded_fields_set) or is_excluded_field(target_col, excluded_fields_set):
                logger.debug(f"⛔ Removing relationship from KG (excluded field): {rel.source_id} ({source_col}) → {rel.target_id} ({target_col})")
                continue  # Skip this relationship

        # Keep this relationship
        filtered_relationships.append(rel)

    kg.relationships = filtered_relationships
    removed_count = original_count - len(filtered_relationships)

    if removed_count > 0:
        logger.info(f"✓ Filtered KG relationships: {original_count} → {len(filtered_relationships)} (removed {removed_count} with excluded fields)")
    else:
        logger.info(f"✓ No relationships removed by exclusion filter")
```

---

## Key Changes

### Before (Buggy):
```python
if rel.properties:
    source_col = rel.properties.get("source_column")
    target_col = rel.properties.get("target_column")
```

### After (Fixed):
```python
# Check BOTH direct fields AND properties dict
source_col = rel.source_column or (rel.properties.get("source_column") if rel.properties else None)
target_col = rel.target_column or (rel.properties.get("target_column") if rel.properties else None)
```

**Priority:** Direct fields take precedence (checked with `or` operator)

---

## Testing the Fix

### Test Case 1: Direct Fields
```python
rel = GraphRelationship(
    source_id="table_A",
    target_id="table_B",
    source_column="Product_Line",  # Excluded field
    target_column="Product_Line",
    relationship_type="MATCHES"
)

# Expected: Should be REMOVED
```

### Test Case 2: Properties Dict
```python
rel = GraphRelationship(
    source_id="table_A",
    target_id="table_B",
    relationship_type="MATCHES",
    properties={
        "source_column": "Business_Unit",  # Excluded field
        "target_column": "Business_Unit"
    }
)

# Expected: Should be REMOVED
```

### Test Case 3: Non-Excluded Field
```python
rel = GraphRelationship(
    source_id="table_A",
    target_id="table_B",
    source_column="Material",  # NOT excluded
    target_column="PLANNING_SKU",
    relationship_type="MATCHES"
)

# Expected: Should be KEPT
```

### Test Case 4: Mixed Storage (Direct + Properties)
```python
rel = GraphRelationship(
    source_id="table_A",
    target_id="table_B",
    source_column="Material",  # Direct field (priority)
    target_column="PLANNING_SKU",
    relationship_type="MATCHES",
    properties={
        "source_column": "Product_Line",  # Ignored (direct field takes priority)
        "target_column": "Product_Line"
    }
)

# Expected: Should be KEPT (direct fields are NOT excluded)
```

---

## Impact Analysis

### Who is Affected?
1. **All KG creations with excluded_fields parameter**
2. **V2 relationship pairs (explicit pairs)**
3. **LLM-inferred relationships**
4. **Pattern-matched relationships**

### Symptoms:
- ❌ Excluded fields (like "Product_Line", "Business_Unit") still appear in KG relationships
- ❌ Queries use excluded fields for JOIN conditions
- ❌ Reconciliation rules created with excluded fields
- ❌ More relationships than expected in KG

### After Fix:
- ✅ All relationships with excluded fields properly removed
- ✅ Cleaner KG with only relevant relationships
- ✅ Better query performance (fewer unnecessary joins)
- ✅ More accurate reconciliation rules

---

## Additional Issues Found

### Issue 2: Inconsistent Column Storage

Different parts of the codebase store columns differently:

**Location 1: Explicit Relationship Pairs (V2)**
```python
# kg_relationship_service.py
rel = GraphRelationship(
    source_id=...,
    target_id=...,
    source_column=pair.source_column,  # ← Direct field
    target_column=pair.target_column,
    relationship_type=pair.relationship_type
)
```

**Location 2: LLM Enhancement**
```python
# schema_parser.py
rel = GraphRelationship(
    source_id=...,
    target_id=...,
    relationship_type=...,
    properties={
        "source_column": source_col,  # ← Properties dict
        "target_column": target_col
    }
)
```

**Recommendation:** Standardize to ALWAYS use direct fields (`rel.source_column`), not properties dict.

---

## Recommended Actions

### Immediate Fix (High Priority)
1. ✅ **Fix the filtering logic in `routes.py:261-274`**
   - Check both direct fields and properties dict
   - Priority: direct fields first

### Short-term Improvements (Medium Priority)
2. ✅ **Standardize column storage**
   - Update all relationship creation code to use direct fields
   - Migrate existing KGs if needed

3. ✅ **Add validation**
   - Warn if columns are in properties but not in direct fields
   - Add migration helper to move properties to direct fields

### Long-term Improvements (Low Priority)
4. ✅ **Add unit tests**
   - Test excluded fields filtering with different storage locations
   - Test edge cases (empty properties, missing columns)

5. ✅ **Add monitoring**
   - Log how many relationships are filtered
   - Track which fields are most commonly excluded
   - Alert if filtering removes 0 relationships (potential bug)

---

## Code to Apply

### File: `kg_builder/routes.py`

**Line 261-274** - Replace with:

```python
for rel in kg.relationships:
    # Check BOTH direct fields AND properties dict for column names
    # Priority: direct fields (rel.source_column) > properties dict
    source_col = rel.source_column or (rel.properties.get("source_column") if rel.properties else None)
    target_col = rel.target_column or (rel.properties.get("target_column") if rel.properties else None)

    if source_col and target_col:
        # Check if either column is excluded
        if is_excluded_field(source_col, excluded_fields_set) or is_excluded_field(target_col, excluded_fields_set):
            logger.debug(f"⛔ Removing relationship from KG (excluded field): {rel.source_id} ({source_col}) → {rel.target_id} ({target_col})")
            continue  # Skip this relationship

    # Keep this relationship
    filtered_relationships.append(rel)
```

---

## Verification Steps

After applying the fix:

1. **Create a KG with excluded fields:**
```json
{
  "kg_name": "test_kg",
  "schema_names": ["schema1"],
  "use_llm_enhancement": true,
  "excluded_fields": ["Product_Line", "Business_Unit", "BUSINESS_UNIT_CODE"],
  "relationship_pairs": [
    {
      "source_table": "brz_lnd_RBP_GPU",
      "source_column": "Product_Line",
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_column": "Product_Line"
    }
  ]
}
```

2. **Check the logs:**
```
✓ Filtered KG relationships: 15 → 12 (removed 3 with excluded fields)
⛔ Removing relationship from KG (excluded field): table_brz_lnd_RBP_GPU (Product_Line) → table_brz_lnd_OPS_EXCEL_GPU (Product_Line)
```

3. **Verify relationships:**
```python
# Get KG relationships
GET /kg/{kg_name}/relationships

# Should NOT contain any relationships with excluded fields
# Verify: No "Product_Line", "Business_Unit" in source_column or target_column
```

4. **Test queries:**
```
Query: "Show products in RBP but not in OPS"

# Should use non-excluded fields (e.g., Material, SKU)
# Should NOT use Product_Line or Business_Unit
```

---

## Summary

| Issue | Status | Priority |
|-------|--------|----------|
| Excluded fields not filtered from direct fields | 🔴 **BUG** | **HIGH** |
| Inconsistent column storage (fields vs properties) | 🟡 **Tech Debt** | Medium |
| Missing validation & tests | 🟡 **Gap** | Medium |

**Immediate Action Required:** Apply the fix to `kg_builder/routes.py:261-274`

**Expected Outcome:** All relationships with excluded fields will be properly removed from KG during creation.
