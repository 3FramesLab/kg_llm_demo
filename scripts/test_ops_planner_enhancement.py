#!/usr/bin/env python3
"""
Test OPS_PLANNER Enhancement Integration
Verifies that ops_planner column is automatically added to all SQL queries involving hana_material_master.
"""

import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kg_builder.services.sql_ops_planner_enhancer import ops_planner_enhancer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_ops_planner_enhancement():
    """Test the ops_planner enhancement functionality."""
    
    print("="*80)
    print("🧪 TESTING OPS_PLANNER ENHANCEMENT")
    print("="*80)
    
    # Test cases with different SQL patterns
    test_cases = [
        {
            'name': 'Simple SELECT with hana_material_master',
            'sql': '''SELECT Material, Product_Line 
FROM hana_material_master 
WHERE Product_Type = 'GPU' ''',
            'should_enhance': True
        },
        {
            'name': 'JOIN with hana_material_master (with alias)',
            'sql': '''SELECT r.Material, r.Product_Line, o.PLANNING_SKU
FROM brz_lnd_RBP_GPU r
INNER JOIN hana_material_master h ON r.Material = h.MATERIAL
WHERE h.Product_Type = 'GPU' ''',
            'should_enhance': True
        },
        {
            'name': 'Complex query with multiple tables including hana_material_master',
            'sql': '''SELECT DISTINCT r.Material, r.Product_Family, o.Customer
FROM brz_lnd_RBP_GPU r
LEFT JOIN brz_lnd_OPS_EXCEL_GPU o ON r.Material = o.PLANNING_SKU
INNER JOIN hana_material_master hm ON r.Material = hm.MATERIAL
WHERE hm.Product_Type = 'GPU' AND r.Business_Unit = 'GPU_BUSINESS' ''',
            'should_enhance': True
        },
        {
            'name': 'Query without hana_material_master',
            'sql': '''SELECT r.Material, o.PLANNING_SKU
FROM brz_lnd_RBP_GPU r
LEFT JOIN brz_lnd_OPS_EXCEL_GPU o ON r.Material = o.PLANNING_SKU
WHERE r.Business_Unit = 'GPU_BUSINESS' ''',
            'should_enhance': False
        },
        {
            'name': 'Query with ops_planner already included',
            'sql': '''SELECT h.Material, h.Product_Line, h.OPS_PLANNER as ops_planner
FROM hana_material_master h
WHERE h.Product_Type = 'GPU' ''',
            'should_enhance': False  # Already has ops_planner
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🧪 Test Case {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        print("📝 Original SQL:")
        print(test_case['sql'])
        print()
        
        # Test the enhancement
        enhancement_result = ops_planner_enhancer.enhance_sql(test_case['sql'])
        
        print("📊 Enhancement Result:")
        print(f"  • Involves hana_material_master: {enhancement_result['involves_hana_master']}")
        print(f"  • Enhancement applied: {enhancement_result['enhancement_applied']}")
        print(f"  • OPS_PLANNER added: {enhancement_result['ops_planner_added']}")
        
        if 'hana_alias' in enhancement_result:
            print(f"  • Hana alias detected: {enhancement_result['hana_alias']}")
        
        if 'error' in enhancement_result:
            print(f"  • Error: {enhancement_result['error']}")
        
        print()
        print("🔧 Enhanced SQL:")
        print(enhancement_result['enhanced_sql'])
        
        # Verify expectations
        expected_enhancement = test_case['should_enhance']
        actual_enhancement = enhancement_result['enhancement_applied']
        
        if expected_enhancement == actual_enhancement:
            status = "✅ PASS"
            results.append(True)
        else:
            status = "❌ FAIL"
            results.append(False)
        
        print(f"\n🎯 Expected enhancement: {expected_enhancement}")
        print(f"🎯 Actual enhancement: {actual_enhancement}")
        print(f"🎯 Test result: {status}")
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! OPS_PLANNER enhancement is working correctly.")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the implementation.")
        return False


def test_integration_with_sql_generators():
    """Test integration with actual SQL generators."""
    
    print(f"\n{'='*80}")
    print("🔗 TESTING INTEGRATION WITH SQL GENERATORS")
    print(f"{'='*80}")
    
    try:
        # Test with NL SQL Generator
        from kg_builder.services.nl_sql_generator import NLSQLGenerator
        from kg_builder.services.nl_query_parser import QueryIntent
        
        print("🧪 Testing Python SQL Generator integration...")
        
        # Create a mock intent that would involve hana_material_master
        intent = QueryIntent(
            definition="Show products from hana master",
            query_type="data_query",
            operation="SELECT",
            source_table="hana_material_master",
            target_table=None,
            join_columns=[],
            filters=[],
            confidence=0.9
        )
        
        generator = NLSQLGenerator(db_type="sqlserver", use_llm=False)
        sql = generator.generate(intent)
        
        print("📝 Generated SQL:")
        print(sql)
        
        # Check if ops_planner was added
        if 'ops_planner' in sql.lower():
            print("✅ OPS_PLANNER successfully integrated with Python SQL Generator")
            return True
        else:
            print("❌ OPS_PLANNER not found in generated SQL")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    
    print("🚀 Starting OPS_PLANNER Enhancement Tests")
    print(f"Timestamp: {__import__('datetime').datetime.now()}")
    
    # Test 1: Core enhancement functionality
    test1_passed = test_ops_planner_enhancement()
    
    # Test 2: Integration with SQL generators
    test2_passed = test_integration_with_sql_generators()
    
    # Overall result
    print(f"\n{'='*80}")
    print("🏁 FINAL RESULTS")
    print(f"{'='*80}")
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ OPS_PLANNER enhancement is fully integrated and working")
        print("✅ Ready for production use")
        return True
    else:
        print("⚠️ SOME TESTS FAILED")
        print("❌ Please review the implementation before deploying")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
