# Rule Generation Optimization Strategies

## 📊 Current Situation

**Current Rules Generated**: 19 rules
- Pattern-based rules: ~5-7 rules
- LLM-based rules: ~12-14 rules

**Problem**: Too many rules → Slower execution, redundant matching logic

---

## 🎯 Root Causes of Rule Explosion

### 1. **LLM Generates All Possible Combinations**
```
Current behavior:
- For each column pair, LLM generates a rule
- For each relationship type, LLM generates a rule
- For each match type (exact, fuzzy, semantic), LLM generates a rule

Example:
- id + id → Rule 1
- id + code → Rule 2
- code + code → Rule 3
- code + name → Rule 4
- ... (exponential growth)
```

### 2. **No Deduplication of Semantic Equivalents**
```
Generated rules:
- Rule: Match on id (confidence: 0.95)
- Rule: Match on id (confidence: 0.92)
- Rule: Match on id (confidence: 0.90)
→ All kept because confidence scores differ slightly
```

### 3. **LLM Generates Rules for All Relationships**
```
Current prompt doesn't limit:
- Number of rules per relationship
- Redundant match strategies
- Low-confidence variations
```

---

## ✅ Optimization Strategy 1: Limit Rules in LLM Prompt

### Current Prompt (Lines 437-490)
```
"For each rule, provide: rule_name, source_schema, ..."
(No limit on number of rules)
```

### Optimized Prompt
```python
def _build_reconciliation_rules_prompt(self, relationships, schemas_info):
    return f"""Generate ONLY the TOP 3 MOST IMPORTANT reconciliation rules.

CRITICAL CONSTRAINTS:
1. Generate MAXIMUM 3 rules total (not per relationship)
2. Prioritize by confidence score (highest first)
3. Avoid duplicate match strategies
4. Each rule must have UNIQUE source_columns + target_columns combination
5. Skip rules with confidence < 0.8

RELATIONSHIPS:
{relationships_str}

SCHEMAS:
{schemas_str}

Return JSON with exactly 3 rules (or fewer if not enough valid rules):
{{
  "rules": [
    {{"rule_name": "...", "confidence": 0.95, ...}},
    {{"rule_name": "...", "confidence": 0.85, ...}},
    {{"rule_name": "...", "confidence": 0.80, ...}}
  ]
}}
"""
```

**Expected Result**: 3 LLM rules instead of 12-14

---

## ✅ Optimization Strategy 2: Smarter Deduplication

### Current Deduplication (Line 83)
```python
unique_rules = self._deduplicate_rules(filtered_rules)
```

### Enhanced Deduplication
```python
def _deduplicate_rules(self, rules):
    """Remove semantically equivalent rules."""
    unique_rules = []
    seen_combinations = set()
    
    # Sort by confidence (highest first)
    sorted_rules = sorted(rules, key=lambda r: r.confidence_score, reverse=True)
    
    for rule in sorted_rules:
        # Create signature: (source_cols, target_cols, match_type)
        signature = (
            tuple(sorted(rule.source_columns)),
            tuple(sorted(rule.target_columns)),
            rule.match_type
        )
        
        # Skip if we've already seen this combination
        if signature not in seen_combinations:
            unique_rules.append(rule)
            seen_combinations.add(signature)
    
    return unique_rules
```

**Expected Result**: Remove 30-40% of duplicate rules

---

## ✅ Optimization Strategy 3: Confidence-Based Filtering

### Current Filtering (Line 80)
```python
filtered_rules = [r for r in all_rules if r.confidence_score >= min_confidence]
```

### Enhanced Filtering
```python
def _filter_rules_intelligently(self, rules, min_confidence=0.7):
    """Filter rules by confidence and importance."""
    
    # Group by (source_table, target_table)
    rule_groups = {}
    for rule in rules:
        key = (rule.source_table, rule.target_table)
        if key not in rule_groups:
            rule_groups[key] = []
        rule_groups[key].append(rule)
    
    filtered = []
    for key, group in rule_groups.items():
        # Sort by confidence
        sorted_group = sorted(group, key=lambda r: r.confidence_score, reverse=True)
        
        # Keep only top 2 rules per table pair
        for rule in sorted_group[:2]:
            if rule.confidence_score >= min_confidence:
                filtered.append(rule)
    
    return filtered
```

