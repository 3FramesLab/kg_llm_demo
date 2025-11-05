#!/usr/bin/env python3
"""
Analyze why MATERIAL → PRDID relationship isn't being considered.
This script checks the specific data patterns and reconciliation logic.
"""

import requests
import json

def analyze_prdid_relationship():
    """Analyze the MATERIAL → PRDID relationship pattern."""
    print("="*60)
    print("ANALYZING MATERIAL → PRDID RELATIONSHIP")
    print("="*60)
    
    # Check the actual data pattern
    print("\n1. ANALYZING DATA PATTERN:")
    print("   Based on seed data structure:")
    print("   hana_material_master.MATERIAL = 'GPU-001'")
    print("   brz_lnd_IBP_Product_Master.PRDID = 'PRD_GPU-001'")
    print("   ")
    print("   This is a HIERARCHICAL relationship:")
    print("   - MATERIAL: Base material identifier")
    print("   - PRDID: Product hierarchy identifier (PRD_ + MATERIAL)")
    print("   ")
    print("   Relationship Type: REFERENCES (not MATCHES)")
    print("   Reason: PRDID contains MATERIAL but with prefix")
    
    # Check reconciliation service logic
    print("\n2. RECONCILIATION SERVICE ANALYSIS:")
    print("   Possible reasons why it's not being considered:")
    print("   ")
    print("   a) EXACT MATCH EXPECTATION:")
    print("      - MATCHES relationships expect identical values")
    print("      - 'GPU-001' ≠ 'PRD_GPU-001' (not exact match)")
    print("   ")
    print("   b) RELATIONSHIP TYPE MISMATCH:")
    print("      - Current: MATCHES")
    print("      - Should be: REFERENCES (hierarchical)")
    print("   ")
    print("   c) PATTERN MATCHING LOGIC:")
    print("      - System may not recognize prefix patterns")
    print("      - Needs fuzzy or semantic matching")
    
    # Test different approaches
    print("\n3. TESTING DIFFERENT APPROACHES:")
    
    approaches = [
        {
            "name": "Keep as MATCHES with Fuzzy Matching",
            "config": {
                "source_table": "hana_material_master",
                "source_columns": ["MATERIAL"],
                "target_table": "brz_lnd_IBP_Product_Master",
                "target_columns": ["PRDID"],
                "match_type": "fuzzy",  # Changed to fuzzy
                "bidirectional": True
            },
            "reasoning": "Fuzzy matching can handle 'GPU-001' → 'PRD_GPU-001'"
        },
        {
            "name": "Change to REFERENCES Relationship",
            "config": {
                "source_table": "hana_material_master",
                "source_columns": ["MATERIAL"],
                "target_table": "brz_lnd_IBP_Product_Master", 
                "target_columns": ["PRDID"],
                "match_type": "exact",
                "bidirectional": False  # References are directional
            },
            "reasoning": "REFERENCES better represents hierarchical relationship"
        },
        {
            "name": "Use Semantic Matching",
            "config": {
                "source_table": "hana_material_master",
                "source_columns": ["MATERIAL"],
                "target_table": "brz_lnd_IBP_Product_Master",
                "target_columns": ["PRDID"],
                "match_type": "semantic",  # LLM-based matching
                "bidirectional": True
            },
            "reasoning": "LLM can understand the prefix relationship pattern"
        }
    ]
    
    for i, approach in enumerate(approaches, 1):
        print(f"\n   Approach {i}: {approach['name']}")
        print(f"   Config: {json.dumps(approach['config'], indent=6)}")
        print(f"   Reasoning: {approach['reasoning']}")
    
    # Check if the issue is in the reconciliation service code
    print("\n4. POTENTIAL CODE ISSUES:")
    print("   Check these areas in reconciliation_service.py:")
    print("   ")
    print("   a) Relationship Type Filtering:")
    print("      if rel.get('relationship_type') in ['MATCHES', 'REFERENCES']:")
    print("          # Make sure MATCHES is included")
    print("   ")
    print("   b) Column Matching Logic:")
    print("      # Check if exact string matching is required")
    print("      if source_col == target_col:  # This would fail for MATERIAL ≠ PRDID")
    print("   ")
    print("   c) Confidence Threshold:")
    print("      if confidence >= min_confidence:  # Check if confidence is too low")
    print("   ")
    print("   d) Schema Validation:")
    print("      # Check if both columns exist in schema")
    print("      if source_col in source_schema and target_col in target_schema:")
    
    return approaches

