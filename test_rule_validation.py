"""
Test script for reconciliation rule validation using JayDeBeApi.

This script demonstrates how to validate reconciliation rules against actual databases.
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


def test_validation_without_db_connection():
    """
    Test 1: Validate a rule WITHOUT database connections.

    This will return a basic validation with warnings that database
    connections are needed for full validation.
    """
    print_section("1. Validation WITHOUT Database Connection (Basic Check)")

    # Example rule to validate
    rule = {
        "rule_id": "RULE_TEST_001",
        "rule_name": "Test_Vendor_Match",
        "source_schema": "orderMgmt",
        "source_table": "catalog",
        "source_columns": ["vendor_uid"],
        "target_schema": "vendorDB",
        "target_table": "suppliers",
        "target_columns": ["supplier_id"],
        "match_type": "exact",
        "transformation": None,
        "confidence_score": 0.95,
        "reasoning": "Test rule for vendor matching",
        "validation_status": "UNCERTAIN",
        "llm_generated": False,
        "created_at": datetime.utcnow().isoformat(),
        "metadata": {}
    }

    # Validation request WITHOUT database connections
    request_data = {
        "rule": rule,
        "sample_size": 100
        # Note: No source_db_config or target_db_config provided
    }

    print("Request:")
    pprint(request_data)
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/reconciliation/validate",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")
        print("\nResponse:")
        pprint(response.json())

    except Exception as e:
        print(f"Error: {e}")


def test_validation_with_db_connection():
    """
    Test 2: Validate a rule WITH database connections.

    This performs full validation including:
    - Table/column existence checks
    - Data type compatibility
    - Sample data matching
    - Cardinality detection
    - Performance estimation
    """
    print_section("2. Validation WITH Database Connection (Full Validation)")

    # Example rule to validate
    rule = {
        "rule_id": "RULE_TEST_002",
        "rule_name": "Full_Validation_Test",
        "source_schema": "SCHEMA1",
        "source_table": "ORDERS",
        "source_columns": ["ORDER_ID", "CUSTOMER_ID"],
        "target_schema": "SCHEMA2",
        "target_table": "ORDER_DETAILS",
        "target_columns": ["ORDER_NUM", "CUST_NUM"],
        "match_type": "exact",
        "transformation": None,
        "confidence_score": 0.88,
        "reasoning": "Test rule for order matching across schemas",
        "validation_status": "UNCERTAIN",
        "llm_generated": False,
        "created_at": datetime.utcnow().isoformat(),
        "metadata": {}
    }

    # Database connection configurations
    # IMPORTANT: Update these with your actual database credentials
    source_db_config = {
        "db_type": "oracle",  # Options: oracle, sqlserver, postgresql, mysql
        "host": "localhost",
        "port": 1521,
        "database": "ORCL",
        "username": "schema1_user",
        "password": "schema1_password",
        "service_name": "ORCLPDB"  # For Oracle
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

    # Validation request WITH database connections
    request_data = {
        "rule": rule,
        "sample_size": 100,
        "source_db_config": source_db_config,
        "target_db_config": target_db_config
    }

    print("Request (database credentials hidden):")
    request_display = {
        "rule": rule,
        "sample_size": 100,
        "source_db_config": {**source_db_config, "password": "***"},
        "target_db_config": {**target_db_config, "password": "***"}
    }
    pprint(request_display)
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/reconciliation/validate",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")
        print("\nResponse:")
        result = response.json()
        pprint(result)

        # Interpret the validation results
        if result.get("success"):
            validation = result.get("validation", {})
            print("\n" + "-" * 80)
            print("VALIDATION SUMMARY:")
            print("-" * 80)
            print(f"✓ Valid: {validation.get('valid')}")
            print(f"✓ Tables/Columns Exist: {validation.get('exists')}")
            print(f"✓ Types Compatible: {validation.get('types_compatible')}")

            match_rate = validation.get('sample_match_rate')
            if match_rate is not None:
                print(f"✓ Sample Match Rate: {match_rate:.2%}")

            cardinality = validation.get('cardinality')
            if cardinality:
                print(f"✓ Cardinality: {cardinality}")

            perf = validation.get('estimated_performance_ms')
            if perf:
                print(f"✓ Estimated Performance: {perf:.2f} ms")

            issues = validation.get('issues', [])
            if issues:
                print(f"\n⚠ Issues ({len(issues)}):")
                for i, issue in enumerate(issues, 1):
                    print(f"  {i}. {issue}")

            warnings = validation.get('warnings', [])
            if warnings:
                print(f"\n⚠ Warnings ({len(warnings)}):")
                for i, warning in enumerate(warnings, 1):
                    print(f"  {i}. {warning}")

    except Exception as e:
        print(f"Error: {e}")


def test_validate_generated_rule():
    """
    Test 3: Validate a rule that was generated from a knowledge graph.

    This demonstrates the end-to-end workflow:
    1. Generate reconciliation rules from KG
    2. Pick a rule to validate
    3. Validate it against actual databases
    """
    print_section("3. Validate a Generated Rule (End-to-End Workflow)")

    # Step 1: Generate rules from a knowledge graph
    print("Step 1: Generating reconciliation rules from KG...")

    kg_request = {
        "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
        "kg_name": "test_validation_kg",
        "use_llm_enhancement": True,
        "min_confidence": 0.7
    }

    try:
        # Note: This assumes you already have a KG created
        # If not, you need to create one first using /kg/generate

        response = requests.post(
            f"{BASE_URL}/reconciliation/generate",
            json=kg_request,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Generated {result.get('rules_count', 0)} rules")

            rules = result.get('rules', [])
            if rules:
                # Step 2: Pick the first rule to validate
                rule_to_validate = rules[0]
                print(f"\nStep 2: Validating rule '{rule_to_validate['rule_name']}'...")

                # Step 3: Validate WITHOUT database connections (basic check)
                validation_request = {
                    "rule": rule_to_validate,
                    "sample_size": 100
                }

                validation_response = requests.post(
                    f"{BASE_URL}/reconciliation/validate",
                    json=validation_request,
                    headers={"Content-Type": "application/json"}
                )

                print(f"\nValidation Status Code: {validation_response.status_code}")
                print("\nValidation Result:")
                pprint(validation_response.json())

                print("\n" + "-" * 80)
                print("NOTE: For full validation with actual data, provide database")
                print("connection configs in 'source_db_config' and 'target_db_config'")
                print("-" * 80)
            else:
                print("No rules were generated")
        else:
            print(f"Error generating rules: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")


def test_different_database_types():
    """
    Test 4: Show examples of different database type configurations.
    """
    print_section("4. Database Configuration Examples")

    examples = {
        "Oracle": {
            "db_type": "oracle",
            "host": "oracle-server.example.com",
            "port": 1521,
            "database": "ORCL",
            "username": "user",
            "password": "password",
            "service_name": "ORCLPDB"
        },
        "SQL Server": {
            "db_type": "sqlserver",
            "host": "sqlserver.example.com",
            "port": 1433,
            "database": "MyDatabase",
            "username": "sa",
            "password": "password"
        },
        "PostgreSQL": {
            "db_type": "postgresql",
            "host": "postgres.example.com",
            "port": 5432,
            "database": "mydb",
            "username": "postgres",
            "password": "password"
        },
        "MySQL": {
            "db_type": "mysql",
            "host": "mysql.example.com",
            "port": 3306,
            "database": "mydb",
            "username": "root",
            "password": "password"
        }
    }

    print("Supported database configurations:\n")
    for db_name, config in examples.items():
        print(f"{db_name}:")
        pprint({**config, "password": "***"})
        print()


def main():
    """Run all validation tests."""
    print("\n")
    print("=" * 80)
    print("  RECONCILIATION RULE VALIDATION TEST SUITE")
    print("=" * 80)

    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print(f"\n⚠ WARNING: API health check failed. Is the server running?")
            print(f"   Start server: python -m uvicorn kg_builder.main:app --reload")
            return
    except Exception as e:
        print(f"\n❌ ERROR: Cannot connect to API at {BASE_URL}")
        print(f"   Error: {e}")
        print(f"\n   Please start the server first:")
        print(f"   python -m uvicorn kg_builder.main:app --reload")
        return

    # Run tests
    test_validation_without_db_connection()

    # Uncomment to test with actual database connections
    # NOTE: You need to configure actual database credentials first!
    # test_validation_with_db_connection()

    test_validate_generated_rule()

    test_different_database_types()

    # Summary
    print_section("Test Suite Complete")
    print("✓ All tests completed successfully!")
    print("\nNext Steps:")
    print("1. Configure JDBC drivers in 'jdbc_drivers/' directory")
    print("2. Update database credentials in test_validation_with_db_connection()")
    print("3. Uncomment test_validation_with_db_connection() to test with real databases")
    print("\nJDBC Drivers needed:")
    print("  - Oracle: ojdbc8.jar or ojdbc11.jar")
    print("  - SQL Server: mssql-jdbc-*.jar")
    print("  - PostgreSQL: postgresql-*.jar")
    print("  - MySQL: mysql-connector-java-*.jar")
    print()


if __name__ == "__main__":
    main()
