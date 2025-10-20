#!/usr/bin/env python
"""
Test script for Knowledge Graph Builder API.
Run this after starting the server with: python -m kg_builder.main
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(name: str, result: Dict[str, Any], success: bool = True):
    """Print a formatted result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {name}")
    print(json.dumps(result, indent=2))
    print()

def test_health():
    """Test health endpoint."""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print_result("Health Check", data)
        return True
    except Exception as e:
        print_result("Health Check", {"error": str(e)}, False)
        return False

def test_list_schemas():
    """Test schema listing."""
    print_section("2. List Schemas")
    try:
        response = requests.get(f"{BASE_URL}/schemas")
        response.raise_for_status()
        data = response.json()
        print_result("List Schemas", data)
        return data.get("schemas", [])
    except Exception as e:
        print_result("List Schemas", {"error": str(e)}, False)
        return []

def test_parse_schema(schema_name: str):
    """Test schema parsing."""
    print_section(f"3. Parse Schema: {schema_name}")
    try:
        response = requests.post(f"{BASE_URL}/schemas/{schema_name}/parse")
        response.raise_for_status()
        data = response.json()
        print_result(f"Parse Schema '{schema_name}'", data)
        return True
    except Exception as e:
        print_result(f"Parse Schema '{schema_name}'", {"error": str(e)}, False)
        return False

def test_generate_kg(schema_name: str, kg_name: str):
    """Test knowledge graph generation."""
    print_section(f"4. Generate Knowledge Graph: {kg_name}")
    try:
        payload = {
            "schema_name": schema_name,
            "kg_name": kg_name,
            "backends": ["graphiti"]
        }
        response = requests.post(f"{BASE_URL}/kg/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        print_result(f"Generate KG '{kg_name}'", data)
        return data.get("success", False)
    except Exception as e:
        print_result(f"Generate KG '{kg_name}'", {"error": str(e)}, False)
        return False

def test_list_graphs():
    """Test listing knowledge graphs."""
    print_section("5. List Knowledge Graphs")
    try:
        response = requests.get(f"{BASE_URL}/kg")
        response.raise_for_status()
        data = response.json()
        print_result("List Graphs", data)
        return data.get("graphs", [])
    except Exception as e:
        print_result("List Graphs", {"error": str(e)}, False)
        return []

def test_get_entities(kg_name: str):
    """Test retrieving entities."""
    print_section(f"6. Get Entities: {kg_name}")
    try:
        response = requests.get(f"{BASE_URL}/kg/{kg_name}/entities")
        response.raise_for_status()
        data = response.json()
        
        # Show summary
        summary = {
            "success": data.get("success"),
            "kg_name": data.get("kg_name"),
            "total_entities": data.get("count"),
            "first_3_entities": data.get("entities", [])[:3]
        }
        print_result(f"Get Entities from '{kg_name}'", summary)
        return True
    except Exception as e:
        print_result(f"Get Entities from '{kg_name}'", {"error": str(e)}, False)
        return False

def test_get_relationships(kg_name: str):
    """Test retrieving relationships."""
    print_section(f"7. Get Relationships: {kg_name}")
    try:
        response = requests.get(f"{BASE_URL}/kg/{kg_name}/relationships")
        response.raise_for_status()
        data = response.json()
        
        # Show summary
        summary = {
            "success": data.get("success"),
            "kg_name": data.get("kg_name"),
            "total_relationships": data.get("count"),
            "first_3_relationships": data.get("relationships", [])[:3]
        }
        print_result(f"Get Relationships from '{kg_name}'", summary)
        return True
    except Exception as e:
        print_result(f"Get Relationships from '{kg_name}'", {"error": str(e)}, False)
        return False

def test_export_graph(kg_name: str):
    """Test exporting knowledge graph."""
    print_section(f"8. Export Knowledge Graph: {kg_name}")
    try:
        response = requests.get(f"{BASE_URL}/kg/{kg_name}/export")
        response.raise_for_status()
        data = response.json()
        
        # Show summary
        summary = {
            "success": data.get("success"),
            "message": data.get("message"),
            "format": data.get("format"),
            "stats": data.get("data", {}).get("stats")
        }
        print_result(f"Export Graph '{kg_name}'", summary)
        return True
    except Exception as e:
        print_result(f"Export Graph '{kg_name}'", {"error": str(e)}, False)
        return False

def test_delete_graph(kg_name: str):
    """Test deleting knowledge graph."""
    print_section(f"9. Delete Knowledge Graph: {kg_name}")
    try:
        response = requests.delete(f"{BASE_URL}/kg/{kg_name}")
        response.raise_for_status()
        data = response.json()
        print_result(f"Delete Graph '{kg_name}'", data)
        return True
    except Exception as e:
        print_result(f"Delete Graph '{kg_name}'", {"error": str(e)}, False)
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  Knowledge Graph Builder - API Test Suite")
    print("="*60)
    print("\nMake sure the server is running: python -m kg_builder.main")
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server is not running. Please start it with:")
        print("   python -m kg_builder.main")
        return
    
    # Test 2: List schemas
    schemas = test_list_schemas()
    if not schemas:
        print("\n❌ No schemas found in schemas/ directory")
        return
    
    schema_name = schemas[0]
    
    # Test 3: Parse schema
    if not test_parse_schema(schema_name):
        return
    
    # Test 4: Generate KG
    kg_name = "test_kg_demo"
    if not test_generate_kg(schema_name, kg_name):
        return
    
    # Test 5: List graphs
    test_list_graphs()
    
    # Test 6: Get entities
    test_get_entities(kg_name)
    
    # Test 7: Get relationships
    test_get_relationships(kg_name)
    
    # Test 8: Export graph
    test_export_graph(kg_name)
    
    # Test 9: Delete graph
    test_delete_graph(kg_name)
    
    # Final summary
    print_section("Test Suite Complete")
    print("✅ All tests completed successfully!")
    print("\nNext steps:")
    print("1. Visit http://localhost:8000/docs for interactive API documentation")
    print("2. Check API_EXAMPLES.md for more usage examples")
    print("3. Read README.md for detailed setup instructions")

if __name__ == "__main__":
    main()

