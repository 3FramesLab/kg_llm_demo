"""
Natural Language Rules Creation - Example Script

This script demonstrates how to use the Natural Language Rules Creation API
with various input formats.

Usage:
    python test_nl_rules_examples.py
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000/v1"


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_natural_language_format():
    """Example 1: Natural Language Format"""
    print_header("Example 1: Natural Language Format")

    payload = {
        "kg_name": "ecommerce_kg",
        "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
        "definitions": [
            "Products are supplied by Vendors",
            "Orders contain Products",
            "Customers place Orders"
        ],
        "use_llm": True,
        "min_confidence": 0.7
    }

    print("📝 Request:")
    pprint(payload)
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/kg/relationships/natural-language",
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"   Parsed Relationships: {result['parsed_count']}")
            print(f"   Failed: {result['failed_count']}")
            print(f"   Processing Time: {result['processing_time_ms']:.2f}ms")

            if result['relationships']:
                print("\n🔗 Relationships:")
                for rel in result['relationships']:
                    print(f"   - {rel['source_entity']}.{rel['source_column']} "
                          f"→ {rel['target_entity']}.{rel['target_column']} "
                          f"({rel['relationship_type']}) [Confidence: {rel['confidence']:.2%}]")

            if result['errors']:
                print("\n⚠️  Errors:")
                for error in result['errors']:
                    print(f"   - {error}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Exception: {e}")


def test_semi_structured_format():
    """Example 2: Semi-Structured (Arrow) Format"""
    print_header("Example 2: Semi-Structured Format (Arrow Notation)")

    payload = {
        "kg_name": "supply_chain_kg",
        "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
        "definitions": [
            "catalog.product_id → vendor.vendor_product_id (SUPPLIED_BY)",
            "orders.customer_id → customers.customer_id (PLACED_BY)",
            "order_items.product_id → products.product_id (CONTAINS)"
        ],
        "use_llm": False,  # No LLM needed for explicit mappings
        "min_confidence": 0.9
    }

    print("📝 Request:")
    pprint(payload)
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/kg/relationships/natural-language",
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"   Parsed Relationships: {result['parsed_count']}")
            print(f"   Processing Time: {result['processing_time_ms']:.2f}ms")

            if result['relationships']:
                print("\n🔗 Relationships:")
                for rel in result['relationships']:
                    print(f"   - {rel['source_entity']}.{rel['source_column']} "
                          f"→ {rel['target_entity']}.{rel['target_column']} "
                          f"({rel['relationship_type']}) [Confidence: {rel['confidence']:.2%}]")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Exception: {e}")


def test_pseudo_sql_format():
    """Example 3: Pseudo-SQL Format"""
    print_header("Example 3: Pseudo-SQL Format")

    payload = {
        "kg_name": "inventory_kg",
        "schemas": ["products-schema", "stock-schema"],
        "definitions": [
            "SELECT * FROM products JOIN suppliers ON products.supplier_id = suppliers.supplier_id",
            "SELECT * FROM orders JOIN customers ON orders.customer_id = customers.customer_id"
        ],
        "use_llm": False,
        "min_confidence": 0.8
    }

    print("📝 Request:")
    pprint(payload)
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/kg/relationships/natural-language",
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"   Parsed Relationships: {result['parsed_count']}")
            print(f"   Processing Time: {result['processing_time_ms']:.2f}ms")

            if result['relationships']:
                print("\n🔗 Relationships:")
                for rel in result['relationships']:
                    print(f"   - {rel['source_entity']}.{rel['source_column']} "
                          f"→ {rel['target_entity']}.{rel['target_column']} "
                          f"({rel['relationship_type']}) [Confidence: {rel['confidence']:.2%}]")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Exception: {e}")


def test_business_rules_format():
    """Example 4: Business Rules Format"""
    print_header("Example 4: Business Rules Format")

    payload = {
        "kg_name": "conditional_kg",
        "schemas": ["sales-schema", "products-schema"],
        "definitions": [
            "IF product.status = 'active' THEN match with inventory.product_id",
            "IF order.order_type = 'online' THEN link to digital_receipts.order_id"
        ],
        "use_llm": True,
        "min_confidence": 0.7
    }

    print("📝 Request:")
    pprint(payload)
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/kg/relationships/natural-language",
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"   Parsed Relationships: {result['parsed_count']}")
            print(f"   Processing Time: {result['processing_time_ms']:.2f}ms")

            if result['relationships']:
                print("\n🔗 Relationships:")
                for rel in result['relationships']:
                    print(f"   - {rel['source_entity']}.{rel['source_column']} "
                          f"→ {rel['target_entity']}.{rel['target_column']} "
                          f"({rel['relationship_type']}) [Confidence: {rel['confidence']:.2%}]")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Exception: {e}")


def test_mixed_formats():
    """Example 5: Mixed Formats"""
    print_header("Example 5: Mixed Formats (All Types Combined)")

    payload = {
        "kg_name": "comprehensive_kg",
        "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
        "definitions": [
            # Natural Language
            "Products are supplied by Vendors",

            # Semi-Structured
            "catalog.product_id → vendor.vendor_product_id (SUPPLIED_BY)",

            # Pseudo-SQL
            "SELECT * FROM orders JOIN customers ON orders.customer_id = customers.customer_id",

            # Business Rules
            "IF product.Active_Inactive = 'Active' THEN match with vendor.product_status = 'Available'"
        ],
        "use_llm": True,
        "min_confidence": 0.75
    }

    print("📝 Request (mixing all 4 formats):")
    pprint(payload)
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/kg/relationships/natural-language",
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"   Parsed Relationships: {result['parsed_count']}")
            print(f"   Failed: {result['failed_count']}")
            print(f"   Processing Time: {result['processing_time_ms']:.2f}ms")

            if result['relationships']:
                print("\n🔗 Relationships by Format:")
                for rel in result['relationships']:
                    print(f"\n   Format: {rel['input_format']}")
                    print(f"   {rel['source_entity']}.{rel['source_column']} "
                          f"→ {rel['target_entity']}.{rel['target_column']}")
                    print(f"   Type: {rel['relationship_type']}")
                    print(f"   Confidence: {rel['confidence']:.2%}")
                    print(f"   Validation: {rel['validation_status']}")

            if result['errors']:
                print("\n⚠️  Errors:")
                for error in result['errors']:
                    print(f"   - {error}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Exception: {e}")


def main():
    """Run all examples."""
    print_header("Natural Language Rules Creation - Examples")
    print("This script demonstrates all 4 input formats for creating reconciliation rules.")
    print()
    print("Prerequisites:")
    print("  1. Backend API server running on http://localhost:8000")
    print("  2. Schema files available in data/schemas/")
    print("  3. (Optional) OpenAI API key set for LLM-enhanced parsing")
    print()
    input("Press Enter to start the examples...")

    # Check server health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!\n")
        else:
            print("⚠️  Server responded but might have issues\n")
    except:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("   Please start the server with: python -m uvicorn kg_builder.main:app --reload")
        return

    # Run examples
    try:
        test_natural_language_format()
        input("\nPress Enter for next example...")

        test_semi_structured_format()
        input("\nPress Enter for next example...")

        test_pseudo_sql_format()
        input("\nPress Enter for next example...")

        test_business_rules_format()
        input("\nPress Enter for next example...")

        test_mixed_formats()

        print_header("Examples Complete!")
        print("✅ All examples have been executed.")
        print()
        print("Next steps:")
        print("  1. Check the generated relationships")
        print("  2. Generate reconciliation rules: POST /v1/reconciliation/generate")
        print("  3. Export to SQL: GET /v1/reconciliation/rulesets/{id}/export/sql")
        print("  4. Execute reconciliation: POST /v1/reconciliation/execute")

    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
