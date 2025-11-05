"""
Column Hints Usage Examples
Demonstrates how to use the persistent hints dictionary system.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/kg"  # Adjust as needed


def example_1_get_all_hints():
    """Example: Get all hints dictionary."""
    print("=== Example 1: Get All Hints ===")
    response = requests.get(f"{BASE_URL}/hints/")
    print(json.dumps(response.json(), indent=2))
    print()


def example_2_get_table_hints():
    """Example: Get hints for a specific table."""
    print("=== Example 2: Get Table Hints ===")
    table_name = "hana_material_master"
    response = requests.get(f"{BASE_URL}/hints/table/{table_name}")
    print(json.dumps(response.json(), indent=2))
    print()


def example_3_get_column_hints():
    """Example: Get hints for a specific column."""
    print("=== Example 3: Get Column Hints ===")
    table_name = "hana_material_master"
    column_name = "MATERIAL"
    response = requests.get(f"{BASE_URL}/hints/column/{table_name}/{column_name}")
    print(json.dumps(response.json(), indent=2))
    print()


def example_4_update_column_hints():
    """Example: Update hints for a column."""
    print("=== Example 4: Update Column Hints ===")

    payload = {
        "table_name": "hana_material_master",
        "column_name": "MATERIAL",
        "user": "john@example.com",
        "hints": {
            "business_name": "Material Number",
            "aliases": ["product", "item", "sku", "material_code", "part_number"],
            "description": "Unique identifier for materials/products in the system",
            "semantic_type": "identifier",
            "data_type": "NVARCHAR(18)",
            "role": "primary_identifier",
            "common_terms": [
                "material",
                "product",
                "item",
                "what material",
                "which product"
            ],
            "examples": ["MAT001234", "PRD-567890"],
            "searchable": True,
            "filterable": True,
            "aggregatable": False,
            "priority": "high",
            "business_rules": ["Always 18 characters", "Format: MAT + 6 digits"],
            "user_notes": "Primary key for all material queries",
            "auto_generated": False,
            "manual_verified": True
        }
    }

    response = requests.post(f"{BASE_URL}/hints/column", json=payload)
    print(json.dumps(response.json(), indent=2))
    print()


def example_5_update_single_field():
    """Example: Update a single field in column hints."""
    print("=== Example 5: Update Single Field ===")

    table_name = "hana_material_master"
    column_name = "MATERIAL"
    field_name = "priority"

    payload = {
        "field_value": "high",
        "user": "sarah@example.com"
    }

    response = requests.patch(
        f"{BASE_URL}/hints/column/{table_name}/{column_name}/{field_name}",
        json=payload
    )
    print(json.dumps(response.json(), indent=2))
    print()


def example_6_add_table_hints():
    """Example: Add hints for a table."""
    print("=== Example 6: Add Table Hints ===")

    payload = {
        "table_name": "hana_material_master",
        "user": "admin@example.com",
        "hints": {
            "business_name": "Material Master Data",
            "aliases": ["materials", "products", "items", "parts"],
            "description": "Central repository for material/product information",
            "category": "master_data",
            "user_notes": "Main table for all material-related queries"
        }
    }

    response = requests.post(f"{BASE_URL}/hints/table", json=payload)
    print(json.dumps(response.json(), indent=2))
    print()


def example_7_search_hints():
    """Example: Search for columns by term."""
    print("=== Example 7: Search Hints ===")

    payload = {
        "search_term": "material",
        "limit": 5
    }

    response = requests.post(f"{BASE_URL}/hints/search", json=payload)
    print(json.dumps(response.json(), indent=2))
    print()


def example_8_generate_hints_llm():
    """Example: Generate hints using LLM."""
    print("=== Example 8: Generate Hints with LLM ===")

    payload = {
        "table_name": "hana_material_master",
        "column_name": "OPS_STATUS",
        "column_type": "NVARCHAR(50)",
        "sample_values": ["Active", "Inactive", "Discontinued"],
        "user": "system"
    }

    response = requests.post(f"{BASE_URL}/hints/generate", json=payload)
    print(json.dumps(response.json(), indent=2))
    print()


def example_9_bulk_generate_hints():
    """Example: Bulk generate hints for all columns in a table."""
    print("=== Example 9: Bulk Generate Hints ===")

    payload = {
        "table_name": "hana_material_master",
        "schema_path": "schemas/newdqschemanov.json",
        "user": "system",
        "overwrite_existing": False
    }

    response = requests.post(f"{BASE_URL}/hints/generate/bulk", json=payload)
    print(json.dumps(response.json(), indent=2))
    print()


def example_10_create_version():
    """Example: Create a version snapshot."""
    print("=== Example 10: Create Version Snapshot ===")

    payload = {
        "version_name": "v1.0_initial",
        "user": "admin@example.com",
        "comment": "Initial version with all auto-generated hints"
    }

    response = requests.post(f"{BASE_URL}/hints/version", json=payload)
    print(json.dumps(response.json(), indent=2))
    print()


def example_11_delete_column_hints():
    """Example: Delete hints for a column."""
    print("=== Example 11: Delete Column Hints ===")

    payload = {
        "table_name": "hana_material_master",
        "column_name": "MATERIAL",
        "user": "admin@example.com"
    }

    response = requests.delete(f"{BASE_URL}/hints/hints", json=payload)
    print(json.dumps(response.json(), indent=2))
    print()


def example_12_get_statistics():
    """Example: Get hints statistics."""
    print("=== Example 12: Get Statistics ===")

    response = requests.get(f"{BASE_URL}/hints/statistics")
    print(json.dumps(response.json(), indent=2))
    print()


def example_13_export_hints():
    """Example: Export hints to file."""
    print("=== Example 13: Export Hints ===")

    response = requests.get(
        f"{BASE_URL}/hints/export",
        params={"output_path": "schemas/hints/exported_hints.json"}
    )
    print(json.dumps(response.json(), indent=2))
    print()


def example_14_import_hints():
    """Example: Import hints from file."""
    print("=== Example 14: Import Hints ===")

    payload = {
        "input_path": "schemas/hints/exported_hints.json",
        "merge": True,
        "user": "admin@example.com"
    }

    response = requests.post(f"{BASE_URL}/hints/import", json=payload)
    print(json.dumps(response.json(), indent=2))
    print()


# ==================== Python Direct Usage ====================

def example_15_direct_python_usage():
    """Example: Direct Python usage without API."""
    print("=== Example 15: Direct Python Usage ===")

    from kg_builder.services.hint_manager import get_hint_manager

    # Get hint manager
    hint_manager = get_hint_manager()

    # Add column hints
    hint_manager.add_column_hints(
        table_name="hana_material_master",
        column_name="MATERIAL",
        column_hints={
            "business_name": "Material Number",
            "aliases": ["product", "item"],
            "description": "Unique identifier",
            "semantic_type": "identifier",
            "priority": "high"
        },
        user="script@example.com"
    )

    # Get column hints
    hints = hint_manager.get_column_hints("hana_material_master", "MATERIAL")
    print("Retrieved hints:", json.dumps(hints, indent=2))

    # Search hints
    results = hint_manager.search_hints("material")
    print(f"Found {len(results)} matching columns")

    # Create version
    hint_manager.create_version_snapshot(
        version_name="v1.0",
        user="script",
        comment="Created via script"
    )

    # Get statistics
    stats = hint_manager.get_statistics()
    print("Statistics:", json.dumps(stats, indent=2))
    print()


# ==================== Integration with NL-to-SQL ====================

def example_16_nl_to_sql_integration():
    """Example: Using hints for NL-to-SQL query generation."""
    print("=== Example 16: NL-to-SQL Integration ===")

    from kg_builder.services.hint_manager import get_hint_manager

    hint_manager = get_hint_manager()

    # User's natural language query
    user_query = "Show me all active materials"

    # Search for relevant columns
    active_matches = hint_manager.search_hints("active")
    material_matches = hint_manager.search_hints("materials")

    print("Matches for 'active':")
    for match in active_matches:
        print(f"  - {match['table_name']}.{match['column_name']}")

    print("\nMatches for 'materials':")
    for match in material_matches:
        print(f"  - {match['table_name']}.{match['column_name']}")

    # Build SQL using matched columns
    # In practice, this would use LLM with hints as context
    sql = """
    SELECT MATERIAL, OPS_STATUS
    FROM hana_material_master
    WHERE OPS_STATUS = 'Active'
    """

    print(f"\nGenerated SQL:\n{sql}")
    print()


if __name__ == "__main__":
    print("Column Hints Usage Examples\n")
    print("=" * 60)
    print()

    # Run examples
    try:
        # Basic operations
        example_2_get_table_hints()
        example_3_get_column_hints()
        example_4_update_column_hints()
        example_5_update_single_field()
        example_6_add_table_hints()

        # Search and statistics
        example_7_search_hints()
        example_12_get_statistics()

        # LLM generation
        example_8_generate_hints_llm()
        # example_9_bulk_generate_hints()  # Uncomment to run bulk generation

        # Version control
        example_10_create_version()

        # Export/Import
        example_13_export_hints()
        # example_14_import_hints()  # Uncomment to test import

        # Direct Python usage
        example_15_direct_python_usage()

        # NL-to-SQL integration
        example_16_nl_to_sql_integration()

    except Exception as e:
        print(f"Error: {e}")
