#!/usr/bin/env python3
"""
Test that aliases work correctly with main table selection fix.
"""

def test_aliases_integration():
    """Test that aliases are properly integrated with main table selection."""
    
    print("="*60)
    print("TESTING ALIASES INTEGRATION WITH MAIN TABLE FIX")
    print("="*60)
    
    # Simulate KG table aliases (format: {table_name: [alias1, alias2]})
    kg_table_aliases = {
        'brz_lnd_IBP_Product_Master': ['IBP', 'Product Master', 'IBP Master'],
        'brz_lnd_RBP_GPU': ['RBP', 'RBP GPU', 'GPU'],
        'brz_lnd_OPS_EXCEL_GPU': ['OPS', 'OPS Excel', 'Excel GPU'],
        'brz_lnd_SKU_LIFNR_Excel': ['SKU', 'LIFNR', 'Supplier'],
        'hana_material_master': ['HANA', 'Material Master', 'HANA Master']
    }
    
    # Test alias formatting for LLM prompt
    print("\n--- Test 1: Alias Formatting for LLM Prompt ---")
    aliases_info = []
    for actual_table, alias_list in kg_table_aliases.items():
        for alias in alias_list:
            aliases_info.append(f"  • \"{alias}\" → {actual_table}")
    
    aliases_str = "\n".join(aliases_info)
    print("Formatted aliases for LLM prompt:")
    print(aliases_str)
    
    # Test table priority with aliases
    print("\n--- Test 2: Table Priority Logic with Aliases ---")
    
    table_priorities = {
        'brz_lnd_IBP_Product_Master': 10,
        'brz_lnd_RBP_GPU': 9,
        'brz_lnd_OPS_EXCEL_GPU': 8,
        'brz_lnd_SKU_LIFNR_Excel': 7,
        'hana_material_master': 1  # Low priority - should be enrichment only
    }
    
    # Simulate table resolution (alias → actual table name)
    def resolve_alias(alias):
        """Simulate table name resolution."""
        for table_name, aliases in kg_table_aliases.items():
            if alias.lower() in [a.lower() for a in aliases]:
                return table_name
        return alias  # Return as-is if not found
    
    # Test cases with aliases
    test_cases = [
        {
            'name': 'Query with HANA alias (should swap)',
            'source_alias': 'HANA',
            'target_alias': 'IBP',
            'expected_main_table': 'brz_lnd_IBP_Product_Master'
        },
        {
            'name': 'Query with Material Master alias (should swap)',
            'source_alias': 'Material Master',
            'target_alias': 'RBP',
            'expected_main_table': 'brz_lnd_RBP_GPU'
        },
        {
            'name': 'Query with RBP alias (should not swap)',
            'source_alias': 'RBP',
            'target_alias': 'HANA',
            'expected_main_table': 'brz_lnd_RBP_GPU'
        },
        {
            'name': 'Query with IBP alias (should not swap)',
            'source_alias': 'IBP',
            'target_alias': 'Material Master',
            'expected_main_table': 'brz_lnd_IBP_Product_Master'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Test {i}: {test_case['name']}")
        
        # Resolve aliases to actual table names
        source_table = resolve_alias(test_case['source_alias'])
        target_table = resolve_alias(test_case['target_alias'])
        
        print(f"    Aliases: '{test_case['source_alias']}' → {source_table}, '{test_case['target_alias']}' → {target_table}")
        
        # Apply table priority logic
        if (source_table == 'hana_material_master' and 
            target_table and 
            table_priorities.get(target_table, 0) > table_priorities.get(source_table, 0)):
            
            # Swap
            main_table = target_table
            enrichment_table = source_table
            print(f"    🔄 Swapped: main={main_table}, enrichment={enrichment_table}")
        else:
            main_table = source_table
            enrichment_table = target_table
            print(f"    ✓ No swap: main={main_table}, enrichment={enrichment_table}")
        
        # Check result
        if main_table == test_case['expected_main_table']:
            print(f"    ✅ PASS: Correct main table selected")
        else:
            print(f"    ❌ FAIL: Expected {test_case['expected_main_table']}, got {main_table}")
    
    print(f"\n{'='*60}")
    print("ALIASES + MAIN TABLE SELECTION TEST COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_aliases_integration()
