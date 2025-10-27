"""
Test script to verify table alias extraction is working
"""
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables FIRST (before importing anything from kg_builder)
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from kg_builder.services.llm_service import get_llm_service
from kg_builder.services.schema_parser import SchemaParser

def test_llm_service():
    """Test if LLM service is properly initialized"""
    print("\n" + "="*60)
    print("TEST 1: LLM Service Initialization")
    print("="*60)

    llm_service = get_llm_service()
    print(f"LLM Service enabled: {llm_service.is_enabled()}")
    print(f"OpenAI API Key present: {bool(llm_service.client)}")
    print(f"Model: {llm_service.model}")

    if not llm_service.is_enabled():
        print("[FAIL] LLM Service is not enabled!")
        return False

    print("[PASS] LLM Service is enabled")
    return True

def test_table_alias_extraction():
    """Test table alias extraction"""
    print("\n" + "="*60)
    print("TEST 2: Table Alias Extraction")
    print("="*60)

    llm_service = get_llm_service()

    # Test with a sample table
    test_table_name = "brz_lnd_RBP_GPU"
    test_columns = ["Material", "Product_Description", "Quantity", "Price"]
    test_description = "Table from newdqschema schema"

    print(f"\nExtracting aliases for table: {test_table_name}")
    print(f"Columns: {test_columns}")
    print(f"Description: {test_description}")

    try:
        result = llm_service.extract_table_aliases(
            table_name=test_table_name,
            table_description=test_description,
            columns=test_columns
        )

        print(f"\n📋 Result: {result}")

        if result.get("aliases"):
            print(f"[PASS] Successfully extracted aliases: {result['aliases']}")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
            return True
        else:
            print(f"[FAIL] No aliases extracted")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"[FAIL] Exception during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_loading():
    """Test schema loading and alias extraction"""
    print("\n" + "="*60)
    print("TEST 3: Full Schema Alias Extraction")
    print("="*60)

    schema_name = "newdqschema"

    try:
        schema = SchemaParser.load_schema(schema_name)
        print(f"[PASS] Loaded schema: {schema_name}")
        print(f"   Tables: {list(schema.tables.keys())}")

        # Test _extract_table_aliases
        schemas_dict = {schema_name: schema}
        table_aliases = SchemaParser._extract_table_aliases(schemas_dict)

        print(f"\n📋 Table aliases extracted: {table_aliases}")

        if table_aliases:
            print(f"[PASS] Successfully extracted aliases for {len(table_aliases)} tables")
            for table, aliases in table_aliases.items():
                print(f"   {table}: {aliases}")
            return True
        else:
            print(f"[FAIL] No table aliases extracted")
            return False

    except Exception as e:
        print(f"[FAIL] Exception during schema loading: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TABLE ALIAS EXTRACTION TEST")
    print("="*60)

    results = []

    # Run tests
    results.append(("LLM Service", test_llm_service()))
    results.append(("Direct Extraction", test_table_alias_extraction()))
    results.append(("Schema Extraction", test_schema_loading()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "[PASS] PASSED" if passed else "[FAIL] FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)
    print("\n" + ("="*60))
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("[FAIL] SOME TESTS FAILED")
    print("="*60)
