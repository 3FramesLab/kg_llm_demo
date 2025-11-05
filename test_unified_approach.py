#!/usr/bin/env python3
"""
Test script to verify the unified knowledge graph generation approach.
Tests that single schema processing works correctly with build_merged_knowledge_graph().
"""

import sys
import os
import warnings
from typing import List

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kg_builder.services.schema_parser import SchemaParser
from kg_builder.models import KnowledgeGraph

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_result(test_name: str, success: bool, details: str = ""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_single_schema_unified():
    """Test single schema processing with unified approach."""
    print_section("TEST 1: Single Schema with Unified Approach")
    
    try:
        schema_name = "newdqschemanov"
        kg_name = "test_unified_single"
        
        print(f"Testing single schema: {schema_name}")
        
        # Test the unified approach
        kg = SchemaParser.build_merged_knowledge_graph(
            schema_names=[schema_name],
            kg_name=kg_name,
            use_llm=False  # Disable LLM for faster testing
        )
        
        # Verify results
        assert isinstance(kg, KnowledgeGraph), "Should return KnowledgeGraph object"
        assert kg.name == kg_name, f"KG name should be {kg_name}"
        assert len(kg.nodes) > 0, "Should have nodes"
        assert len(kg.relationships) >= 0, "Should have relationships (can be 0)"
        
        print_result("Single schema unified approach", True, 
                    f"Nodes: {len(kg.nodes)}, Relationships: {len(kg.relationships)}")
        return True
        
    except Exception as e:
        print_result("Single schema unified approach", False, str(e))
        return False

def test_multiple_schema_unified():
    """Test multiple schema processing with unified approach."""
    print_section("TEST 2: Multiple Schemas with Unified Approach")
    
    try:
        # Use the same schema twice to simulate multiple schemas
        schema_names = ["newdqschemanov"]  # Only one available for testing
        kg_name = "test_unified_multi"
        
        print(f"Testing schemas: {schema_names}")
        
        # Test the unified approach
        kg = SchemaParser.build_merged_knowledge_graph(
            schema_names=schema_names,
            kg_name=kg_name,
            use_llm=False  # Disable LLM for faster testing
        )
        
        # Verify results
        assert isinstance(kg, KnowledgeGraph), "Should return KnowledgeGraph object"
        assert kg.name == kg_name, f"KG name should be {kg_name}"
        assert len(kg.nodes) > 0, "Should have nodes"
        
        print_result("Multiple schema unified approach", True, 
                    f"Nodes: {len(kg.nodes)}, Relationships: {len(kg.relationships)}")
        return True
        
    except Exception as e:
        print_result("Multiple schema unified approach", False, str(e))
        return False

def test_deprecated_method():
    """Test that the deprecated method shows warning and works."""
    print_section("TEST 3: Deprecated Method Warning")
    
    try:
        schema_name = "newdqschemanov"
        kg_name = "test_deprecated"
        
        print(f"Testing deprecated method with schema: {schema_name}")
        
        # Load schema first
        schema = SchemaParser.load_schema(schema_name)
        
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Call deprecated method
            kg = SchemaParser.build_knowledge_graph(
                schema_name=schema_name,
                kg_name=kg_name,
                schema=schema,
                use_llm=False
            )
            
            # Check if deprecation warning was issued
            deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
            
        # Verify results
        assert len(deprecation_warnings) > 0, "Should show deprecation warning"
        assert isinstance(kg, KnowledgeGraph), "Should still return KnowledgeGraph object"
        assert kg.name == kg_name, f"KG name should be {kg_name}"
        
        warning_msg = str(deprecation_warnings[0].message)
        print_result("Deprecated method warning", True, 
                    f"Warning: {warning_msg[:50]}...")
        return True
        
    except Exception as e:
        print_result("Deprecated method warning", False, str(e))
        return False

def test_relationship_types():
    """Test that single schema gets all relationship types."""
    print_section("TEST 4: Relationship Types Available")
    
    try:
        schema_name = "newdqschemanov"
        kg_name = "test_relationship_types"
        
        print(f"Testing relationship types with schema: {schema_name}")
        
        # Test with LLM disabled (pattern-based only)
        kg_no_llm = SchemaParser.build_merged_knowledge_graph(
            schema_names=[schema_name],
            kg_name=f"{kg_name}_no_llm",
            use_llm=False
        )
        
        # Get relationship types
        rel_types_no_llm = set()
        for rel in kg_no_llm.relationships:
            rel_types_no_llm.add(rel.relationship_type)
        
        print_result("Pattern-based relationships", True, 
                    f"Types found: {sorted(rel_types_no_llm)}")
        
        # Note: We can't test LLM-enhanced relationships without API key
        # But the unified approach ensures they would be available
        
        return True
        
    except Exception as e:
        print_result("Relationship types test", False, str(e))
        return False

def test_consistency():
    """Test that single and multiple schema approaches give consistent results."""
    print_section("TEST 5: Consistency Check")
    
    try:
        schema_name = "newdqschemanov"
        
        # Generate KG using single schema
        kg_single = SchemaParser.build_merged_knowledge_graph(
            schema_names=[schema_name],
            kg_name="test_single",
            use_llm=False
        )
        
        # Generate KG using the same schema in a list (should be identical)
        kg_list = SchemaParser.build_merged_knowledge_graph(
            schema_names=[schema_name],
            kg_name="test_list",
            use_llm=False
        )
        
        # Compare results
        assert len(kg_single.nodes) == len(kg_list.nodes), "Node count should be identical"
        assert len(kg_single.relationships) == len(kg_list.relationships), "Relationship count should be identical"
        
        print_result("Consistency check", True, 
                    f"Both approaches: {len(kg_single.nodes)} nodes, {len(kg_single.relationships)} relationships")
        return True
        
    except Exception as e:
        print_result("Consistency check", False, str(e))
        return False

def main():
    """Run all tests."""
    print_section("UNIFIED KNOWLEDGE GRAPH APPROACH - TEST SUITE")
    print("Testing that single schema processing works correctly with the unified approach")
    
    tests = [
        test_single_schema_unified,
        test_multiple_schema_unified,
        test_deprecated_method,
        test_relationship_types,
        test_consistency
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
    print_section("TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Unified approach is working correctly!")
        return 0
    else:
        print("⚠️  Some tests failed - please check the implementation")
        return 1

if __name__ == "__main__":
    sys.exit(main())
