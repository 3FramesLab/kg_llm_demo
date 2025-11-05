#!/usr/bin/env python3
"""
Test script to verify main table selection fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kg_builder.services.nl_query_parser import get_nl_query_parser
from kg_builder.services.nl_sql_generator import NLSQLGenerator
from kg_builder.services.schema_parser import SchemaParser

def test_main_table_selection():
    """Test that hana_material_master is not selected as main table."""
    
    print("="*60)
    print("TESTING MAIN TABLE SELECTION FIX")
    print("="*60)
    
    # Build KG
    try:
        kg = SchemaParser.build_merged_knowledge_graph(
            schema_names=["newdqschemanov"],
            kg_name="test_main_table_kg",
            use_llm=False  # Use rule-based for consistent testing
        )
        print(f"✅ Built KG with {len(kg.relationships)} relationships")
    except Exception as e:
        print(f"❌ Failed to build KG: {e}")
        return
    
    # Extract schemas info
    schemas_info = {}
    for node in kg.nodes:
        if node.properties.get("type") == "Table":
            table_name = node.label
            columns = [col.get("name") if isinstance(col, dict) else col.name 
                      for col in node.properties.get("columns", [])]
            schemas_info[table_name] = {"columns": columns}
    
    # Initialize parser and generator
    parser = get_nl_query_parser(kg=kg, schemas_info=schemas_info)
    generator = NLSQLGenerator(db_type="sqlserver", use_llm=True, kg=kg, schemas_info=schemas_info)
    
    # Test queries that might incorrectly use hana_material_master as main table
    test_queries = [
        "Show NBU products where OPS_PLANNER is null",
        "Find materials with Product Type NBU and no planner assigned",
        "List all NBU items without OPS_PLANNER",
        "Show products from IBP where Product Type is NBU and OPS_PLANNER is null"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {query} ---")
        
        try:
            # Parse the query
            intent = parser.parse(query)
            print(f"Source Table: {intent.source_table}")
            print(f"Target Table: {intent.target_table}")
            
            # Generate SQL
            sql = generator.generate(intent)
            print(f"Generated SQL:")
            print(sql)
            
            # Check if hana_material_master is used as main table (should NOT be)
            if sql and "FROM [hana_material_master]" in sql:
                print("❌ FAIL: hana_material_master used as main table!")
            elif sql and "FROM [brz_lnd_IBP_Product_Master]" in sql:
                print("✅ PASS: brz_lnd_IBP_Product_Master used as main table")
            elif sql and any(f"FROM [{table}]" in sql for table in ["brz_lnd_RBP_GPU", "brz_lnd_OPS_EXCEL_GPU"]):
                print("✅ PASS: Main table (brz_lnd_*) used correctly")
            else:
                print("⚠️  UNKNOWN: Could not determine main table from SQL")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_main_table_selection()
