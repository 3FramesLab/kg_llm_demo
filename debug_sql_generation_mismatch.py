#!/usr/bin/env python3
"""
Debug why SQL generation is using ZBASEMATERIAL instead of PRDID 
when the KG relationship clearly shows MATERIAL → PRDID.
"""

import requests
import json

def debug_sql_generation_mismatch():
    """Debug the SQL generation mismatch."""
    print("="*60)
    print("DEBUGGING SQL GENERATION MISMATCH")
    print("="*60)
    
    print("\n🔍 PROBLEM IDENTIFIED:")
    print("   KG Relationship: MATERIAL → PRDID")
    print("   Generated SQL:   MATERIAL → ZBASEMATERIAL")
    print("   Issue: Reconciliation service is ignoring KG relationship")
    
    # Test rule generation to see what's happening
    print("\n1. TESTING RULE GENERATION:")
    
    try:
        test_config = {
            "kg_name": "Nov_100_KG",
            "schema_names": ["newdqschemanov"],
            "use_llm_enhancement": False,  # Disable to isolate KG usage
            "min_confidence": 0.1,
            "auto_discover_additional": True,
            "max_rules": 50
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/reconciliation/generate",
            json=test_config,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Rule generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
        
        result = response.json()
        rules = result.get('rules', [])
        
        print(f"✅ Generated {len(rules)} rules")
        
        # Look for the IBP Product Master rule
        ibp_rules = []
        for rule in rules:
            if (rule.get('source_table') == 'hana_material_master' and 
                rule.get('target_table') == 'brz_lnd_IBP_Product_Master'):
                ibp_rules.append(rule)
        
        if ibp_rules:
            print(f"\n📋 Found {len(ibp_rules)} rules for hana_material_master → brz_lnd_IBP_Product_Master:")
            
            for i, rule in enumerate(ibp_rules, 1):
                print(f"\n   Rule {i}:")
                print(f"   - Source columns: {rule.get('source_columns')}")
                print(f"   - Target columns: {rule.get('target_columns')}")
                print(f"   - Match type: {rule.get('match_type')}")
                print(f"   - Confidence: {rule.get('confidence_score')}")
                print(f"   - Reasoning: {rule.get('reasoning', 'N/A')}")
                print(f"   - Source: {rule.get('source', 'N/A')}")
                
                # Check if this is using PRDID
                if 'PRDID' in rule.get('target_columns', []):
                    print(f"   ✅ This rule DOES use PRDID!")
                elif 'ZBASEMATERIAL' in rule.get('target_columns', []):
                    print(f"   ❌ This rule uses ZBASEMATERIAL instead of PRDID")
                    print(f"   🔍 This suggests the rule is NOT coming from your KG relationship")
        else:
            print(f"\n❌ NO RULES found for hana_material_master → brz_lnd_IBP_Product_Master")
            print(f"   This means your KG relationship is being completely ignored")
        
        # 2. Test with explicit pairs to force the relationship
        print(f"\n2. TESTING WITH EXPLICIT PAIRS:")
        
        explicit_config = {
            "kg_name": "Nov_100_KG",
            "schema_names": ["newdqschemanov"],
            "use_llm_enhancement": False,
            "min_confidence": 0.1,
            "reconciliation_pairs": [
                {
                    "source_table": "hana_material_master",
                    "source_columns": ["MATERIAL"],
                    "target_table": "brz_lnd_IBP_Product_Master",
                    "target_columns": ["PRDID"],  # Force PRDID
                    "match_type": "exact",
                    "bidirectional": True
                }
            ],
            "auto_discover_additional": False  # Only use explicit pairs
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/reconciliation/generate",
            json=explicit_config,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            rules = result.get('rules', [])
            
            print(f"✅ Generated {len(rules)} rules with explicit pairs")
            
            if rules:
                rule = rules[0]
                print(f"\n   Explicit rule:")
                print(f"   - Source columns: {rule.get('source_columns')}")
                print(f"   - Target columns: {rule.get('target_columns')}")
                
                if 'PRDID' in rule.get('target_columns', []):
                    print(f"   ✅ Explicit pairs DO work with PRDID!")
                    print(f"   🔍 This confirms the issue is with KG relationship processing")
            else:
                print(f"   ❌ No rules generated even with explicit pairs")
        else:
            print(f"❌ Explicit pairs test failed: {response.status_code}")
        
        # 3. Test SQL generation for a specific rule
        print(f"\n3. TESTING SQL GENERATION:")
        
        if ibp_rules:
            rule_id = ibp_rules[0].get('rule_id')
            if rule_id:
                sql_config = {
                    "rule_ids": [rule_id],
                    "limit": 1000,
                    "filters": {
                        "hana_material_master": {
                            "Product Type": "GPU"
                        }
                    }
                }
                
                response = requests.post(
                    "http://localhost:8000/api/v1/reconciliation/execute",
                    json=sql_config,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    sql_query = result.get('sql_query', '')
                    
                    print(f"✅ Generated SQL:")
                    print(f"   {sql_query}")
                    
                    if 'PRDID' in sql_query:
                        print(f"   ✅ SQL uses PRDID - correct!")
                    elif 'ZBASEMATERIAL' in sql_query:
                        print(f"   ❌ SQL uses ZBASEMATERIAL - this is the bug!")
                        print(f"   🔍 The rule generation is correct but SQL generation is wrong")
                    else:
                        print(f"   ⚠️  SQL doesn't contain either PRDID or ZBASEMATERIAL")
                else:
                    print(f"❌ SQL generation failed: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_possible_causes():
    """Analyze possible causes of the mismatch."""
    print(f"\n4. POSSIBLE CAUSES ANALYSIS:")
    print("="*40)
    
    causes = [
        {
            "cause": "KG Relationship Not Being Used",
            "description": "The reconciliation service is not reading from KG",
            "check": "Rule generation should show 'source': 'kg_relationship' or similar",
            "fix": "Check if auto_discover_additional=true and KG is accessible"
        },
        {
            "cause": "Schema-Based Auto-Discovery Override",
            "description": "Service finds ZBASEMATERIAL via schema analysis and ignores KG",
            "check": "Rules show 'source': 'schema_analysis' or 'llm_inferred': true",
            "fix": "Disable auto-discovery or increase KG relationship priority"
        },
        {
            "cause": "Column Name Similarity Logic",
            "description": "Service prefers exact column name matches (Material ↔ Material)",
            "check": "ZBASEMATERIAL contains 'MATERIAL' substring",
            "fix": "Increase confidence of PRDID relationship or disable similarity matching"
        },
        {
            "cause": "Rule Merging/Deduplication",
            "description": "Multiple rules exist and wrong one is selected",
            "check": "Multiple rules for same table pair with different columns",
            "fix": "Check rule selection/ranking logic"
        },
        {
            "cause": "SQL Generation Bug",
            "description": "Rule is correct but SQL generation uses wrong column",
            "check": "Rule shows PRDID but SQL shows ZBASEMATERIAL",
            "fix": "Bug in SQL generation service - needs code fix"
        }
    ]
    
    for i, cause in enumerate(causes, 1):
        print(f"\n   Cause {i}: {cause['cause']}")
        print(f"   Description: {cause['description']}")
        print(f"   Check: {cause['check']}")
        print(f"   Fix: {cause['fix']}")

def main():
    """Main debugging function."""
    print("SQL GENERATION MISMATCH DEBUGGER")
    print("This debugs why SQL uses ZBASEMATERIAL when KG shows PRDID")
    print()
    
    debug_sql_generation_mismatch()
    analyze_possible_causes()
    
    print(f"\n{'='*60}")
    print("🎯 NEXT STEPS:")
    print("="*60)
    print("1. Check the rule generation output above")
    print("2. If rules show PRDID but SQL shows ZBASEMATERIAL → SQL generation bug")
    print("3. If rules show ZBASEMATERIAL → KG relationship being ignored")
    print("4. Try explicit pairs to confirm PRDID works")
    print("5. Check reconciliation service logs for KG relationship processing")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
