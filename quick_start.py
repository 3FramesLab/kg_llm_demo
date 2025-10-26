"""
Quick Start Script - Reconciliation Rule Generation

This script provides an interactive way to generate reconciliation rules.
Simply run: python quick_start.py
"""

import requests
import sys
from pprint import pprint

BASE_URL = "http://localhost:8000"


def check_server():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/v1/health", timeout=2)
        if response.status_code == 200:
            return True
    except:
        return False
    return False


def get_schemas():
    """Get list of available schemas."""
    try:
        response = requests.get(f"{BASE_URL}/v1/schemas")
        if response.status_code == 200:
            return response.json().get('schemas', [])
    except:
        return []
    return []


def main():
    print("=" * 70)
    print("  RECONCILIATION RULE GENERATION - QUICK START")
    print("=" * 70)
    print()

    # Check if server is running
    print("Checking if API server is running...")
    if not check_server():
        print()
        print("❌ ERROR: API server is not running!")
        print()
        print("To start the server, run:")
        print("  python -m uvicorn kg_builder.main:app --reload")
        print()
        sys.exit(1)

    print("✅ Server is running\n")

    # Get available schemas
    print("Loading available schemas...")
    schemas = get_schemas()

    if not schemas:
        print()
        print("❌ ERROR: No schemas found!")
        print()
        print("Please add JSON schema files to the schemas/ directory")
        sys.exit(1)

    print(f"✅ Found {len(schemas)} schemas:\n")
    for i, schema in enumerate(schemas, 1):
        print(f"  {i}. {schema}")
    print()

    # Select schemas for reconciliation
    if len(schemas) < 2:
        print("⚠️  WARNING: Need at least 2 schemas for reconciliation")
        print("   Using the available schema for demonstration\n")
        selected = schemas
    else:
        print("Select schemas to reconcile:")
        print("  (Press Enter to use first 2 schemas)")
        print()

        user_input = input("Enter schema numbers (e.g., '1,2') or press Enter: ").strip()

        if not user_input:
            selected = schemas[:2]
        else:
            try:
                indices = [int(x.strip()) - 1 for x in user_input.split(',')]
                selected = [schemas[i] for i in indices if 0 <= i < len(schemas)]
                if len(selected) < 2:
                    print("⚠️  Using first 2 schemas instead")
                    selected = schemas[:2]
            except:
                print("⚠️  Invalid input, using first 2 schemas")
                selected = schemas[:2]

    print()
    print(f"Selected schemas: {', '.join(selected)}")
    print()

    # Ask for KG name
    kg_name = input("Enter knowledge graph name (or press Enter for 'quick_start_kg'): ").strip()
    if not kg_name:
        kg_name = "quick_start_kg"

    print()
    print("=" * 70)
    print("  STEP 1: Generating Knowledge Graph")
    print("=" * 70)
    print()

    # Generate KG
    kg_request = {
        "schema_names": selected,
        "kg_name": kg_name,
        "backends": ["falkordb"],
        "use_llm_enhancement": True
    }

    print("Request:")
    pprint(kg_request)
    print()

    try:
        response = requests.post(f"{BASE_URL}/v1/kg/generate", json=kg_request)
        response.raise_for_status()
        kg_result = response.json()

        print("✅ Knowledge Graph Created Successfully!")
        print(f"   Name: {kg_result['kg_name']}")
        print(f"   Nodes: {kg_result['nodes_count']}")
        print(f"   Relationships: {kg_result['relationships_count']}")
        print(f"   Time: {kg_result['generation_time_ms']:.2f}ms")
    except Exception as e:
        print(f"❌ Error creating knowledge graph: {e}")
        sys.exit(1)

    print()
    print("=" * 70)
    print("  STEP 2: Generating Reconciliation Rules")
    print("=" * 70)
    print()

    # Generate rules
    rules_request = {
        "schema_names": selected,
        "kg_name": kg_name,
        "use_llm_enhancement": True,
        "min_confidence": 0.7,
        "match_types": ["exact", "semantic"]
    }

    print("Request:")
    pprint(rules_request)
    print()

    try:
        response = requests.post(f"{BASE_URL}/v1/reconciliation/generate", json=rules_request)
        response.raise_for_status()
        rules_result = response.json()

        print("✅ Reconciliation Rules Generated Successfully!")
        print(f"   Ruleset ID: {rules_result['ruleset_id']}")
        print(f"   Rules Count: {rules_result['rules_count']}")
        print(f"   Time: {rules_result['generation_time_ms']:.2f}ms")
    except Exception as e:
        print(f"❌ Error generating rules: {e}")
        sys.exit(1)

    # Display rules
    print()
    print("=" * 70)
    print("  GENERATED RULES")
    print("=" * 70)
    print()

    if rules_result['rules_count'] == 0:
        print("No rules generated. This might happen if:")
        print("  - No cross-schema relationships were detected")
        print("  - All rules had confidence < 0.7")
        print()
    else:
        for i, rule in enumerate(rules_result['rules'], 1):
            print(f"Rule {i}: {rule['rule_name']}")
            print(f"  Match Type: {rule['match_type']}")
            print(f"  Confidence: {rule['confidence_score']:.2f}")
            print(f"  Source: {rule['source_schema']}.{rule['source_table']} ({', '.join(rule['source_columns'])})")
            print(f"  Target: {rule['target_schema']}.{rule['target_table']} ({', '.join(rule['target_columns'])})")
            print(f"  Reasoning: {rule['reasoning']}")
            print(f"  LLM Generated: {'Yes' if rule['llm_generated'] else 'No'}")
            print()

    # Export to SQL
    print("=" * 70)
    print("  SQL EXPORT")
    print("=" * 70)
    print()

    try:
        ruleset_id = rules_result['ruleset_id']
        response = requests.get(f"{BASE_URL}/v1/reconciliation/rulesets/{ruleset_id}/export/sql")
        response.raise_for_status()
        sql_result = response.json()

        print(sql_result['sql'])
    except Exception as e:
        print(f"⚠️  Could not export to SQL: {e}")

    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print()
    print("✅ Success! Your reconciliation ruleset is ready.")
    print()
    print(f"  Ruleset ID: {rules_result['ruleset_id']}")
    print(f"  Rules Generated: {rules_result['rules_count']}")
    print(f"  Schemas: {', '.join(selected)}")
    print()
    print("You can view this ruleset anytime at:")
    print(f"  http://localhost:8000/v1/reconciliation/rulesets/{rules_result['ruleset_id']}")
    print()
    print("Or via API:")
    print(f"  curl http://localhost:8000/v1/reconciliation/rulesets/{rules_result['ruleset_id']}")
    print()
    print("Next steps:")
    print("  1. Review the generated rules")
    print("  2. Test rules with your actual data")
    print("  3. Integrate rules into your ETL pipeline")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
