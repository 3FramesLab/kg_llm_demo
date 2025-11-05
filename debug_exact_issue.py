#!/usr/bin/env python3
"""
Debug exactly why the MATERIAL → PRDID relationship isn't being considered.
No suggestions to change the relationship - just find the blocking issue.
"""

import requests
import json

def debug_exact_blocking_issue(kg_name):
    """Find the exact reason the relationship is being ignored."""
    print("="*60)
    print("DEBUGGING EXACT BLOCKING ISSUE")
    print("="*60)
    
    try:
        # 1. Verify KG relationship exists exactly as specified
        print("\n1. CHECKING KG RELATIONSHIP EXISTS:")
        response = requests.get(f"http://localhost:8000/api/v1/kg/{kg_name}/relationships")
        
        if response.status_code != 200:
            print(f"❌ Cannot access KG '{kg_name}': {response.status_code}")
            return False
        
        relationships = response.json()
        target_rel = None
        
        for rel in relationships:
            if (rel.get('source_id') == 'hana_material_master' and 
                rel.get('target_id') == 'brz_lnd_IBP_Product_Master' and
                rel.get('source_column') == 'MATERIAL' and
                rel.get('target_column') == 'PRDID'):
                target_rel = rel
                break
        
        if not target_rel:
            print("❌ RELATIONSHIP NOT FOUND IN KG")
            print("   Looking for:")
            print("   - source_id: hana_material_master")
            print("   - target_id: brz_lnd_IBP_Product_Master") 
            print("   - source_column: MATERIAL")
            print("   - target_column: PRDID")
            print("\n   Available relationships:")
            for rel in relationships[:5]:
                print(f"   - {rel.get('source_id')} → {rel.get('target_id')}")
                print(f"     {rel.get('source_column')} → {rel.get('target_column')}")
            return False
        
        print("✅ RELATIONSHIP FOUND IN KG:")
        print(f"   Type: {target_rel.get('relationship_type')}")
        print(f"   Confidence: {target_rel.get('properties', {}).get('confidence')}")
        print(f"   Forward: {target_rel.get('properties', {}).get('forward')}")
        print(f"   Explicit: {target_rel.get('properties', {}).get('explicit')}")
        
        # 2. Check schema availability
        print("\n2. CHECKING SCHEMA AVAILABILITY:")
        response = requests.get("http://localhost:8000/api/v1/schemas")
        
        if response.status_code != 200:
            print(f"❌ Cannot access schemas: {response.status_code}")
            return False
        
        schemas = response.json()
        schema_found = False
        
        for schema_name, schema_data in schemas.items():
            tables = schema_data.get('tables', {})
            if 'hana_material_master' in tables and 'brz_lnd_IBP_Product_Master' in tables:
                schema_found = True
                print(f"✅ SCHEMA FOUND: {schema_name}")
                
                # Check columns exist
                hana_cols = [col['name'] for col in tables['hana_material_master'].get('columns', [])]
                ibp_cols = [col['name'] for col in tables['brz_lnd_IBP_Product_Master'].get('columns', [])]
                
                material_exists = 'MATERIAL' in hana_cols
                prdid_exists = 'PRDID' in ibp_cols
                
                print(f"   MATERIAL column exists: {'✅' if material_exists else '❌'}")
                print(f"   PRDID column exists: {'✅' if prdid_exists else '❌'}")
                
                if not material_exists or not prdid_exists:
                    print("❌ MISSING COLUMNS - This is the blocking issue!")
                    if not material_exists:
                        print(f"   Available in hana_material_master: {hana_cols[:10]}")
                    if not prdid_exists:
                        print(f"   Available in brz_lnd_IBP_Product_Master: {ibp_cols[:10]}")
                    return False
                break
        
        if not schema_found:
            print("❌ SCHEMA NOT FOUND containing both tables")
            print("   Available schemas:")
            for schema_name in schemas.keys():
                print(f"   - {schema_name}")
            return False
        
        # 3. Test rule generation with minimal config
        print("\n3. TESTING RULE GENERATION:")
        test_config = {
            "kg_name": kg_name,
            "schema_names": [schema_name],
            "use_llm_enhancement": False,  # Disable LLM to isolate issue
            "min_confidence": 0.1,  # Very low threshold
            "auto_discover_additional": True,
            "max_rules": 100
        }
        
        print(f"   Using config: {json.dumps(test_config, indent=2)}")
        
        response = requests.post(
            "http://localhost:8000/api/v1/reconciliation/generate",
            json=test_config,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ RULE GENERATION FAILED: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        result = response.json()
        rules = result.get('rules', [])
        
        print(f"✅ GENERATED {len(rules)} RULES")
        
        # Look for our specific rule
        found_rule = None
        for rule in rules:
            if (rule.get('source_table') == 'hana_material_master' and 
                rule.get('target_table') == 'brz_lnd_IBP_Product_Master'):
                found_rule = rule
                break
        
        if found_rule:
            print("✅ RULE FOUND:")
            print(f"   Source columns: {found_rule.get('source_columns')}")
            print(f"   Target columns: {found_rule.get('target_columns')}")
            print(f"   Match type: {found_rule.get('match_type')}")
            print(f"   Confidence: {found_rule.get('confidence_score')}")
            
            # Check if it's the right columns
            if ('MATERIAL' in found_rule.get('source_columns', []) and 
                'PRDID' in found_rule.get('target_columns', [])):
                print("✅ CORRECT COLUMNS MATCHED!")
                print("   Your relationship IS being considered!")
            else:
                print("❌ WRONG COLUMNS:")
                print(f"   Expected: MATERIAL → PRDID")
                print(f"   Got: {found_rule.get('source_columns')} → {found_rule.get('target_columns')}")
        else:
            print("❌ NO RULE GENERATED for hana_material_master → brz_lnd_IBP_Product_Master")
            print("   This means the relationship is being filtered out")
            
            # Show what rules were generated
            print("\n   Generated rules:")
            for i, rule in enumerate(rules[:5], 1):
                print(f"   {i}. {rule.get('source_table')} → {rule.get('target_table')}")
                print(f"      {rule.get('source_columns')} → {rule.get('target_columns')}")
        
        # 4. Check reconciliation service logs/debug info
        print("\n4. CHECKING SERVICE STATUS:")
        response = requests.get("http://localhost:8000/api/v1/health")
        if response.status_code == 200:
            print("✅ Service is healthy")
        else:
            print(f"⚠️  Service health check failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main debugging function."""
    print("EXACT ISSUE DEBUGGER")
    print("This will find exactly why your MATERIAL → PRDID relationship isn't working")
    print("No suggestions to change anything - just diagnosis")
    print()
    
    kg_name = input("Enter your KG name: ").strip()
    if not kg_name:
        print("❌ KG name is required")
        return
    
    success = debug_exact_blocking_issue(kg_name)
    
    print(f"\n{'='*60}")
    if success:
        print("🔍 DIAGNOSIS COMPLETE")
        print("Check the output above for the exact blocking issue")
    else:
        print("❌ DIAGNOSIS FAILED")
        print("Could not complete the analysis")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
