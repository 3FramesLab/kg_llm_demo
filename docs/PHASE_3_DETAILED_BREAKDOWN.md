# Phase 3: Detailed Breakdown - What Will Be Done

## 🎯 Overview

Phase 3 will execute a comprehensive end-to-end test using real schemas to validate the Natural Language Relationships feature and measure its impact on reconciliation rules.

---

## 📋 Detailed Tasks

### TASK 1: Environment Setup (15 minutes)

**What**: Prepare the testing environment

**Steps**:
1. Verify real schemas are loaded
   - `schemas/orderMgmt-catalog.json` (29 KB)
   - `schemas/qinspect-designcode.json` (18 KB)

2. Create test data directory
   - `data/phase_3_results/`
   - `data/phase_3_baseline/`

3. Initialize logging
   - Enable detailed logging
   - Create log files for each step

4. Verify all dependencies
   - Check Phase 1 parser is working
   - Check Phase 2 integration is working
   - Check reconciliation engine is working

**Output**: Ready-to-test environment

---

### TASK 2: Baseline Metrics Collection (30 minutes)

**What**: Establish baseline before adding NL relationships

**Steps**:

1. **Load Schemas**
   ```python
   from kg_builder.services.schema_parser import SchemaParser
   
   schema1 = SchemaParser.load_schema("orderMgmt-catalog")
   schema2 = SchemaParser.load_schema("qinspect-designcode")
   ```

2. **Generate Initial KG**
   ```python
   kg = SchemaParser.build_merged_knowledge_graph(
       schema_names=["orderMgmt-catalog", "qinspect-designcode"],
       kg_name="baseline_kg",
       use_llm=True
   )
   ```

3. **Collect Baseline Metrics**
   - Total nodes: Count all tables/columns
   - Total relationships: Count auto-detected relationships
   - Relationships by type: FOREIGN_KEY, REFERENCES, etc.
   - Average confidence: Calculate from all relationships
   - High-confidence count: Count relationships with confidence ≥ 0.7

4. **Generate Reconciliation Rules**
   ```python
   rules = SchemaParser.generate_reconciliation_rules(kg)
   ```

5. **Record Baseline Data**
   ```json
   {
     "timestamp": "2025-10-22T10:00:00Z",
     "schemas": ["orderMgmt-catalog", "qinspect-designcode"],
     "kg_nodes": 50,
     "kg_relationships": 25,
     "reconciliation_rules": 19,
     "avg_confidence": 0.75,
     "high_confidence_count": 18,
     "relationships_by_type": {
       "FOREIGN_KEY": 12,
       "REFERENCES": 8,
       "CROSS_SCHEMA": 5
     }
   }
   ```

**Output**: `data/phase_3_baseline/baseline_metrics.json`

---

### TASK 3: Natural Language Definitions (30 minutes)

**What**: Define business relationships in natural language

**Steps**:

1. **Analyze Real Schemas**
   - Examine orderMgmt-catalog schema structure
   - Examine qinspect-designcode schema structure
   - Identify key business relationships

2. **Define NL Relationships** (8-10 definitions)
   ```
   1. "Products are supplied by Vendors"
   2. "Orders are placed by Vendors"
   3. "Orders contain Products"
   4. "Vendors manage Inventory"
   5. "Products have Categories"
   6. "Orders reference Customers"
   7. "Vendors provide Services"
   8. "Products are stored in Warehouses"
   ```

3. **Parse Each Definition**
   ```python
   from kg_builder.services.nl_relationship_parser import get_nl_relationship_parser
   
   parser = get_nl_relationship_parser()
   for definition in nl_definitions:
       parsed = parser.parse(definition, schemas_info, use_llm=True)
       # Record: source, target, type, confidence
   ```

4. **Validate Definitions**
   - Check source table exists
   - Check target table exists
   - Verify relationship type is valid
   - Confirm confidence score ≥ 0.7

5. **Record NL Definitions**
   ```json
   {
     "definitions": [
       {
         "text": "Products are supplied by Vendors",
         "source_table": "products",
         "target_table": "vendors",
         "relationship_type": "SUPPLIED_BY",
         "confidence": 0.85,
         "status": "VALID"
       }
     ]
   }
   ```

**Output**: `data/phase_3_baseline/nl_definitions.json`

---

### TASK 4: Integration & Reconciliation (30 minutes)

**What**: Add NL relationships and regenerate reconciliation rules

**Steps**:

1. **Add NL Relationships to KG**
   ```python
   updated_kg = SchemaParser.add_nl_relationships_to_kg(
       kg=baseline_kg,
       nl_relationships=parsed_definitions
   )
   ```

