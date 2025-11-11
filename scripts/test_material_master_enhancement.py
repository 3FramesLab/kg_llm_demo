#!/usr/bin/env python3
"""
Test Material Master Enhancement
Verifies that material tables automatically get hana_material_master joins and ops_planner columns.
"""

import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kg_builder.services.material_master_enhancer import material_master_enhancer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_material_master_enhancement():
    """Test the material master enhancement functionality."""
    
    print("="*80)
    print("🧪 TESTING MATERIAL MASTER ENHANCEMENT")
    print("="*80)
    
    # Test cases with different SQL patterns
    test_cases = [
        {
            'name': 'RBP GPU query (should be enhanced)',
            'sql': '''SELECT r.Material, r.Product_Line, r.Business_Unit
FROM brz_lnd_RBP_GPU r
WHERE r.Business_Unit = 'GPU_BUSINESS' ''',
            'should_enhance': True,
            'expected_material_master': True,
            'expected_ops_planner': True
        },
        {
            'name': 'OPS Excel GPU query (should be enhanced)',
            'sql': '''SELECT o.PLANNING_SKU, o.Customer, o.Demand_Qty
FROM brz_lnd_OPS_EXCEL_GPU o
WHERE o.Customer = 'NVIDIA' ''',
            'should_enhance': True,
            'expected_material_master': True,
            'expected_ops_planner': True
        },
        {
            'name': 'RBP vs OPS comparison (should be enhanced)',
            'sql': '''SELECT r.Material, o.PLANNING_SKU, r.Product_Line
FROM brz_lnd_RBP_GPU r
LEFT JOIN brz_lnd_OPS_EXCEL_GPU o ON r.Material = o.PLANNING_SKU
WHERE r.Business_Unit = 'GPU_BUSINESS' ''',
            'should_enhance': True,
            'expected_material_master': True,
            'expected_ops_planner': True
        },
        {
            'name': 'Query with hana_material_master already present',
            'sql': '''SELECT r.Material, r.Product_Line, h.MATERIAL
FROM brz_lnd_RBP_GPU r
INNER JOIN hana_material_master h ON r.Material = h.MATERIAL
WHERE r.Business_Unit = 'GPU_BUSINESS' ''',
            'should_enhance': True,
            'expected_material_master': False,  # Already present
            'expected_ops_planner': True
        },
        {
            'name': 'Non-material query (should not be enhanced)',
            'sql': '''SELECT user_id, login_time, session_duration
FROM user_sessions
WHERE login_time > '2024-01-01' ''',
            'should_enhance': False,
            'expected_material_master': False,
            'expected_ops_planner': False
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
        enhancement_result = material_master_enhancer.enhance_sql_with_material_master(test_case['sql'])
        
        print("📊 Enhancement Result:")
        print(f"  • Enhancement applied: {enhancement_result['enhancement_applied']}")
        print(f"  • Material master added: {enhancement_result['material_master_added']}")
        print(f"  • OPS_PLANNER added: {enhancement_result['ops_planner_added']}")
        
        if 'material_tables_detected' in enhancement_result:
            print(f"  • Material tables detected: {enhancement_result['material_tables_detected']}")
        
        if 'reason' in enhancement_result:
            print(f"  • Reason: {enhancement_result['reason']}")
        
        if 'error' in enhancement_result:
            print(f"  • Error: {enhancement_result['error']}")
        
        print()
        print("🔧 Enhanced SQL:")
        print(enhancement_result['enhanced_sql'])
        
        # Verify expectations
        expected_enhancement = test_case['should_enhance']
        actual_enhancement = enhancement_result['enhancement_applied']
        
        expected_material_master = test_case['expected_material_master']
        actual_material_master = enhancement_result['material_master_added']
        
        expected_ops_planner = test_case['expected_ops_planner']
        actual_ops_planner = enhancement_result['ops_planner_added']
        
        # Check if enhanced SQL contains expected elements
        enhanced_sql_lower = enhancement_result['enhanced_sql'].lower()
        has_hana_master = 'hana_material_master' in enhanced_sql_lower
        has_ops_planner = 'ops_planner' in enhanced_sql_lower
        
        test_passed = True
        issues = []
        
        if expected_enhancement != actual_enhancement:
            test_passed = False
            issues.append(f"Enhancement expected: {expected_enhancement}, actual: {actual_enhancement}")
        
        if expected_material_master != actual_material_master:
            test_passed = False
            issues.append(f"Material master expected: {expected_material_master}, actual: {actual_material_master}")
        
        if expected_ops_planner != actual_ops_planner:
            test_passed = False
            issues.append(f"OPS_PLANNER expected: {expected_ops_planner}, actual: {actual_ops_planner}")
        
        # Additional checks for SQL content
        if test_case['should_enhance']:
            if not has_hana_master and expected_material_master:
                test_passed = False
                issues.append("Enhanced SQL should contain hana_material_master")
            
            if not has_ops_planner and expected_ops_planner:
                test_passed = False
                issues.append("Enhanced SQL should contain ops_planner")
        
        status = "✅ PASS" if test_passed else "❌ FAIL"
        results.append(test_passed)
        
        print(f"\n🎯 Test result: {status}")
        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"   - {issue}")
    
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
        print("\n🎉 ALL TESTS PASSED! Material Master enhancement is working correctly.")
        print("✅ Material tables will automatically get hana_material_master joins")
        print("✅ OPS_PLANNER column will be automatically included")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the implementation.")
        return False


def main():
    """Run all tests."""
    
    print("🚀 Starting Material Master Enhancement Tests")
    print(f"Timestamp: {__import__('datetime').datetime.now()}")
    
    # Test the enhancement functionality
    test_passed = test_material_master_enhancement()
    
    # Overall result
    print(f"\n{'='*80}")
    print("🏁 FINAL RESULTS")
    print(f"{'='*80}")
    
    if test_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Material Master enhancement is fully working")
        print("✅ OPS_PLANNER will now appear in generated SQL")
        print("✅ Ready for production use")
        return True
    else:
        print("⚠️ SOME TESTS FAILED")
        print("❌ Please review the implementation before deploying")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
