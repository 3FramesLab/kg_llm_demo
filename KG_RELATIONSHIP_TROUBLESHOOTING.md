# KG Relationship Not Being Considered - Troubleshooting Guide

## 🎯 Problem
Your KG relationship `hana_material_master.MATERIAL → brz_lnd_IBP_Product_Master.PRDID` is not being considered during reconciliation rule generation.

## 🔍 Common Causes & Solutions

### **1. Wrong Target Column**
**Issue**: Using `PRDID` instead of `ZBASEMATERIAL`

**Check**: Based on the seed data structure:
```sql
-- PRDID contains: 'PRD_GPU-001' (hierarchical product ID)
-- ZBASEMATERIAL contains: 'GPU-001' (actual material match)
```

**Solution**: Update relationship to use correct column:
```json
{
    "source_column": "MATERIAL",
    "target_column": "ZBASEMATERIAL",  // ← Change from PRDID
    "relationship_type": "MATCHES"
}
```

### **2. KG Not Loaded/Accessible**
**Check**: Verify KG exists and is accessible
```bash
curl http://localhost:8000/api/v1/kg/YOUR_KG_NAME/relationships
```

**Solution**: Ensure KG is properly created and stored

### **3. Schema Names Mismatch**
**Check**: Verify schema names in request match KG
```json
{
    "kg_name": "your_kg_name",
    "schema_names": ["newdqschemanov"],  // ← Must match KG schema names
}
```

### **4. Confidence Threshold Too High**
**Check**: Relationship confidence vs min_confidence
```json
{
    "min_confidence": 0.7,  // ← Lower if relationship confidence is below this
}
```

### **5. Auto-Discovery Disabled**
**Check**: Ensure auto-discovery is enabled
```json
{
    "auto_discover_additional": true  // ← Must be true to use KG relationships
}
```

### **6. Explicit Pairs Override**
**Issue**: When using `reconciliation_pairs`, auto-discovery might be skipped

**Solution**: Either:
- Remove `reconciliation_pairs` to rely on KG auto-discovery
- Or add the relationship as an explicit pair:
```json
{
    "reconciliation_pairs": [
        {
            "source_table": "hana_material_master",
            "source_columns": ["MATERIAL"],
            "target_table": "brz_lnd_IBP_Product_Master", 
            "target_columns": ["ZBASEMATERIAL"],
            "match_type": "exact",
            "bidirectional": true
        }
    ]
}
```

### **7. Table/Column Names Case Sensitivity**
**Check**: Ensure exact case matching
```json
// KG uses:
"source_id": "hana_material_master"
"target_id": "brz_lnd_IBP_Product_Master"

// Request uses:
"schema_names": ["newdqschemanov"]  // ← Must contain these tables
```

### **8. Relationship Type Filtering**
**Check**: Some relationship types might be filtered out
```python
# In reconciliation service, check if MATCHES relationships are processed
if rel.get('relationship_type') in ['MATCHES', 'REFERENCES', 'FOREIGN_KEY']:
    # Process relationship
```

## 🧪 **Debugging Steps**

### **Step 1: Run Debug Script**
```bash
python3 debug_kg_relationship.py
```

### **Step 2: Check KG Directly**
```bash
# Get all relationships
curl http://localhost:8000/api/v1/kg/YOUR_KG_NAME/relationships

# Look for your specific relationship
curl http://localhost:8000/api/v1/kg/YOUR_KG_NAME/relationships | grep -A5 -B5 "hana_material_master"
```

### **Step 3: Test Rule Generation**
```bash
curl -X POST http://localhost:8000/api/v1/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "YOUR_KG_NAME",
    "schema_names": ["newdqschemanov"],
    "use_llm_enhancement": true,
    "min_confidence": 0.5,
    "auto_discover_additional": true
  }'
```

### **Step 4: Check Logs**
```bash
# Check application logs for errors
tail -f logs/app.log

# Look for reconciliation service logs
grep -i "reconciliation" logs/app.log
```

## 🔧 **Quick Fixes**

### **Fix 1: Correct the Column Mapping**
```json
{
    "source_table": "hana_material_master",
    "source_column": "MATERIAL", 
    "target_table": "brz_lnd_IBP_Product_Master",
    "target_column": "ZBASEMATERIAL",  // ← Changed from PRDID
    "relationship_type": "MATCHES",
    "confidence": 0.95,
    "bidirectional": true
}
```

### **Fix 2: Add as Explicit Pair**
```json
{
    "reconciliation_pairs": [
        {
            "source_table": "hana_material_master",
            "source_columns": ["MATERIAL"],
            "target_table": "brz_lnd_IBP_Product_Master",
            "target_columns": ["ZBASEMATERIAL"],
            "match_type": "exact",
            "bidirectional": true
        }
    ],
    "auto_discover_additional": true
}
```

### **Fix 3: Lower Confidence Threshold**
```json
{
    "min_confidence": 0.5,  // ← Lower threshold
    "auto_discover_additional": true
}
```

## 📊 **Expected Behavior**

When working correctly, you should see:

### **In KG Relationships:**
```json
{
    "source_id": "hana_material_master",
    "target_id": "brz_lnd_IBP_Product_Master", 
    "relationship_type": "MATCHES",
    "source_column": "MATERIAL",
    "target_column": "ZBASEMATERIAL",
    "properties": {
        "confidence": 0.95
    }
}
```

### **In Generated Rules:**
```json
{
    "rule_id": "rule_123",
    "source_table": "hana_material_master",
    "source_columns": ["MATERIAL"],
    "target_table": "brz_lnd_IBP_Product_Master",
    "target_columns": ["ZBASEMATERIAL"],
    "match_type": "EXACT",
    "confidence_score": 0.95,
    "reasoning": "Direct material match from KG relationship"
}
```

## 🎯 **Most Likely Issue**

Based on your relationship showing `PRDID`, the most likely issue is **wrong target column**. 

**Quick Fix**: Change `target_column` from `"PRDID"` to `"ZBASEMATERIAL"` in your KG relationship.

Run the debug script to confirm the exact issue!
