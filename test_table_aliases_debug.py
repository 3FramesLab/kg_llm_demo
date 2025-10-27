"""
Debug script to test table_aliases extraction for single schema
"""
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from kg_builder.services.schema_parser import SchemaParser

def test_single_schema_aliases():
    """Test table alias extraction for single schema"""
    print("\n" + "="*80)
    print("TEST: Single Schema Table Alias Extraction")
    print("="*80)

    schema_name = "newdqschema"
    kg_name = "test_kg"

    try:
        # Load schema
        print(f"\n1. Loading schema: {schema_name}")
        schema = SchemaParser.load_schema(schema_name)
        print(f"   ✓ Loaded schema with {len(schema.tables)} tables")
        print(f"   Tables: {list(schema.tables.keys())}")

        # Build knowledge graph with LLM enabled
        print(f"\n2. Building knowledge graph with LLM enabled")
        kg = SchemaParser.build_knowledge_graph(
            schema_name=schema_name,
            kg_name=kg_name,
            schema=schema,
            use_llm=True,
            field_preferences=None
        )

        print(f"\n3. Knowledge Graph built:")
        print(f"   - Name: {kg.name}")
        print(f"   - Nodes: {len(kg.nodes)}")
        print(f"   - Relationships: {len(kg.relationships)}")
        print(f"   - Table Aliases: {len(kg.table_aliases)}")
        print(f"   - Aliases: {kg.table_aliases}")

        if kg.table_aliases:
            print(f"\n✅ SUCCESS: Extracted aliases for {len(kg.table_aliases)} tables")
            for table, aliases in kg.table_aliases.items():
                print(f"   {table}: {aliases}")
            return True
        else:
            print(f"\n❌ FAILURE: No table aliases extracted")
            return False

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_single_schema_aliases()
    sys.exit(0 if result else 1)