2. **Merge Relationships**
   ```python
   merged_kg = SchemaParser.merge_relationships(
       kg=updated_kg,
       strategy="deduplicate"
   )
   ```

3. **Get Updated Statistics**
   ```python
   stats = SchemaParser.get_relationship_statistics(merged_kg)
   ```

4. **Regenerate Reconciliation Rules**
   ```python
   new_rules = SchemaParser.generate_reconciliation_rules(merged_kg)
   ```

5. **Compare Metrics**
   ```json
   {
     "after_integration": {
       "kg_relationships": 35,
       "reconciliation_rules": 35,
       "avg_confidence": 0.82,
       "high_confidence_count": 32
     },
     "improvement": {
       "rules_increase": 16,
       "rules_increase_pct": 84.2,
       "confidence_increase": 0.07,
       "confidence_increase_pct": 9.3,
       "high_confidence_increase": 14,
       "high_confidence_increase_pct": 77.8
     }
   }
   ```

**Output**: `data/phase_3_results/integration_results.json`

---

### TASK 5: Validation & Testing (1 hour)

**What**: Verify accuracy and performance

**Test Cases**:

1. **Relationship Accuracy Tests**
   - Verify each NL relationship is in final KG
   - Check source and target are correct
   - Validate relationship type
   - Confirm confidence score

2. **Duplicate Detection Tests**
   - Verify no duplicate relationships
   - Check merge strategy worked
   - Validate deduplication count

3. **Confidence Scoring Tests**
   - Verify confidence scores 0.7-0.95
   - Check average calculation
   - Validate high-confidence filtering

4. **Performance Tests**
   - Measure KG generation: <2 seconds
   - Measure NL parsing: <1 second per definition
   - Measure integration: <1 second
   - Measure reconciliation: <2 seconds
   - Total: <5 seconds

5. **Edge Case Tests**
   - Invalid definitions (should be skipped)
   - Non-existent tables (should error)
   - Circular relationships (should be allowed)
   - Self-references (should be allowed)

**Output**: `tests/test_phase_3_e2e.py` (comprehensive test suite)

---

### TASK 6: Reporting & Analysis (1 hour)

**What**: Generate comprehensive reports

**Reports to Create**:

1. **Baseline Report**
   - Initial KG metrics
   - Auto-detected relationships
   - Initial reconciliation rules
   - Baseline confidence scores

2. **Results Report**
   - Final KG metrics
   - NL-defined relationships
   - Final reconciliation rules
   - Updated confidence scores

3. **Comparison Analysis**
   - Side-by-side metrics
   - Improvement percentages
   - Relationship breakdown
   - Confidence distribution

4. **Recommendations**
   - Additional NL definitions to consider
   - Performance optimizations
   - Production deployment readiness
   - Future enhancements

**Output**: 
- `docs/PHASE_3_BASELINE_REPORT.md`
- `docs/PHASE_3_RESULTS_REPORT.md`
- `docs/PHASE_3_COMPARISON_ANALYSIS.md`
- `docs/PHASE_3_RECOMMENDATIONS.md`

---

## 📊 Expected Results

### Metrics Improvement
```
Baseline:
  - KG Relationships: 25
  - Reconciliation Rules: 19
  - Avg Confidence: 0.75
  - High-Confidence: 18

After NL Integration:
  - KG Relationships: 35 (+40%)
  - Reconciliation Rules: 35 (+84%)
  - Avg Confidence: 0.82 (+9%)
  - High-Confidence: 32 (+78%)
```

### Quality Metrics
- ✅ 100% relationship accuracy
- ✅ 100% duplicate detection
- ✅ 100% error handling
- ✅ <5 second total processing time

---

## 🧪 Test Files to Create

1. **`tests/test_phase_3_e2e.py`**
   - End-to-end workflow tests
   - Real schema tests
   - Metrics comparison tests
   - Performance tests

2. **`scripts/phase_3_baseline.py`**
   - Baseline collection script
   - Metrics recording
   - Data export

3. **`scripts/phase_3_integration.py`**
   - NL integration script
   - Reconciliation regeneration
   - Results comparison

---

## 📈 Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| Rule increase | >80% | TBD |
| Confidence increase | >8% | TBD |
| Processing time | <5 sec | TBD |
| Accuracy | >95% | TBD |
| All tests pass | 100% | TBD |
| Documentation | Complete | TBD |

---

## ⏱️ Timeline

- **Setup**: 15 minutes
- **Baseline**: 30 minutes
- **NL Definitions**: 30 minutes
- **Integration**: 30 minutes
- **Testing**: 1 hour
- **Reporting**: 1 hour
- **Total**: ~4 hours

---

**Status**: Ready to Execute
**Complexity**: Medium
**Risk**: Low

