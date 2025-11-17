#!/usr/bin/env python3
"""
Debug script to check table matching for your KG and query.
This helps understand why the LLM confidence was 0.0.
"""

def analyze_table_matching():
    """Analyze why the LLM couldn't match tables."""
    
    print("🔍 Table Matching Analysis")
    print("="*60)
    
    # Your actual KG tables (from the logs you showed earlier)
    kg_tables = [
        'hana_material_master',
        'brz_lnd_RBP_GPU', 
        'brz_lnd_SKU_LIFNR_Excel',
        'brz_lnd_OPS_EXCEL_GPU',
        'brz_lnd_SAR_Excel_GPU',
        'brz_lnd_SAR_Excel_NBU',
        'brz_lnd_OPS_EXCEL_NBU',
        'brz_lnd_RBP_NBU',
        'brz_lnd_SAR_UNK_GPU',
        'brz_lnd_SAR_UNK_NBU'
    ]
    
    # Your query mentioned these tables
    query_tables = [
        "nbu product master",
        "hana master"
    ]
    
    print(f"📊 Available KG Tables ({len(kg_tables)}):")
    for i, table in enumerate(kg_tables, 1):
        print(f"   {i:2d}. {table}")
    
    print(f"\n🔍 Query Mentioned Tables:")
    for i, table in enumerate(query_tables, 1):
        print(f"   {i}. '{table}'")
    
    print(f"\n🤔 Table Matching Analysis:")
    
    # Check for potential matches
    potential_matches = []
    
    for query_table in query_tables:
        print(f"\n   Looking for matches for: '{query_table}'")
        matches = []
        
        for kg_table in kg_tables:
            # Check for partial matches
            if "nbu" in query_table.lower() and "nbu" in kg_table.lower():
                matches.append((kg_table, "NBU keyword match"))
            elif "hana" in query_table.lower() and "hana" in kg_table.lower():
                matches.append((kg_table, "HANA keyword match"))
            elif "master" in query_table.lower() and "master" in kg_table.lower():
                matches.append((kg_table, "Master keyword match"))
        
        if matches:
            print(f"      Potential matches:")
            for match, reason in matches:
                print(f"         - {match} ({reason})")
                potential_matches.append((query_table, match, reason))
        else:
            print(f"      ❌ No matches found")
    
    print(f"\n💡 Recommendations:")
    
    if potential_matches:
        print(f"   ✅ Found {len(potential_matches)} potential matches:")
        for query_table, kg_table, reason in potential_matches:
            print(f"      '{query_table}' → '{kg_table}' ({reason})")
        
        print(f"\n   🔧 Suggested query improvements:")
        
        # NBU tables
        nbu_tables = [t for t in kg_tables if 'nbu' in t.lower()]
        if nbu_tables:
            print(f"      For 'nbu product master', try:")
            for table in nbu_tables:
                print(f"         - '{table}'")
        
        # HANA tables  
        hana_tables = [t for t in kg_tables if 'hana' in t.lower()]
        if hana_tables:
            print(f"      For 'hana master', try:")
            for table in hana_tables:
                print(f"         - '{table}'")
    else:
        print(f"   ❌ No clear matches found")
        print(f"   💡 Try using exact table names from the KG")
    
    print(f"\n🎯 Improved Query Suggestions:")
    
    # Suggest better queries based on available tables
    if any('nbu' in t.lower() for t in kg_tables) and any('hana' in t.lower() for t in kg_tables):
        nbu_table = next((t for t in kg_tables if 'nbu' in t.lower()), 'brz_lnd_SAR_Excel_NBU')
        hana_table = next((t for t in kg_tables if 'hana' in t.lower()), 'hana_material_master')
        
        print(f"   1. 'get products from {nbu_table} and {hana_table} where planner is missing in both'")
        print(f"   2. 'find products in {hana_table} where OPS_PLANNER is null'")
        print(f"   3. 'show products from {nbu_table} with missing planner information'")
    
    return potential_matches

def suggest_column_names():
    """Suggest likely column names for 'planner'."""
    
    print(f"\n🔍 Column Name Analysis for 'planner'")
    print("="*60)
    
    # Common planner column variations
    planner_variations = [
        "OPS_PLANNER",
        "PLANNER", 
        "PLANNER_CODE",
        "PLANNER_NAME",
        "MATERIAL_PLANNER",
        "BUYER_PLANNER",
        "MRP_CONTROLLER",
        "PURCHASING_GROUP"
    ]
    
    print(f"📋 Likely column names for 'planner':")
    for i, col in enumerate(planner_variations, 1):
        print(f"   {i:2d}. {col}")
    
    print(f"\n💡 Based on your KG structure, 'OPS_PLANNER' is most likely")
    print(f"   (This appears in hana_material_master table)")
    
    return planner_variations

if __name__ == "__main__":
    print("🚀 KG Table Matching Debug Analysis")
    print("="*70)
    
    matches = analyze_table_matching()
    columns = suggest_column_names()
    
    print("\n" + "="*70)
    print("🎉 SUMMARY:")
    print(f"   📊 Found {len(matches)} potential table matches")
    print(f"   🔧 Suggested {len(columns)} planner column variations")
    print(f"\n   💡 Key Insight: Use exact table names from your KG")
    print(f"   🎯 Try: 'get products from hana_material_master where OPS_PLANNER is missing'")
    print("="*70)
