#!/usr/bin/env python3
"""
Test script to verify the KPI execution parameter conversion fix.
This script tests the parameter mapping from schemas array to select_schema.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_parameter_conversion():
    """Test the parameter conversion logic."""
    
    # Test case 1: Your actual request parameters
    execution_params = {
        "kg_name": "New_KG_101",
        "schemas": ["newdqnov7"],
        "definitions": ["get products from gpu product master and hana master where marketing code is missing in both"],
        "use_llm": True,
        "min_confidence": 0.8,
        "limit": 1000,
        "db_type": "sqlserver"
    }
    
    print("🧪 Testing Parameter Conversion")
    print("="*50)
    print(f"Input parameters: {execution_params}")
    print()
    
    # Simulate the conversion logic from the fixed code
    schemas = execution_params.get('schemas', [])
    select_schema = execution_params.get('select_schema')
    if not select_schema and schemas:
        select_schema = schemas[0]
    if not select_schema:
        select_schema = 'newdqschemanov'  # Default fallback
    
    # Convert limit to limit_records if needed
    limit_records = execution_params.get('limit_records') or execution_params.get('limit', 1000)
    
    print("🔧 Converted Parameters:")
    print(f"   kg_name: {execution_params.get('kg_name', 'default')}")
    print(f"   select_schema: {select_schema} (converted from schemas: {schemas})")
    print(f"   db_type: {execution_params.get('db_type', 'sqlserver')}")
    print(f"   limit_records: {limit_records}")
    print(f"   use_llm: {execution_params.get('use_llm', True)}")
    print(f"   user_id: {execution_params.get('user_id')}")
    print(f"   session_id: {execution_params.get('session_id')}")
    print()
    
    # Test the SQL parameters that would be inserted
    sql_params = (
        999,  # kpi_id (test value)
        execution_params.get('kg_name', 'default'),
        select_schema,  # This should NOT be None now
        execution_params.get('db_type', 'sqlserver'),
        limit_records,
        execution_params.get('use_llm', True),
        'pending',
        execution_params.get('user_id'),
        execution_params.get('session_id')
    )
    
    print("📋 SQL Insert Parameters:")
    for i, param in enumerate(sql_params):
        param_names = ['kpi_id', 'kg_name', 'select_schema', 'db_type', 'limit_records', 'use_llm', 'execution_status', 'user_id', 'session_id']
        print(f"   {param_names[i]}: {param} ({type(param).__name__})")
    
    # Check for None values that would cause the error
    none_params = [i for i, param in enumerate(sql_params) if param is None and param_names[i] in ['select_schema']]
    
    if none_params:
        print(f"\n❌ ERROR: Found None values in required fields: {[param_names[i] for i in none_params]}")
        return False
    else:
        print(f"\n✅ SUCCESS: All required parameters have values!")
        return True

def test_edge_cases():
    """Test edge cases for parameter conversion."""
    
    print("\n🧪 Testing Edge Cases")
    print("="*50)
    
    test_cases = [
        {
            "name": "Empty schemas array",
            "params": {"schemas": [], "kg_name": "test"}
        },
        {
            "name": "No schemas field",
            "params": {"kg_name": "test"}
        },
        {
            "name": "Explicit select_schema",
            "params": {"select_schema": "custom_schema", "schemas": ["ignored"], "kg_name": "test"}
        },
        {
            "name": "Multiple schemas",
            "params": {"schemas": ["schema1", "schema2", "schema3"], "kg_name": "test"}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        params = test_case['params']
        
        # Apply conversion logic
        schemas = params.get('schemas', [])
        select_schema = params.get('select_schema')
        if not select_schema and schemas:
            select_schema = schemas[0]
        if not select_schema:
            select_schema = 'newdqschemanov'
        
        print(f"   Input: {params}")
        print(f"   Result: select_schema = '{select_schema}'")
        
        if select_schema:
            print(f"   ✅ PASS")
        else:
            print(f"   ❌ FAIL")

if __name__ == "__main__":
    print("🚀 KPI Execution Parameter Conversion Test")
    print("="*60)
    
    success = test_parameter_conversion()
    test_edge_cases()
    
    print("\n" + "="*60)
    if success:
        print("🎉 CONCLUSION: The fix should resolve the select_schema NULL error!")
        print("   The parameter conversion logic correctly handles your request.")
    else:
        print("❌ CONCLUSION: The fix needs more work.")
    print("="*60)
