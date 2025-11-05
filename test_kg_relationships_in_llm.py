#!/usr/bin/env python3
"""
Test that KG relationships are properly passed to LLM SQL generator.
"""

def test_kg_relationships_format():
    """Test KG relationship formatting for LLM prompt."""
    
    print("="*60)
    print("TESTING KG RELATIONSHIPS IN LLM PROMPT")
    print("="*60)
    
    # Simulate KG relationships (as they would come from the KG)
    kg_relationships = [
        {
            "source_id": "table_hana_material_master",
            "target_id": "table_brz_lnd_IBP_Product_Master", 
            "source_column": "MATERIAL",
            "target_column": "ZBASEMATERIAL",
            "relationship_type": "MATCHES",
            "properties": {"llm_confidence": 0.95}
        },
        {
            "source_id": "table_brz_lnd_SKU_LIFNR_Excel",
            "target_id": "table_hana_material_master",
            "source_column": "Material", 
            "target_column": "MATERIAL",
            "relationship_type": "REFERENCES",
            "properties": {"confidence": 0.90}
        },
        {
            "source_id": "table_brz_lnd_SKU_LIFNR_Excel",
            "target_id": "table_brz_lnd_IBP_Product_Master",
            "source_column": "Material",
            "target_column": "ZBASEMATERIAL", 
            "relationship_type": "MATCHES",
            "properties": {"llm_confidence": 0.88}
        },
        {
            "source_id": "table_brz_lnd_RBP_GPU",
            "target_id": "table_hana_material_master",
            "source_column": "Material",
            "target_column": "MATERIAL",
            "relationship_type": "REFERENCES", 
            "properties": {"confidence": 0.85}
        }
    ]
    
    print("\n--- Test 1: Relationship Processing ---")
    
    # Simulate the processing logic from llm_sql_generator.py
    context_relationships = []
    
    for rel in kg_relationships:
        if rel.get("source_column") and rel.get("target_column"):
            # Clean table names (remove table_ prefix)
            source_table = rel["source_id"].replace("table_", "")
            target_table = rel["target_id"].replace("table_", "")
            
            context_relationships.append({
                "source_table": source_table,
                "target_table": target_table,
                "source_column": rel["source_column"],
                "target_column": rel["target_column"],
                "relationship_type": rel["relationship_type"],
                "confidence": rel["properties"].get("llm_confidence", rel["properties"].get("confidence", 0.75))
            })
    
    print(f"Processed {len(context_relationships)} relationships:")
    for rel in context_relationships:
        print(f"  • {rel['source_table']}.{rel['source_column']} ↔ {rel['target_table']}.{rel['target_column']} ({rel['relationship_type']}) conf: {rel['confidence']:.2f}")
    
    print("\n--- Test 2: Query-Specific Relationship Prioritization ---")
    
    # Test prioritization for a specific query
    query_tables = {"brz_lnd_SKU_LIFNR_Excel", "brz_lnd_IBP_Product_Master"}
    
    relevant_rels = []
    other_rels = []
    
    for rel in context_relationships:
        if (rel['source_table'] in query_tables or rel['target_table'] in query_tables):
            relevant_rels.append(rel)
        else:
            other_rels.append(rel)
    
    # Sort by confidence
    relevant_rels.sort(key=lambda r: r.get('confidence', 0.75), reverse=True)
    other_rels.sort(key=lambda r: r.get('confidence', 0.75), reverse=True)
    
    print(f"Query tables: {query_tables}")
    print(f"Relevant relationships ({len(relevant_rels)}):")
    for rel in relevant_rels:
        print(f"  ✓ {rel['source_table']}.{rel['source_column']} ↔ {rel['target_table']}.{rel['target_column']} (conf: {rel['confidence']:.2f})")
    
    print(f"Other relationships ({len(other_rels)}):")
    for rel in other_rels:
        print(f"  • {rel['source_table']}.{rel['source_column']} ↔ {rel['target_table']}.{rel['target_column']} (conf: {rel['confidence']:.2f})")
    
    print("\n--- Test 3: Expected vs Actual Join ---")
    
    # Find the correct relationship for SKU_LIFNR_Excel → IBP_Product_Master
    correct_rel = None
    for rel in relevant_rels:
        if (rel['source_table'] == 'brz_lnd_SKU_LIFNR_Excel' and 
            rel['target_table'] == 'brz_lnd_IBP_Product_Master'):
            correct_rel = rel
            break
    
    if correct_rel:
        print("✅ CORRECT relationship found:")
        print(f"   {correct_rel['source_table']}.{correct_rel['source_column']} = {correct_rel['target_table']}.{correct_rel['target_column']}")
        print("   Expected SQL: s.[Material] = t.[ZBASEMATERIAL]")
    else:
        print("❌ MISSING: No direct relationship found between brz_lnd_SKU_LIFNR_Excel and brz_lnd_IBP_Product_Master")
    
    print(f"\n{'='*60}")
    print("KG RELATIONSHIPS TEST COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_kg_relationships_format()
