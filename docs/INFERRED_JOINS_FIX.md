# Inferred Joins Fix - Additional Columns from Related Tables

## Problem Statement

**Query:** "Show me all products in RBP GPU which are inactive in OPS Excel, show who was ops_planner from material master"

**Error:**
```
❌ No join path found between brz_lnd_RBP_GPU and hana_material_master
❌ No relationship path found for column 'ops_planner'
```

**Root Cause:**
- LLM correctly extracted "ops_planner from material_master" as additional column
- System tried to find a relationship path in the Knowledge Graph
- No explicit relationship existed between RBP_GPU and material_master
- Query failed even though both tables have common "Material" column

---

## What Should Happen ✅

For the query above, the system should generate SQL like:

```sql
SELECT DISTINCT s.*, mm.ops_planner AS ops_planner
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t
  ON s.[Material] = t.[PLANNING_SKU]
LEFT JOIN [hana_material_master] mm
  ON s.[Material] = mm.[Material]  -- ← Inferred from common column names!
WHERE t.[Active_Inactive] = 'Inactive'
```

**Key Points:**
1. ✅ Main query: Products in RBP that are inactive in OPS
2. ✅ Additional column: `ops_planner` from `material_master`
3. ✅ Automatic join inference: Both tables have "Material" column
4. ✅ No explicit KG relationship needed

---

## The Fix Applied

### 1. Reverted Wrong Excluded Fields Logic

**File:** `kg_builder/routes.py:250-277`

**Before (WRONG):**
```python
# Removed relationships from KG if they used excluded fields
if is_excluded_field(source_col, excluded_fields_set):
    continue  # ❌ Skip this relationship - BREAKS CONNECTIVITY!
```

**After (CORRECT):**
```python
# Mark relationships as low-priority but KEEP them for connectivity
rel.properties["is_excluded"] = True
rel.properties["priority"] = -1  # Lower priority, but still usable
```

**Why:** Removing relationships broke table connectivity in the KG. Tables became disconnected and queries failed.

---

### 2. Added Inferred Join Fallback

**File:** `kg_builder/services/nl_query_parser.py:890-979`

**New Method:** `_infer_join_from_column_names(source, target)`

**How It Works:**

```python
def _infer_join_from_column_names(source, target):
    """
    When no explicit KG relationship exists, infer join from common columns.

    Steps:
    1. Get columns from both tables (from schemas_info)
    2. Find common column names (case-insensitive)
    3. Prioritize ID-like columns (Material, SKU, etc.)
    4. Return synthetic JoinPath with confidence=0.65
    """
```

**Column Priority:**
```python
High Priority (score=3):
  - material, product, sku, item, code

Medium Priority (score=2):
  - columns ending with "_id", "_uid"

Low Priority (score=1):
  - number, ref, key

Avoid:
  - Generic columns like "status", "date", "name"
```

**Example:**
```
brz_lnd_RBP_GPU columns: [Material, Material_Desc, Status, ...]
hana_material_master columns: [Material, Material_Name, Planner, ...]

Common columns found: Material (HIGH PRIORITY)
✓ Inferred join: Material ←→ Material (confidence: 0.65)
```

---

### 3. Updated Join Path Finding Logic

**File:** `kg_builder/services/nl_query_parser.py:859-869`

**Before:**
```python
if not all_paths:
    logger.warning(f"No join path found between {source} and {target}")
    return None  # ❌ Immediate failure
```

**After:**
```python
if not all_paths:
    logger.warning(f"No join path found in KG between {source} and {target}")

    # Fallback: Try to infer join from column names
    inferred_path = self._infer_join_from_column_names(source, target)
    if inferred_path:
        logger.info(f"✓ Inferred join path from column names")
        return inferred_path  # ✅ Success with inferred join

    logger.warning(f"❌ No join path found")
    return None
```

**Flow:**
```
1. Try to find path in KG relationships (BFS)
   ↓ Not found
2. Try to infer join from common column names
   ↓ Found!
3. Return synthetic JoinPath with inferred columns
```

---

## Example: End-to-End Flow

### Query
```
"Show me all products in RBP GPU which are inactive in OPS Excel, show who was ops_planner from material master"
```

### Step 1: LLM Parsing
```json
{
  "source_table": "brz_lnd_RBP_GPU",
  "target_table": "brz_lnd_OPS_EXCEL_GPU",
  "filters": [{"column": "Active_Inactive", "value": "Inactive"}],
  "additional_columns": [
    {
      "column_name": "ops_planner",
      "source_table": "hana_material_master"
    }
  ]
}
```

### Step 2: Join Resolution
```
Main join: RBP_GPU ←→ OPS_EXCEL_GPU
  ✓ Found in KG: Material ←→ PLANNING_SKU

Additional column join: RBP_GPU ←→ hana_material_master
  ✗ Not found in KG relationships
  🔍 Trying to infer from column names...
  ✓ Found common column: Material
  ✓ Inferred join: Material ←→ Material (confidence: 0.65)
```

