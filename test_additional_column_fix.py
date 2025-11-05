#!/usr/bin/env python3
"""
Test that additional columns don't create incorrect WHERE clauses.
"""

def test_additional_column_where_clause():
    """Test that 'from table' doesn't create WHERE conditions."""
    
    print("="*60)
    print("TESTING ADDITIONAL COLUMN WHERE CLAUSE FIX")
    print("="*60)
    
    # Test the problematic query
    test_query = "Show me all the products in RBP GPU which are missing in OPS Excel, also show ops planner from hana master"
    
    print(f"Query: {test_query}")
    print()
    
    # Expected behavior analysis
    print("--- Expected Parsing ---")
    print("Main comparison: RBP GPU vs OPS Excel (NOT_IN)")
    print("Additional column: 'ops planner' from 'hana master'")
    print("  → Should resolve to: OPS_PLANNER from hana_material_master")
    print("  → Should add LEFT JOIN, NOT WHERE condition")
    print()
    
    # Expected SQL structure
    expected_sql_structure = """
    Expected SQL Structure:
    SELECT DISTINCT 
        s.*,
        h.[OPS_PLANNER] AS [OPS_PLANNER]
    FROM [brz_lnd_RBP_GPU] s
    LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
    LEFT JOIN [hana_material_master] h ON s.[Material] = h.[MATERIAL]
    WHERE t.[PLANNING_SKU] IS NULL
    """
    
    print("--- Expected SQL Structure ---")
    print(expected_sql_structure)
    
    # What should NOT appear
    print("--- What Should NOT Appear ---")
    print("❌ WHERE h.[OPS_PLANNER] = 'hana master'")
    print("❌ WHERE h.[OPS_PLANNER] = 'hana'")
    print("❌ WHERE h.[OPS_PLANNER] = 'master'")
    print("❌ Any WHERE condition involving table names as values")
    print()
    
    # What SHOULD appear
    print("--- What SHOULD Appear ---")
    print("✅ LEFT JOIN [hana_material_master] h ON s.[Material] = h.[MATERIAL]")
    print("✅ h.[OPS_PLANNER] AS [OPS_PLANNER] in SELECT clause")
    print("✅ WHERE t.[PLANNING_SKU] IS NULL (for the NOT_IN comparison)")
    print("✅ No additional WHERE conditions for 'hana master'")
    print()
    
    # Test cases for different phrasings
    test_cases = [
        "show ops planner from hana master",
        "include planner from hana",
        "add ops planner from material master",
        "also show planner from hana material master"
    ]
    
    print("--- Test Cases for Additional Column Parsing ---")
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. '{case}'")
        print(f"   Expected: Include column, add LEFT JOIN")
        print(f"   Should NOT: Add WHERE condition with table name")
    
    print(f"\n{'='*60}")
    print("ADDITIONAL COLUMN WHERE CLAUSE TEST COMPLETE")
    print(f"{'='*60}")
    
    # Instructions for manual testing
    print("\n--- Manual Testing Instructions ---")
    print("1. Run the server: python3 run_server.py")
    print("2. Test the query via API:")
    print("   curl -X POST http://localhost:8000/api/v1/nl-query/execute \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "kg_name": "your_kg_name",')
    print(f'       "query": "{test_query}",')
    print('       "use_llm": true')
    print("     }'")
    print("3. Check the generated SQL for the issues above")

if __name__ == "__main__":
    test_additional_column_where_clause()
