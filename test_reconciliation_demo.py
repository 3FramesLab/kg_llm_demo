"""
Demo script for testing reconciliation rule generation.

This script demonstrates the complete workflow of:
1. Creating a knowledge graph from multiple schemas
2. Generating reconciliation rules from the KG
3. Viewing and analyzing the generated rules
4. Exporting rules to SQL
"""

import requests
import json
import time
from pprint import pprint

# API base URL
BASE_URL = "http://localhost:8000"


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_health_check():
    """Test the health check endpoint."""
    print_header("1. Health Check")
    response = requests.get(f"{BASE_URL}/v1/health")
    print(f"Status Code: {response.status_code}")
    pprint(response.json())
    return response.json()


def list_available_schemas():
    """List available schemas."""
    print_header("2. List Available Schemas")
    response = requests.get(f"{BASE_URL}/v1/schemas")
    print(f"Status Code: {response.status_code}")
    result = response.json()
    pprint(result)
    return result.get('schemas', [])


def generate_knowledge_graph(schema_names, kg_name="test_reconciliation_kg"):
    """Generate a knowledge graph from multiple schemas."""
    print_header(f"3. Generate Knowledge Graph: {kg_name}")

    request_data = {
        "schema_names": schema_names,
        "kg_name": kg_name,
        "backends": ["falkordb"],
        "use_llm_enhancement": True
    }

    print("Request:")
    pprint(request_data)

    response = requests.post(f"{BASE_URL}/v1/kg/generate", json=request_data)
    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\nResponse:")
        pprint(result)
        return result
    else:
        print(f"Error: {response.text}")
        return None


def generate_reconciliation_rules(schema_names, kg_name="test_reconciliation_kg"):
    """Generate reconciliation rules from the knowledge graph."""
    print_header("4. Generate Reconciliation Rules")

    request_data = {
        "schema_names": schema_names,
        "kg_name": kg_name,
        "use_llm_enhancement": True,
        "min_confidence": 0.7,
        "match_types": ["exact", "semantic"]
    }

    print("Request:")
    pprint(request_data)

    response = requests.post(f"{BASE_URL}/v1/reconciliation/generate", json=request_data)
    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\nResponse:")
        print(f"Success: {result['success']}")
        print(f"Ruleset ID: {result['ruleset_id']}")
        print(f"Rules Count: {result['rules_count']}")
        print(f"Generation Time: {result['generation_time_ms']:.2f}ms")
        print(f"\nGenerated {len(result['rules'])} rules:\n")

        for i, rule in enumerate(result['rules'], 1):
            print(f"Rule {i}: {rule['rule_name']}")
            print(f"  Match Type: {rule['match_type']}")
            print(f"  Confidence: {rule['confidence_score']:.2f}")
            print(f"  Source: {rule['source_schema']}.{rule['source_table']} ({', '.join(rule['source_columns'])})")
            print(f"  Target: {rule['target_schema']}.{rule['target_table']} ({', '.join(rule['target_columns'])})")
            print(f"  Reasoning: {rule['reasoning']}")
            print(f"  LLM Generated: {rule['llm_generated']}")
            print()

        return result
    else:
        print(f"Error: {response.text}")
        return None


def list_rulesets():
    """List all saved rulesets."""
    print_header("5. List All Rulesets")

    response = requests.get(f"{BASE_URL}/v1/reconciliation/rulesets")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\nFound {result['count']} rulesets:\n")

        for ruleset in result['rulesets']:
            print(f"- {ruleset['ruleset_name']} (ID: {ruleset['ruleset_id']})")
            print(f"  Schemas: {', '.join(ruleset['schemas'])}")
            print(f"  Rules: {ruleset['rules_count']}")
            print(f"  Source KG: {ruleset['generated_from_kg']}")
            print(f"  Created: {ruleset['created_at']}")
            print()

        return result
    else:
        print(f"Error: {response.text}")
        return None


def get_ruleset_details(ruleset_id):
    """Get detailed information about a specific ruleset."""
    print_header(f"6. Get Ruleset Details: {ruleset_id}")

    response = requests.get(f"{BASE_URL}/v1/reconciliation/rulesets/{ruleset_id}")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        ruleset = result['ruleset']
        print(f"\nRuleset: {ruleset['ruleset_name']}")
        print(f"ID: {ruleset['ruleset_id']}")
        print(f"Schemas: {', '.join(ruleset['schemas'])}")
        print(f"Total Rules: {len(ruleset['rules'])}")
        print(f"Source KG: {ruleset['generated_from_kg']}")
        return result
    else:
        print(f"Error: {response.text}")
        return None


def export_ruleset_to_sql(ruleset_id):
    """Export a ruleset as SQL statements."""
    print_header(f"7. Export Ruleset to SQL: {ruleset_id}")

    response = requests.get(f"{BASE_URL}/v1/reconciliation/rulesets/{ruleset_id}/export/sql")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\nSQL Export:")
        print("-" * 80)
        print(result['sql'])
        print("-" * 80)
        return result
    else:
        print(f"Error: {response.text}")
        return None


def run_demo():
    """Run the complete demo workflow."""
    print("\n" + "=" * 80)
    print("  RECONCILIATION RULE GENERATION DEMO")
    print("=" * 80)

    try:
        # 1. Health check
        health = test_health_check()
        if not health.get('falkordb_connected'):
            print("\nWarning: FalkorDB not connected. Some features may not work.")
            time.sleep(2)

        # 2. List available schemas
        schemas = list_available_schemas()
        if not schemas:
            print("\nNo schemas found. Please add schema files to the schemas/ directory.")
            return

        # 3. Select schemas for reconciliation
        # Use the first two schemas if available
        if len(schemas) >= 2:
            selected_schemas = schemas[:2]
        else:
            print("\nNeed at least 2 schemas for reconciliation. Using available schema(s).")
            selected_schemas = schemas

        print(f"\nUsing schemas for reconciliation: {selected_schemas}")
        time.sleep(1)

        # 4. Generate knowledge graph
        kg_name = f"recon_kg_{int(time.time())}"
        kg_result = generate_knowledge_graph(selected_schemas, kg_name)

        if not kg_result or not kg_result.get('success'):
            print("\nFailed to generate knowledge graph. Exiting.")
            return

        time.sleep(1)

        # 5. Generate reconciliation rules
        rules_result = generate_reconciliation_rules(selected_schemas, kg_name)

        if not rules_result or not rules_result.get('success'):
            print("\nFailed to generate reconciliation rules. Exiting.")
            return

        ruleset_id = rules_result['ruleset_id']
        time.sleep(1)

        # 6. List all rulesets
        list_rulesets()
        time.sleep(1)

        # 7. Get ruleset details
        get_ruleset_details(ruleset_id)
        time.sleep(1)

        # 8. Export to SQL
        export_ruleset_to_sql(ruleset_id)

        print_header("Demo Complete!")
        print(f"✓ Knowledge graph '{kg_name}' created")
        print(f"✓ Reconciliation ruleset '{ruleset_id}' generated")
        print(f"✓ {rules_result['rules_count']} rules created")
        print(f"\nYou can view the ruleset at: {BASE_URL}/v1/reconciliation/rulesets/{ruleset_id}")

    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API server.")
        print("Please ensure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\nError occurred during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_demo()