def test_relationship_with_api(kg_name="demo_kg"):
    """Test the relationship with different configurations."""
    print(f"\n5. TESTING WITH API (KG: {kg_name}):")
    
    try:
        # Test with fuzzy matching
        test_config = {
            "kg_name": kg_name,
            "schema_names": ["newdqschemanov"],
            "use_llm_enhancement": True,
            "min_confidence": 0.5,  # Lower threshold
            "reconciliation_pairs": [
                {
                    "source_table": "hana_material_master",
                    "source_columns": ["MATERIAL"],
                    "target_table": "brz_lnd_IBP_Product_Master",
                    "target_columns": ["PRDID"],
                    "match_type": "fuzzy",  # Try fuzzy matching
                    "bidirectional": True
                }
            ],
            "auto_discover_additional": True
        }
        
        print(f"   Testing fuzzy matching approach...")
        response = requests.post(
            "http://localhost:8000/api/v1/reconciliation/generate",
            json=test_config,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            rules = result.get('rules', [])
            
            # Look for our rule
            found_rule = None
            for rule in rules:
                if (rule.get('source_table') == 'hana_material_master' and 
                    rule.get('target_table') == 'brz_lnd_IBP_Product_Master' and
                    'MATERIAL' in rule.get('source_columns', []) and
                    'PRDID' in rule.get('target_columns', [])):
                    found_rule = rule
                    break
            
            if found_rule:
                print(f"   ✅ SUCCESS: Rule generated with fuzzy matching!")
                print(f"      Rule ID: {found_rule.get('rule_id')}")
                print(f"      Confidence: {found_rule.get('confidence_score')}")
                print(f"      Match Type: {found_rule.get('match_type')}")
                print(f"      Reasoning: {found_rule.get('reasoning')}")
            else:
                print(f"   ❌ FAILED: No rule generated even with fuzzy matching")
                print(f"      Generated {len(rules)} rules total")
                if rules:
                    print(f"      Sample rule: {rules[0].get('source_table')} → {rules[0].get('target_table')}")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"      Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  Cannot connect to API server")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Main analysis function."""
    print("MATERIAL → PRDID Relationship Analysis")
    print("This analyzes why your specific relationship isn't being considered")
    print()
    
    # Analyze the relationship pattern
    approaches = analyze_prdid_relationship()
    
    # Test with API if available
    kg_name = input("\nEnter your KG name to test with API (or press Enter to skip): ").strip()
    if kg_name:
        test_relationship_with_api(kg_name)
    
    # Provide recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS:")
    print("="*60)
    print()
    print("1. IMMEDIATE FIX - Try Fuzzy Matching:")
    print("   Change match_type from 'exact' to 'fuzzy' in your reconciliation_pairs")
    print()
    print("2. ALTERNATIVE - Use Semantic Matching:")
    print("   Change match_type to 'semantic' to let LLM understand the pattern")
    print()
    print("3. CHECK CONFIDENCE THRESHOLD:")
    print("   Lower min_confidence to 0.5 or 0.3 to see if confidence is the issue")
    print()
    print("4. VERIFY KG RELATIONSHIP EXISTS:")
    print("   Run: curl http://localhost:8000/api/v1/kg/YOUR_KG_NAME/relationships")
    print()
    print("5. CHECK LOGS:")
    print("   Look at logs/app.log for reconciliation service debug messages")
    print()
    print("The most likely fix is changing match_type to 'fuzzy' or 'semantic'!")

if __name__ == "__main__":
    main()
