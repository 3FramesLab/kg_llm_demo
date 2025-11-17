#!/usr/bin/env python3
"""
Test script to verify the SQL preview endpoint fix.
This script tests the NLQueryExecutor initialization fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_nl_query_executor_initialization():
    """Test the NLQueryExecutor initialization with correct parameters."""
    
    print("🧪 Testing NLQueryExecutor Initialization Fix")
    print("="*60)
    
    try:
        from kg_builder.services.nl_query_executor import NLQueryExecutor
        from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship
        
        # Test 1: Basic initialization (should work)
        print("📋 Test 1: Basic NLQueryExecutor initialization")
        executor1 = NLQueryExecutor(db_type="sqlserver", use_llm=True)
        print(f"✅ SUCCESS: Basic initialization")
        print(f"   DB Type: {executor1.db_type}")
        print(f"   Use LLM: {executor1.use_llm}")
        print(f"   KG: {executor1.kg}")
        
        # Test 2: Initialization with Knowledge Graph
        print(f"\n📋 Test 2: NLQueryExecutor with Knowledge Graph")
        
        # Create a mock KG
        nodes = [
            GraphNode(
                id="table1",
                label="hana_material_master",
                properties={
                    "type": "Table",
                    "schema": "newdqnov7",
                    "columns": [
                        {"name": "MATERIAL", "type": "VARCHAR"},
                        {"name": "OPS_PLANNER", "type": "VARCHAR"}
                    ]
                }
            )
        ]
        
        relationships = [
            GraphRelationship(
                id="rel1",
                source_id="table1",
                target_id="table2",
                relationship_type="JOINS_WITH",
                properties={"join_columns": ["MATERIAL"]}
            )
        ]
        
        kg = KnowledgeGraph(
            name="Test_KG",
            nodes=nodes,
            relationships=relationships,
            schema_file="newdqnov7",
            table_aliases={"hana_material_master": ["Material Master"]}
        )
        
        executor2 = NLQueryExecutor(db_type="sqlserver", kg=kg, use_llm=True)
        print(f"✅ SUCCESS: Initialization with KG")
        print(f"   DB Type: {executor2.db_type}")
        print(f"   Use LLM: {executor2.use_llm}")
        print(f"   KG Name: {executor2.kg.name if executor2.kg else 'None'}")
        print(f"   KG Nodes: {len(executor2.kg.nodes) if executor2.kg else 0}")
        
        # Test 3: Test the old incorrect way (should fail)
        print(f"\n📋 Test 3: Testing old incorrect initialization (should fail)")
        try:
            # This should fail - the old way that was causing the error
            executor3 = NLQueryExecutor(
                kg_name="Test_KG",
                select_schema="newdqnov7",
                use_llm=True
            )
            print(f"❌ FAIL: Old initialization should have failed but didn't")
            return False
        except TypeError as e:
            print(f"✅ SUCCESS: Old initialization correctly failed")
            print(f"   Error: {e}")
        
        # Test 4: Test SQL preview request simulation
        print(f"\n📋 Test 4: Simulating SQL preview request")
        
        class MockRequest:
            def __init__(self):
                self.kg_name = "New_KG_101"
                self.select_schema = "newdqnov7"
                self.use_llm = True
                self.nl_definition = "get products from nbu product master and hana master where planner is missing in both"
        
        request = MockRequest()
        
        # This is the NEW correct way (after our fix)
        executor4 = NLQueryExecutor(
            db_type="sqlserver",
            kg=kg,  # Pass the KG object, not kg_name
            use_llm=request.use_llm
        )
        
        print(f"✅ SUCCESS: SQL preview simulation")
        print(f"   Request KG Name: {request.kg_name}")
        print(f"   Request Schema: {request.select_schema}")
        print(f"   Request Use LLM: {request.use_llm}")
        print(f"   Executor DB Type: {executor4.db_type}")
        print(f"   Executor KG: {executor4.kg.name if executor4.kg else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Unexpected error during testing")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {e}")
        return False

def test_sql_preview_endpoint_logic():
    """Test the SQL preview endpoint logic."""
    
    print(f"\n🧪 Testing SQL Preview Endpoint Logic")
    print("="*60)
    
    try:
        # Simulate the fixed SQL preview logic
        class MockRequest:
            def __init__(self):
                self.kg_name = "New_KG_101"
                self.select_schema = "newdqnov7"
                self.use_llm = True
                self.nl_definition = "get products where planner is missing"
        
        request = MockRequest()
        
        print(f"📋 Simulating SQL Preview Request:")
        print(f"   KG Name: {request.kg_name}")
        print(f"   Schema: {request.select_schema}")
        print(f"   Use LLM: {request.use_llm}")
        print(f"   NL Definition: {request.nl_definition}")
        
        # Step 1: Load KG (simulated)
        kg = None  # In real scenario, this would load from Graphiti
        print(f"   KG Loaded: {kg is not None}")
        
        # Step 2: Initialize executor (the fixed way)
        from kg_builder.services.nl_query_executor import NLQueryExecutor
        executor = NLQueryExecutor(
            db_type="sqlserver",
            kg=kg,
            use_llm=request.use_llm
        )
        
        print(f"✅ SUCCESS: SQL Preview endpoint logic simulation")
        print(f"   Executor initialized successfully")
        print(f"   DB Type: {executor.db_type}")
        print(f"   Use LLM: {executor.use_llm}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: SQL Preview endpoint logic failed")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 NLQueryExecutor Initialization Fix Test")
    print("="*70)
    
    test1_success = test_nl_query_executor_initialization()
    test2_success = test_sql_preview_endpoint_logic()
    
    print("\n" + "="*70)
    if test1_success and test2_success:
        print("🎉 CONCLUSION: NLQueryExecutor initialization fix is working!")
        print("   ✅ Basic initialization works")
        print("   ✅ KG initialization works")
        print("   ✅ Old incorrect way properly fails")
        print("   ✅ SQL preview endpoint logic works")
        print("\n   The SQL preview error should now be resolved!")
    else:
        print("❌ CONCLUSION: Some tests failed - fix needs more work.")
    print("="*70)
