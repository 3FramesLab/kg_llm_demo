"""
Demo script for reconciliation execution using SQL export approach.

This script demonstrates the complete reconciliation workflow:
1. Generate reconciliation rules from a knowledge graph
2. Export rules as SQL queries
3. Execute reconciliation (SQL export mode or direct execution mode)
"""

import requests
import json
from pprint import pprint
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80 + "\n")


def step_1_list_available_schemas():
    """List available schemas."""
    print_section("STEP 1: List Available Schemas")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/schemas")

        if response.status_code == 200:
            result = response.json()
            schemas = result.get('schemas', [])
            print(f"✓ Found {len(schemas)} schemas:")
            for schema in schemas:
                print(f"  - {schema}")
            return schemas
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return []

    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def step_2_generate_knowledge_graph(schema_names: list):
    """Generate a knowledge graph from schemas."""
    print_section("STEP 2: Generate Knowledge Graph")

    kg_name = "demo_reconciliation_kg"

    request_data = {
        "schema_names": schema_names,
        "kg_name": kg_name,
        "backends": ["falkordb", "graphiti"],
        "use_llm_enhancement": True
    }

    print(f"Generating KG '{kg_name}' from schemas: {', '.join(schema_names)}")
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/kg/generate",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Knowledge graph created successfully!")
            print(f"  - Nodes: {result.get('nodes_count', 0)}")
            print(f"  - Relationships: {result.get('relationships_count', 0)}")
            print(f"  - Generation time: {result.get('generation_time_ms', 0):.2f} ms")
            return kg_name
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def step_3_generate_reconciliation_rules(schema_names: list, kg_name: str):
    """Generate reconciliation rules from the knowledge graph."""
    print_section("STEP 3: Generate Reconciliation Rules")

    request_data = {
        "schema_names": schema_names,
        "kg_name": kg_name,
        "use_llm_enhancement": True,
        "min_confidence": 0.7
    }

    print(f"Generating rules from KG '{kg_name}'...")
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/reconciliation/generate",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            ruleset_id = result.get('ruleset_id')
            rules = result.get('rules', [])

            print(f"✓ Generated {len(rules)} reconciliation rules")
            print(f"  - Ruleset ID: {ruleset_id}")
            print()

            # Show first 3 rules
            print("Sample rules:")
            for i, rule in enumerate(rules[:3], 1):
                print(f"\n  Rule {i}: {rule['rule_name']}")
                print(f"    Source: {rule['source_schema']}.{rule['source_table']}[{', '.join(rule['source_columns'])}]")
                print(f"    Target: {rule['target_schema']}.{rule['target_table']}[{', '.join(rule['target_columns'])}]")
                print(f"    Match Type: {rule['match_type']}")
                print(f"    Confidence: {rule['confidence_score']:.2f}")
                print(f"    Reasoning: {rule['reasoning']}")

            if len(rules) > 3:
                print(f"\n  ... and {len(rules) - 3} more rules")

            return ruleset_id

        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def step_4_export_sql_queries(ruleset_id: str, query_type: str = "all"):
    """Export reconciliation rules as SQL queries."""
    print_section(f"STEP 4: Export SQL Queries (type={query_type})")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/reconciliation/rulesets/{ruleset_id}/export/sql",
            params={"query_type": query_type}
        )

        if response.status_code == 200:
            result = response.json()
            sql = result.get('sql', '')

            print(f"✓ SQL queries exported successfully!")
            print(f"  - Ruleset ID: {result.get('ruleset_id')}")
            print(f"  - Query Type: {result.get('query_type')}")
            print()

            # Save to file
            filename = f"reconciliation_queries_{ruleset_id}_{query_type}.sql"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(sql)

            print(f"✓ SQL queries saved to: {filename}")
            print()

            # Show preview
            lines = sql.split('\n')
            preview_lines = 50
            print(f"Preview (first {preview_lines} lines):")
            print("-" * 80)
            print('\n'.join(lines[:preview_lines]))
            if len(lines) > preview_lines:
                print(f"... and {len(lines) - preview_lines} more lines")
            print("-" * 80)

            return sql

        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def step_5_execute_sql_export_mode(ruleset_id: str):
    """Execute reconciliation in SQL export mode (no database connection)."""
    print_section("STEP 5: Execute Reconciliation (SQL Export Mode)")

    print("This mode generates SQL queries without executing them.")
    print("You can then run these queries manually in your database client.")
    print()

    request_data = {
        "ruleset_id": ruleset_id,
        "limit": 100
        # Note: No source_db_config or target_db_config provided
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/reconciliation/execute",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()

            print(f"✓ SQL queries generated!")
            print(f"  - Mode: {result.get('mode')}")
            print(f"  - Message: {result.get('message')}")
            print()

            print("Instructions:")
            for i, instruction in enumerate(result.get('instructions', []), 1):
                print(f"  {i}. {instruction}")
            print()

            # Save SQL to file
            sql = result.get('sql', '')
            if sql:
                filename = f"reconciliation_execution_{ruleset_id}.sql"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(sql)
                print(f"✓ SQL queries saved to: {filename}")

            return result

        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def step_6_execute_direct_mode(ruleset_id: str):
    """Execute reconciliation in direct execution mode (with database connection)."""
    print_section("STEP 6: Execute Reconciliation (Direct Execution Mode)")

    print("⚠️  This mode requires:")
    print("  1. JayDeBeApi installed: pip install JayDeBeApi")
    print("  2. JDBC drivers in jdbc_drivers/ directory")
    print("  3. Actual database connections")
    print()

    # Example database configurations
    source_db_config = {
        "db_type": "oracle",
        "host": "localhost",
        "port": 1521,
        "database": "ORCL",
        "username": "schema1_user",
        "password": "schema1_password",
        "service_name": "ORCLPDB"
    }

    target_db_config = {
        "db_type": "oracle",
        "host": "localhost",
        "port": 1521,
        "database": "ORCL",
        "username": "schema2_user",
        "password": "schema2_password",
        "service_name": "ORCLPDB"
    }

    request_data = {
        "ruleset_id": ruleset_id,
        "limit": 100,
        "source_db_config": source_db_config,
        "target_db_config": target_db_config,
        "include_matched": True,
        "include_unmatched": True
    }

    print("This is a DEMO - not executing with real database credentials.")
    print("To execute with real databases, update the database configs above.")
    print()

    print("Example request:")
    # Hide passwords
    display_request = {
        **request_data,
        "source_db_config": {**source_db_config, "password": "***"},
        "target_db_config": {**target_db_config, "password": "***"}
    }
    pprint(display_request)

    print()
    print("To execute with real databases, uncomment the code below and")
    print("update the database configurations with your actual credentials.")

    # Uncomment to execute with real databases:
    # try:
    #     response = requests.post(
    #         f"{BASE_URL}/api/v1/reconciliation/execute",
    #         json=request_data,
    #         headers={"Content-Type": "application/json"}
    #     )
    #
    #     if response.status_code == 200:
    #         result = response.json()
    #
    #         print(f"✓ Reconciliation executed successfully!")
    #         print(f"  - Matched: {result.get('matched_count', 0)}")
    #         print(f"  - Unmatched Source: {result.get('unmatched_source_count', 0)}")
    #         print(f"  - Unmatched Target: {result.get('unmatched_target_count', 0)}")
    #         print(f"  - Execution Time: {result.get('execution_time_ms', 0):.2f} ms")
    #
    #         return result
    #     else:
    #         print(f"✗ Error: {response.status_code}")
    #         print(response.text)
    #         return None
    #
    # except Exception as e:
    #     print(f"✗ Error: {e}")
    #     return None


def demo_workflow():
    """Run the complete reconciliation workflow demo."""
    print("\n")
    print("=" * 80)
    print("  RECONCILIATION EXECUTION DEMO")
    print("  SQL Export Approach")
    print("=" * 80)

    # Check API availability
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code != 200:
            print(f"\n⚠ WARNING: API health check failed.")
            print(f"   Start server: python -m uvicorn kg_builder.main:app --reload")
            return
    except Exception as e:
        print(f"\n❌ ERROR: Cannot connect to API at {BASE_URL}")
        print(f"   Error: {e}")
        print(f"\n   Please start the server first:")
        print(f"   python -m uvicorn kg_builder.main:app --reload")
        return

    # Step 1: List schemas
    schemas = step_1_list_available_schemas()

    if len(schemas) < 2:
        print("\n⚠️  Need at least 2 schemas for reconciliation demo.")
        print("   Please add schema files to the schemas/ directory.")
        return

    # Use first 2 schemas for demo
    demo_schemas = schemas[:2]

    # Step 2: Generate KG
    kg_name = step_2_generate_knowledge_graph(demo_schemas)
    if not kg_name:
        print("\n⚠️  Failed to generate knowledge graph. Stopping demo.")
        return

    # Step 3: Generate rules
    ruleset_id = step_3_generate_reconciliation_rules(demo_schemas, kg_name)
    if not ruleset_id:
        print("\n⚠️  Failed to generate reconciliation rules. Stopping demo.")
        return

    # Step 4: Export SQL queries (different types)
    step_4_export_sql_queries(ruleset_id, query_type="all")
    step_4_export_sql_queries(ruleset_id, query_type="matched")

    # Step 5: Execute in SQL export mode
    step_5_execute_sql_export_mode(ruleset_id)

    # Step 6: Show direct execution example
    step_6_execute_direct_mode(ruleset_id)

    # Summary
    print_section("DEMO COMPLETE")
    print("✓ Reconciliation workflow completed successfully!")
    print()
    print("Next Steps:")
    print("  1. Review the generated SQL files")
    print("  2. Run the SQL queries in your database client")
    print("  3. Review matched and unmatched records")
    print("  4. For automated execution:")
    print("     - Install JayDeBeApi: pip install JayDeBeApi")
    print("     - Add JDBC drivers to jdbc_drivers/ directory")
    print("     - Update database configs in step_6_execute_direct_mode()")
    print("     - Uncomment the execution code")
    print()
    print("Generated Files:")
    print(f"  - reconciliation_queries_{ruleset_id}_all.sql")
    print(f"  - reconciliation_queries_{ruleset_id}_matched.sql")
    print(f"  - reconciliation_execution_{ruleset_id}.sql")
    print()


if __name__ == "__main__":
    demo_workflow()