**Expected Result**: Keep only best rules per table pair

---

## ✅ Optimization Strategy 4: Relationship Filtering

### Current Approach
```
All relationships → All rules
```

### Optimized Approach
```python
def _get_kg_relationships(self, kg_name):
    """Query only high-confidence relationships."""
    query = """
    MATCH (source)-[r]->(target)
    WHERE r.confidence >= 0.8  # Filter at source
    RETURN source.label, target.label, type(r), properties(r)
    """
    # Only process high-confidence relationships
```

**Expected Result**: Fewer relationships → Fewer rules

---

## 📋 Implementation Roadmap

### Phase 1: Quick Wins (5 minutes)
```python
# 1. Update LLM prompt to limit to 3 rules
# 2. Enhance deduplication logic
# 3. Add per-table-pair rule limit
```

### Phase 2: Advanced Filtering (10 minutes)
```python
# 1. Filter relationships by confidence
# 2. Add rule importance scoring
# 3. Implement rule consolidation
```

### Phase 3: Testing & Validation (5 minutes)
```python
# 1. Run test with optimizations
# 2. Verify rule quality
# 3. Compare execution time
```

---

## 🎯 Expected Results

### Before Optimization
```
Total Rules: 19
- Pattern-based: 6
- LLM-based: 13
Execution Time: 16-21 seconds
```

### After Optimization (Phase 1)
```
Total Rules: 8-10
- Pattern-based: 5-6
- LLM-based: 3-4
Execution Time: 8-12 seconds (50% faster)
```

### After Optimization (Phase 1 + 2)
```
Total Rules: 5-7
- Pattern-based: 3-4
- LLM-based: 2-3
Execution Time: 4-6 seconds (75% faster)
```

---

## 💡 Key Principles

✅ **Quality over Quantity**
- 5 high-confidence rules > 19 mixed-confidence rules

✅ **Avoid Redundancy**
- One rule per unique column combination

✅ **Prioritize Relationships**
- Focus on strongest relationships first

✅ **Limit LLM Output**
- Explicit constraints in prompt

✅ **Smart Deduplication**
- Remove semantic duplicates

---

## 🔧 Code Changes Required

### File: `kg_builder/services/multi_schema_llm_service.py`

**Change 1**: Update prompt (lines 437-490)
```python
# Add: "Generate MAXIMUM 3 rules"
# Add: "Avoid duplicate match strategies"
# Add: "Each rule must have UNIQUE column combination"
```

**Change 2**: Add rule limit parameter
```python
def generate_reconciliation_rules(
    self,
    relationships,
    schemas_info,
    max_rules_per_relationship=1,  # NEW
    max_total_rules=3               # NEW
):
```

### File: `kg_builder/services/reconciliation_service.py`

**Change 1**: Enhance deduplication (lines 83)
```python
unique_rules = self._deduplicate_rules_enhanced(filtered_rules)
```

**Change 2**: Add per-table-pair filtering (lines 80)
```python
filtered_rules = self._filter_rules_intelligently(all_rules, min_confidence)
```

---

## 📊 Comparison Table

| Aspect | Current | Optimized |
|--------|---------|-----------|
| Total Rules | 19 | 5-7 |
| LLM Rules | 13 | 2-3 |
| Execution Time | 16-21s | 4-6s |
| Redundancy | High | Low |
| Quality | Mixed | High |
| Maintainability | Hard | Easy |

---

## 🚀 Next Steps

1. **Implement Phase 1** (Quick Wins)
   - Update LLM prompt
   - Enhance deduplication
   - Test with current data

2. **Measure Impact**
   - Compare rule count
   - Compare execution time
   - Verify rule quality

3. **Implement Phase 2** (Advanced)
   - Add relationship filtering
   - Add rule importance scoring
   - Optimize further

4. **Document Results**
   - Create before/after comparison
   - Document optimization techniques
   - Update prompts documentation

---

**Version**: 1.0  
**Date**: 2025-10-24  
**Status**: Ready for Implementation

