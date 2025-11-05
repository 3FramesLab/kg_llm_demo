#!/usr/bin/env python3
"""
Debug script to check if KG relationships are being considered during rule generation.
"""

import requests
import json

def check_kg_relationships(kg_name="your_kg_name"):
    """Check what relationships exist in the knowledge graph."""
    print("="*60)
    print("DEBUGGING KG RELATIONSHIP CONSIDERATION")
    print("="*60)
    
    try:
        # 1. Check if KG exists and get relationships
        print(f"\n1. Checking KG '{kg_name}' relationships...")
        
        response = requests.get(
            f"http://localhost:8000/api/v1/kg/{kg_name}/relationships",
            timeout=30
        )
        
        if response.status_code == 200:
            relationships = response.json()
            print(f"✅ Found {len(relationships)} relationships in KG")
            
            # Look for the specific relationship (MATERIAL → PRDID)
            target_relationship = None
            for rel in relationships:
                if (rel.get('source_id') == 'hana_material_master' and
                    rel.get('target_id') == 'brz_lnd_IBP_Product_Master' and
                    rel.get('source_column') == 'MATERIAL' and
                    rel.get('target_column') == 'PRDID'):
                    target_relationship = rel
                    break
            
            if target_relationship:
                print(f"\n✅ Found target relationship:")
                print(f"   Source: {target_relationship.get('source_id')}")
                print(f"   Target: {target_relationship.get('target_id')}")
                print(f"   Type: {target_relationship.get('relationship_type')}")
                print(f"   Source Column: {target_relationship.get('source_column')}")
                print(f"   Target Column: {target_relationship.get('target_column')}")
                print(f"   Properties: {json.dumps(target_relationship.get('properties', {}), indent=2)}")
            else:
                print(f"\n❌ Target relationship NOT FOUND in KG")
                print(f"   Looking for: hana_material_master → brz_lnd_IBP_Product_Master")
                
                # Show what relationships DO exist
                print(f"\n📋 Available relationships:")
                for i, rel in enumerate(relationships[:10], 1):  # Show first 10
                    print(f"   {i}. {rel.get('source_id')} → {rel.get('target_id')}")
                    print(f"      Type: {rel.get('relationship_type')}")
                    print(f"      Columns: {rel.get('source_column')} → {rel.get('target_column')}")
                
                if len(relationships) > 10:
                    print(f"   ... and {len(relationships) - 10} more")
        
        else:
            print(f"❌ Failed to get KG relationships: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # 2. Test rule generation with explicit pairs
        print(f"\n2. Testing rule generation with explicit pairs...")
        
        rule_request = {
            "kg_name": kg_name,
            "schema_names": ["newdqschemanov"],  # Adjust to your schema name
            "use_llm_enhancement": True,
            "min_confidence": 0.7,
            "reconciliation_pairs": [
                {
                    "source_table": "hana_material_master",
                    "source_columns": ["MATERIAL"],
                    "target_table": "brz_lnd_IBP_Product_Master",
                    "target_columns": ["PRDID"],  # Keep existing column as requested
                    "match_type": "exact",
                    "bidirectional": True
                }
            ],
            "auto_discover_additional": True
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/reconciliation/generate",
            json=rule_request,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            rules = result.get('rules', [])
            print(f"✅ Generated {len(rules)} reconciliation rules")
            
            # Look for our specific rule
            target_rule = None
            for rule in rules:
                if (rule.get('source_table') == 'hana_material_master' and 
                    rule.get('target_table') == 'brz_lnd_IBP_Product_Master'):
                    target_rule = rule
                    break
            
            if target_rule:
                print(f"\n✅ Found target rule:")
                print(f"   Rule ID: {target_rule.get('rule_id')}")
                print(f"   Source: {target_rule.get('source_table')}.{target_rule.get('source_columns')}")
                print(f"   Target: {target_rule.get('target_table')}.{target_rule.get('target_columns')}")
                print(f"   Match Type: {target_rule.get('match_type')}")
                print(f"   Confidence: {target_rule.get('confidence_score')}")
                print(f"   Reasoning: {target_rule.get('reasoning')}")
            else:
                print(f"\n❌ Target rule NOT GENERATED")
                print(f"   Expected: hana_material_master → brz_lnd_IBP_Product_Master")
                
                # Show what rules were generated
                print(f"\n📋 Generated rules:")
                for i, rule in enumerate(rules[:5], 1):  # Show first 5
                    print(f"   {i}. {rule.get('source_table')} → {rule.get('target_table')}")
                    print(f"      Columns: {rule.get('source_columns')} → {rule.get('target_columns')}")
                    print(f"      Confidence: {rule.get('confidence_score')}")
        
        else:
            print(f"❌ Failed to generate rules: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # 3. Check schema information
        print(f"\n3. Checking schema information...")
        
        response = requests.get(
            f"http://localhost:8000/api/v1/schemas",
            timeout=30
        )
        
        if response.status_code == 200:
            schemas = response.json()
            print(f"✅ Found {len(schemas)} schemas")
            
            # Look for our tables
            for schema_name, schema_info in schemas.items():
                if 'newdq' in schema_name.lower():
                    tables = schema_info.get('tables', {})
                    print(f"\n📋 Schema '{schema_name}' has {len(tables)} tables:")
                    
                    # Check specific tables
                    if 'hana_material_master' in tables:
                        hana_cols = [col['name'] for col in tables['hana_material_master'].get('columns', [])]
                        print(f"   ✅ hana_material_master: {len(hana_cols)} columns")
                        if 'MATERIAL' in hana_cols:
                            print(f"      ✅ MATERIAL column exists")
                        else:
                            print(f"      ❌ MATERIAL column missing")
                    
                    if 'brz_lnd_IBP_Product_Master' in tables:
                        ibp_cols = [col['name'] for col in tables['brz_lnd_IBP_Product_Master'].get('columns', [])]
                        print(f"   ✅ brz_lnd_IBP_Product_Master: {len(ibp_cols)} columns")
                        if 'ZBASEMATERIAL' in ibp_cols:
                            print(f"      ✅ ZBASEMATERIAL column exists")
                        else:
                            print(f"      ❌ ZBASEMATERIAL column missing")
                        if 'PRDID' in ibp_cols:
                            print(f"      ✅ PRDID column exists")
        
        else:
            print(f"❌ Failed to get schemas: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return False

def main():
    """Main debugging function."""
    print("KG Relationship Debugging Tool")
    print("This tool checks why KG relationships aren't being considered")
    print()
    
    # You may need to adjust the KG name
    kg_name = input("Enter your KG name (or press Enter for 'demo_kg'): ").strip()
    if not kg_name:
        kg_name = "demo_kg"
    
    success = check_kg_relationships(kg_name)
    
    print(f"\n{'='*60}")
    if success:
        print("🔍 DEBUGGING COMPLETED")
        print("Check the output above for issues with:")
        print("1. KG relationship existence")
        print("2. Rule generation process") 
        print("3. Schema column availability")
    else:
        print("❌ DEBUGGING FAILED")
        print("Check API server connection and try again")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