### Step 3: SQL Generation
```sql
SELECT DISTINCT s.*, mm.ops_planner AS ops_planner
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t
  ON s.[Material] = t.[PLANNING_SKU]
LEFT JOIN [hana_material_master] mm
  ON s.[Material] = mm.[Material]  -- ← Inferred!
WHERE t.[Active_Inactive] = 'Inactive'
```

### Step 4: Execution
```
✅ Query executes successfully
✅ Returns products with ops_planner column
```

---

## Benefits

### Before Fix
```
❌ Required explicit KG relationships for ALL table joins
❌ Failed when relationships missing
❌ No fallback mechanism
❌ Users had to manually add relationships
```

### After Fix
```
✅ Automatically infers joins from common columns
✅ Works even without explicit KG relationships
✅ Intelligent column prioritization
✅ Seamless user experience
```

---

## Configuration

**No configuration needed!** The feature works automatically:

1. **KG relationships take priority** (confidence: 0.75-0.95)
2. **Inferred joins as fallback** (confidence: 0.65)
3. **Column name matching is case-insensitive**
4. **Prefers ID-like columns** (Material, SKU, Product, etc.)

---

## Column Matching Examples

### Good Matches (High Confidence)
```
✓ Material ←→ Material
✓ PLANNING_SKU ←→ planning_sku
✓ Product_ID ←→ product_id
✓ Material_Code ←→ MATERIAL_CODE
```

### Acceptable Matches (Medium Confidence)
```
✓ Item_ID ←→ Item_ID
✓ Product_Ref ←→ PRODUCT_REF
✓ Customer_Number ←→ customer_number
```

### Avoided Matches (Low Priority)
```
⚠️ Status ←→ Status (too generic)
⚠️ Date ←→ Date (ambiguous)
⚠️ Name ←→ Name (common but unreliable)
```

---

## Testing

### Test Case 1: Inferred Join with Material Column
```python
Query: "Show products from RBP with planner from material master"

Expected:
- Main table: brz_lnd_RBP_GPU
- Additional column: planner from hana_material_master
- Inferred join: Material ←→ Material
- SQL includes: LEFT JOIN hana_material_master mm ON s.Material = mm.Material
```

### Test Case 2: Multiple Common Columns
```python
Tables:
- RBP_GPU: [Material, Product_ID, Status]
- MATERIAL_MASTER: [Material, Product_ID, Planner]

Expected:
- Finds both Material and Product_ID
- Prioritizes "Material" (higher priority)
- Uses Material for join
```

### Test Case 3: No Common Columns
```python
Tables:
- RBP_GPU: [Material, Quantity]
- SUPPLIER: [Supplier_ID, Supplier_Name]

Expected:
- No common columns found
- Returns None
- Error message: "No join path found"
```

---

## Logging Output

### Success Case
```
INFO - Parsing definition: Show products with planner from material master
INFO - ✓ Extracted 1 additional column requests
WARNING - No join path found in KG between brz_lnd_RBP_GPU and hana_material_master
INFO - 🔍 Attempting to infer join between brz_lnd_RBP_GPU and hana_material_master from column names
DEBUG - Source columns: ['Material', 'Material_Desc', 'Status', ...]
DEBUG - Target columns: ['Material', 'Material_Name', 'Planner', ...]
DEBUG - Found common column: Material ←→ Material
INFO - ✓ Inferred join column: brz_lnd_RBP_GPU.Material ←→ hana_material_master.Material
INFO - ✓ Inferred join path from column names: brz_lnd_RBP_GPU ←→ hana_material_master
INFO - ✓ Resolved 1 additional columns
```

### Failure Case
```
WARNING - No join path found in KG between table_A and table_B
INFO - 🔍 Attempting to infer join between table_A and table_B from column names
DEBUG - No common columns found
WARNING - ❌ No join path found between table_A and table_B
WARNING - Column validation errors: ["❌ No relationship path found..."]
```

---

## Future Enhancements

1. **Fuzzy Column Matching**
   - Match "MaterialID" with "Material_ID"
   - Handle abbreviations: "Mat" ←→ "Material"

2. **Multi-Column Joins**
   - Support composite keys
   - JOIN ON (col1, col2) = (col3, col4)

3. **Foreign Key Detection**
   - Analyze column names for FK patterns
   - "Customer_ID" likely references "Customer.ID"

4. **User Override**
   - Allow users to specify preferred join columns
   - Override inferred joins

5. **Learning from Usage**
   - Track successful inferred joins
   - Increase confidence for frequently used patterns

---

## Summary

| Issue | Status | Impact |
|-------|--------|--------|
| Excluded fields breaking connectivity | ✅ **Fixed** | Tables remain connected in KG |
| No fallback for missing relationships | ✅ **Fixed** | Automatic column name inference |
| Additional columns requiring explicit KG paths | ✅ **Fixed** | Works without KG relationships |

**Result:** System now handles additional columns from related tables automatically, even without explicit Knowledge Graph relationships!
