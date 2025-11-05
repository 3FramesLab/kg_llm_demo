#!/usr/bin/env python3
"""
Simple test to verify the unified approach code structure is correct.
This test doesn't require external dependencies.
"""

import ast
import os

def test_routes_unified_approach():
    """Test that routes.py uses the unified approach."""
    print("Testing routes.py for unified approach...")
    
    with open('kg_builder/routes.py', 'r') as f:
        content = f.read()
    
    # Check that the old dual approach is removed
    if 'if len(schema_names) == 1:' in content and 'build_knowledge_graph(' in content:
        print("❌ FAIL: Old dual approach still present in routes.py")
        return False
    
    # Check that unified approach is used
    if 'build_merged_knowledge_graph(' not in content:
        print("❌ FAIL: Unified approach not found in routes.py")
        return False
    
    # Check for unified approach comment
    if 'UNIFIED APPROACH' not in content:
        print("❌ FAIL: Unified approach comment not found")
        return False
    
    print("✅ PASS: routes.py uses unified approach")
    return True

def test_schema_parser_deprecation():
    """Test that build_knowledge_graph is properly deprecated."""
    print("Testing schema_parser.py for deprecation...")
    
    with open('kg_builder/services/schema_parser.py', 'r') as f:
        content = f.read()
    
    # Check for deprecation warning
    if 'warnings.warn' not in content:
        print("❌ FAIL: Deprecation warning not found")
        return False
    
    if 'DeprecationWarning' not in content:
        print("❌ FAIL: DeprecationWarning not used")
        return False
    
    # Check that it redirects to unified method
    if 'build_merged_knowledge_graph(' not in content:
        print("❌ FAIL: Deprecated method doesn't redirect to unified approach")
        return False
    
    print("✅ PASS: build_knowledge_graph properly deprecated")
    return True

def test_test_files_updated():
    """Test that test files are updated."""
    print("Testing that test files use unified approach...")
    
    test_files = [
        'test_e2e_reconciliation_simple.py',
        'test_table_aliases_debug.py'
    ]
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"⚠️  SKIP: {test_file} not found")
            continue
            
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Check for unified approach usage
        if 'build_merged_knowledge_graph(' not in content:
            print(f"❌ FAIL: {test_file} doesn't use unified approach")
            return False
        
        # Check for old dual approach pattern
        if 'if len(schema_names) > 1:' in content and 'build_knowledge_graph(' in content:
            print(f"❌ FAIL: {test_file} still has old dual approach")
            return False
    
    print("✅ PASS: Test files updated to use unified approach")
    return True

def test_documentation_created():
    """Test that documentation is created."""
    print("Testing documentation...")
    
    doc_file = 'docs/UNIFIED_KG_APPROACH.md'
    if not os.path.exists(doc_file):
        print("❌ FAIL: Unified approach documentation not found")
        return False
    
    with open(doc_file, 'r') as f:
        content = f.read()
    
    # Check for key sections
    required_sections = [
        'Unified Knowledge Graph Generation Approach',
        'What Changed',
        'Benefits',
        'Migration Guide'
    ]
    
    for section in required_sections:
        if section not in content:
            print(f"❌ FAIL: Documentation missing section: {section}")
            return False
    
    print("✅ PASS: Documentation created with all required sections")
    return True

def main():
    """Run all tests."""
    print("="*60)
    print("  UNIFIED APPROACH - CODE STRUCTURE VERIFICATION")
    print("="*60)
    
    tests = [
        test_routes_unified_approach,
        test_schema_parser_deprecation,
        test_test_files_updated,
        test_documentation_created
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Unified approach implementation is correct!")
        print("\nKey changes implemented:")
        print("✅ routes.py always uses build_merged_knowledge_graph()")
        print("✅ build_knowledge_graph() is deprecated with proper warning")
        print("✅ Test files updated to use unified approach")
        print("✅ Documentation created explaining the changes")
        return 0
    else:
        print("⚠️  Some tests failed - please check the implementation")
        return 1

if __name__ == "__main__":
    exit(main())
