#!/usr/bin/env python3
"""
Simple test to verify table priority logic without full environment.
"""

def test_table_priority_logic():
    """Test the table priority logic we added."""
    
    # Define table priorities (same as in the code)
    table_priorities = {
        'brz_lnd_IBP_Product_Master': 10,
        'brz_lnd_RBP_GPU': 9,
        'brz_lnd_OPS_EXCEL_GPU': 8,
        'brz_lnd_SKU_LIFNR_Excel': 7,
        'hana_material_master': 1  # Low priority - should be enrichment only
    }
    
    print("="*60)
    print("TESTING TABLE PRIORITY LOGIC")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            'name': 'hana_material_master as source (should swap)',
            'source': 'hana_material_master',
            'target': 'brz_lnd_IBP_Product_Master',
            'expected_source': 'brz_lnd_IBP_Product_Master',
            'expected_target': 'hana_material_master'
        },
        {
            'name': 'hana_material_master as source with RBP (should swap)',
            'source': 'hana_material_master', 
            'target': 'brz_lnd_RBP_GPU',
            'expected_source': 'brz_lnd_RBP_GPU',
            'expected_target': 'hana_material_master'
        },
        {
            'name': 'IBP as source (should not swap)',
            'source': 'brz_lnd_IBP_Product_Master',
            'target': 'hana_material_master',
            'expected_source': 'brz_lnd_IBP_Product_Master',
            'expected_target': 'hana_material_master'
        },
        {
            'name': 'RBP as source (should not swap)',
            'source': 'brz_lnd_RBP_GPU',
            'target': 'hana_material_master',
            'expected_source': 'brz_lnd_RBP_GPU',
            'expected_target': 'hana_material_master'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        
        source = test_case['source']
        target = test_case['target']
        
        print(f"Original: source={source}, target={target}")
        
        # Apply the logic
        if (source == 'hana_material_master' and 
            target and 
            table_priorities.get(target, 0) > table_priorities.get(source, 0)):
            
            # Swap
            source, target = target, source
            print(f"🔄 Swapped: source={source}, target={target}")
        else:
            print(f"✓ No swap needed: source={source}, target={target}")
        
        # Check result
        if (source == test_case['expected_source'] and 
            target == test_case['expected_target']):
            print("✅ PASS: Table priority logic worked correctly")
        else:
            print(f"❌ FAIL: Expected source={test_case['expected_source']}, target={test_case['expected_target']}")
    
    print(f"\n{'='*60}")
    print("TABLE PRIORITY LOGIC TEST COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_table_priority_logic()
