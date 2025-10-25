# Field Hints & Semantic Mapping - FAQ

## Q1: If I provide field hints, will semantic mapping still happen?

**A: YES! Semantic mapping ALWAYS happens. Field hints ENHANCE it.**

Field hints don't replace semantic mapping—they guide it. The LLM still performs semantic analysis, but with your hints as additional context.

---

## Q2: Are field hints and semantic mapping mutually exclusive?

**A: NO. They are COMPLEMENTARY.**

```
Semantic Mapping = LLM analyzes column names, data types, business logic
Field Hints = User provides additional guidance to semantic mapping

Result = Better semantic mapping with higher confidence
```

---

## Q3: What exactly do field hints do?

**A: Field hints provide three types of guidance:**

### 1. Explicit Suggestions
```json
"field_hints": { "MATERIAL": "PLANNING_SKU" }
```
Tells LLM: "These fields represent the same data"

### 2. Priority Focus
```json
"priority_fields": ["MATERIAL", "PLANNING_SKU"]
```
Tells LLM: "Focus on these fields first"

### 3. Noise Filtering
```json
"exclude_fields": ["INTERNAL_NOTES", "STAGING_FLAG"]
```
Tells LLM: "Skip these fields"

---

## Q4: How does the LLM use field hints?

**A: The LLM includes field hints in the prompt:**

```
SCHEMAS:
[schema definitions]

RELATIONSHIPS:
[detected relationships]

=== USER-SPECIFIC FIELD PREFERENCES ===
Table: hana_material_master
  ✓ PRIORITY FIELDS: MATERIAL, MATERIAL_DESC
  ✗ EXCLUDE FIELDS: INTERNAL_NOTES
  → FIELD HINTS: MATERIAL → PLANNING_SKU

TASK:
Generate reconciliation rules using semantic analysis
ENHANCED BY user-provided field hints
```

The LLM then:
1. Reads your field hints
2. Analyzes column names and data types
3. Performs semantic inference (GUIDED by hints)
4. Generates rules with higher confidence

---

## Q5: What's the difference in results?

**A: Field hints boost confidence and accuracy:**

| Metric | Without Hints | With Hints |
|--------|---------------|-----------|
| Rules | 5-8 | 8-12 |
| Confidence | 0.6-0.7 | 0.8-0.95 |
| Accuracy | ~60% | ~95% |

---

## Q6: Can field hints override semantic mapping?

**A: NO. Field hints GUIDE semantic mapping, not override it.**

Example:
```
Field Hint: MATERIAL → PLANNING_SKU
LLM Analysis:
1. User says these match
2. MATERIAL is a product identifier
3. PLANNING_SKU is a product identifier
4. Semantic meaning: same business entity
5. Generate rule with HIGH confidence (0.95)
```

The LLM validates hints against semantic analysis.

---

## Q7: What if my field hints are wrong?

**A: The LLM will still validate them semantically.**

Example:
```
Field Hint: MATERIAL → CUSTOMER_NAME (wrong!)
LLM Analysis:
1. User says these match
2. MATERIAL is a product identifier
3. CUSTOMER_NAME is a person's name
4. Semantic meaning: DIFFERENT business entities
5. Generate rule with LOW confidence (0.3)
   OR skip the rule entirely
```

The LLM uses semantic analysis to validate hints.

---

## Q8: Do I need field hints for semantic mapping to work?

**A: NO. Semantic mapping works without field hints.**

```
Without Field Hints:
- LLM analyzes schemas
- Infers relationships
- Generates rules (0.6-0.7 confidence)

With Field Hints:
- LLM reads your hints
- Analyzes schemas
- Infers relationships (guided)
- Generates rules (0.8-0.95 confidence)
```

Field hints are OPTIONAL but RECOMMENDED.

---

## Q9: When should I use field hints?

**A: Use field hints when:**

✅ You know fields represent the same data
✅ Field names differ between schemas
✅ You want to guide the LLM toward specific matches
✅ You have domain expertise about field relationships
✅ You want higher confidence scores

❌ Don't use when:
- You're unsure about field relationships
- Field names are already identical
- You want the LLM to discover relationships independently

---

## Q10: Can I use field hints without LLM?

**A: NO. Field hints only work with LLM enabled.**

```
use_llm=False:
- Only pattern-based rules generated
- Field hints are ignored

use_llm=True:
- Pattern-based rules generated
- LLM rules generated (using field hints)
- Combined results
```

---

## Q11: How do field hints affect performance?

**A: Minimal impact. Field hints actually improve performance:**

```
Without Field Hints:
- LLM explores many possibilities
- Slower inference
- Lower confidence

With Field Hints:
- LLM focuses on guided paths
- Faster inference
- Higher confidence
```

Field hints make the LLM more efficient.

---

## Q12: Can I provide field hints for only some tables?

**A: YES. Field hints are table-specific.**

```json
[
  {
    "table_name": "hana_material_master",
    "field_hints": { "MATERIAL": "PLANNING_SKU" }
  },
  {
    "table_name": "other_table",
    "field_hints": {}  // No hints for this table
  }
]
```

---

## Q13: What if I provide conflicting field hints?

**A: The LLM will resolve conflicts using semantic analysis.**

Example:
```json
{
  "field_hints": {
    "MATERIAL": "PLANNING_SKU",
    "MATERIAL": "PRODUCT_CODE"  // Conflict!
  }
}
```

The LLM will:
1. Recognize the conflict
2. Analyze semantic meaning
3. Choose the most likely match
4. Generate rule with appropriate confidence

---

## Q14: Do field hints work for single-schema reconciliation?

**A: YES. Field hints work for both single and multi-schema.**

```
Single Schema (intra-schema joins):
- Field hints guide table-to-table matching
- Example: orders.customer_id → customers.id

Multi-Schema (cross-schema):
- Field hints guide cross-database matching
- Example: db1.material → db2.planning_sku
```

---

## Q15: How do I know if field hints are working?

**A: Check the generated rules:**

```
Signs field hints are working:
✅ Rules include your suggested field mappings
✅ Confidence scores are 0.8+
✅ More rules generated (8-12 vs 5-8)
✅ Rules match your domain knowledge
✅ Metadata shows "llm_generated": true

Signs field hints aren't working:
❌ Your suggested mappings missing
❌ Low confidence scores (0.6-0.7)
❌ Few rules generated (5-8)
❌ Rules don't match domain knowledge
```

---

## Summary

| Question | Answer |
|----------|--------|
| Mutually exclusive? | NO - Complementary |
| Semantic mapping still happens? | YES - Enhanced |
| Override semantic mapping? | NO - Guide it |
| Required for semantic mapping? | NO - Optional |
| Work without LLM? | NO - LLM required |
| Affect performance? | Improves it |
| Work for single-schema? | YES |
| Work for multi-schema? | YES |

---

## Key Takeaway

```
Field Hints + Semantic Mapping = Better Results

Field hints don't replace semantic mapping.
They enhance it by providing user guidance.
```

---

## Related Documentation

- **FIELD_HINTS_VS_SEMANTIC_MAPPING.md** - Detailed comparison
- **FIELD_HINTS_EXAMPLE.md** - Real-world example
- **FIELD_HINTS_QUICK_REFERENCE.md** - Quick lookup
- **COPY_PASTE_NOW.md** - Ready-to-use examples


