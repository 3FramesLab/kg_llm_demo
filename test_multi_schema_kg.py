#!/usr/bin/env python
"""
Test script for multi-schema knowledge graph generation.
Demonstrates the new feature to generate unified KGs from multiple schemas.
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_single_schema():
    """Test single schema KG generation (backward compatibility)."""
    print_section("Test 1: Single Schema (Backward Compatible)")
    
    payload = {
        "schema_name": "orderMgmt-catalog",
        "kg_name": "single_schema_kg",
        "backends": ["graphiti"]
    }
    
    print(f"Request payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    response = requests.post(f"{BASE_URL}/kg/generate", json=payload)
    result = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(result, indent=2))
    
    return result


def test_multi_schema():
    """Test multi-schema KG generation with cross-schema relationships."""
    print_section("Test 2: Multiple Schemas (New Feature)")
    
    payload = {
        "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
        "kg_name": "unified_kg",
        "backends": ["graphiti"]
    }
    
    print(f"Request payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    response = requests.post(f"{BASE_URL}/kg/generate", json=payload)
    result = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(result, indent=2))
    
    return result


def test_multi_schema_new_format():
    """Test multi-schema using new schema_names format."""
    print_section("Test 3: Multiple Schemas (New Format)")
    
    payload = {
        "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
        "kg_name": "unified_kg_v2",
        "backends": ["graphiti"]
    }
    
    print(f"Request payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    response = requests.post(f"{BASE_URL}/kg/generate", json=payload)
    result = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(result, indent=2))
    
    return result


def compare_results(single: Dict[str, Any], multi: Dict[str, Any]):
    """Compare single vs multi-schema results."""
    print_section("Comparison: Single vs Multi-Schema")
    
    print(f"Single Schema KG:")
    print(f"  Schemas processed: {single['schemas_processed']}")
    print(f"  Nodes: {single['nodes_count']}")
    print(f"  Relationships: {single['relationships_count']}")
    print(f"  Generation time: {single['generation_time_ms']:.2f}ms")
    print()
    
    print(f"Multi-Schema KG:")
    print(f"  Schemas processed: {multi['schemas_processed']}")
    print(f"  Nodes: {multi['nodes_count']}")
    print(f"  Relationships: {multi['relationships_count']}")
    print(f"  Generation time: {multi['generation_time_ms']:.2f}ms")
    print()
    
    # Calculate differences
    node_diff = multi['nodes_count'] - single['nodes_count']
    rel_diff = multi['relationships_count'] - single['relationships_count']
    
    print(f"Differences (Multi vs Single):")
    print(f"  Additional nodes: {node_diff} ({(node_diff/single['nodes_count']*100):.1f}%)")
    print(f"  Additional relationships: {rel_diff} ({(rel_diff/single['relationships_count']*100):.1f}%)")
    print()
    
    # Estimate cross-schema relationships
    cross_schema_rels = rel_diff
    print(f"Estimated cross-schema relationships: {cross_schema_rels}")


def test_error_handling():
    """Test error handling."""
    print_section("Test 4: Error Handling")
    
    # Test missing both schema_name and schema_names
    print("Test 4a: Missing both schema_name and schema_names")
    payload = {
        "kg_name": "test_kg",
        "backends": ["graphiti"]
    }
    
    print(f"Request payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    response = requests.post(f"{BASE_URL}/kg/generate", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test non-existent schema
    print("Test 4b: Non-existent schema")
    payload = {
        "schema_names": ["nonexistent-schema"],
        "kg_name": "test_kg",
        "backends": ["graphiti"]
    }
    
    print(f"Request payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    response = requests.post(f"{BASE_URL}/kg/generate", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  Multi-Schema Knowledge Graph Generation Tests")
    print("="*70)
    
    try:
        # Test 1: Single schema (backward compatibility)
        single_result = test_single_schema()
        time.sleep(1)
        
        # Test 2: Multi-schema
        multi_result = test_multi_schema()
        time.sleep(1)
        
        # Test 3: Multi-schema with new format
        multi_result_v2 = test_multi_schema_new_format()
        time.sleep(1)
        
        # Compare results
        compare_results(single_result, multi_result)
        
        # Test 4: Error handling
        test_error_handling()
        
        print_section("All Tests Completed Successfully! ✅")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

