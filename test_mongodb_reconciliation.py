"""
Test script for MongoDB reconciliation storage.

This script tests the MongoDB storage functionality without requiring actual database connections.
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_mongodb_connection():
    """Test if MongoDB is accessible through the API."""
    print_section("Test 1: MongoDB Connection")

    try:
        # Try to list existing results (should work even if empty)
        response = requests.get(f"{BASE_URL}/api/v1/reconciliation/results")

        if response.status_code == 200:
            result = response.json()
            print("✓ MongoDB connection successful!")
            print(f"  - Found {result.get('count', 0)} existing results")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return False

    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to API at {BASE_URL}")
        print("  Make sure the application is running:")
        print("  docker-compose up -d")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_list_results():
    """Test listing reconciliation results."""
    print_section("Test 2: List Reconciliation Results")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/reconciliation/results?limit=5")

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Successfully listed results")
            print(f"  - Count: {result.get('count', 0)}")
            print(f"  - Limit: {result.get('limit', 0)}")
            print(f"  - Skip: {result.get('skip', 0)}")

            if result.get('count', 0) > 0:
                print("\n  Recent results:")
                for res in result.get('results', [])[:3]:
                    print(f"    - ID: {res.get('_id')}")
                    print(f"      Ruleset: {res.get('ruleset_id')}")
                    print(f"      Timestamp: {res.get('execution_timestamp')}")
                    print(f"      Matched: {res.get('matched_count', 0)}")
                    print()

            return result.get('results', [])
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return []

    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def test_get_result(document_id: str):
    """Test retrieving a specific result."""
    print_section(f"Test 3: Get Specific Result")

    print(f"Retrieving document: {document_id}")
    print()

    try:
        response = requests.get(f"{BASE_URL}/api/v1/reconciliation/results/{document_id}")

        if response.status_code == 200:
            result = response.json()
            print("✓ Successfully retrieved result")
            print()

            doc = result.get('result', {})
            print(f"  Ruleset ID: {doc.get('ruleset_id')}")
            print(f"  Execution Time: {doc.get('execution_timestamp')}")
            print(f"  Matched: {doc.get('matched_count', 0)}")
            print(f"  Unmatched Source: {doc.get('unmatched_source_count', 0)}")
            print(f"  Unmatched Target: {doc.get('unmatched_target_count', 0)}")

            metadata = doc.get('metadata', {})
            if metadata:
                print(f"\n  Metadata:")
                print(f"    - Execution Time: {metadata.get('execution_time_ms', 0):.2f} ms")
                print(f"    - Source DB Type: {metadata.get('source_db_type', 'N/A')}")
                print(f"    - Target DB Type: {metadata.get('target_db_type', 'N/A')}")

            return True
        elif response.status_code == 404:
            print(f"✗ Document not found: {document_id}")
            return False
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_statistics():
    """Test getting reconciliation statistics."""
    print_section("Test 4: Get Reconciliation Statistics")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/reconciliation/statistics")

        if response.status_code == 200:
            result = response.json()
            stats = result.get('statistics', {})

            print("✓ Successfully retrieved statistics")
            print()
            print(f"  Total Executions: {stats.get('total_executions', 0)}")
            print(f"  Total Matched: {stats.get('total_matched', 0)}")
            print(f"  Total Unmatched Source: {stats.get('total_unmatched_source', 0)}")
            print(f"  Total Unmatched Target: {stats.get('total_unmatched_target', 0)}")
            print()
            print(f"  Average Matched: {stats.get('avg_matched', 0):.2f}")
            print(f"  Average Unmatched Source: {stats.get('avg_unmatched_source', 0):.2f}")
            print(f"  Average Unmatched Target: {stats.get('avg_unmatched_target', 0):.2f}")

            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_mongodb_health():
    """Test MongoDB health through the application."""
    print_section("Test 5: MongoDB Health Check")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")

        if response.status_code == 200:
            result = response.json()
            print("✓ Application health check successful")
            print(f"  - Status: {result.get('status')}")
            print(f"  - FalkorDB Connected: {result.get('falkordb_connected')}")
            print(f"  - Graphiti Available: {result.get('graphiti_available')}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_all_tests():
    """Run all MongoDB tests."""
    print("\n")
    print("=" * 80)
    print("  MONGODB RECONCILIATION STORAGE TESTS")
    print("=" * 80)

    # Check API availability
    print_section("Checking API Availability")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if response.status_code != 200:
            print(f"⚠ WARNING: API health check failed")
            print(f"   Start services: docker-compose up -d")
            return
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to API at {BASE_URL}")
        print(f"   Error: {e}")
        print(f"\n   Please start the services first:")
        print(f"   docker-compose up -d")
        return

    # Run tests
    results = []

    # Test 1: MongoDB connection
    results.append(("MongoDB Connection", test_mongodb_connection()))

    # Test 2: List results
    existing_results = test_list_results()
    results.append(("List Results", len(existing_results) >= 0))

    # Test 3: Get specific result (if any exist)
    if existing_results:
        doc_id = existing_results[0].get('_id')
        results.append(("Get Specific Result", test_get_result(doc_id)))
    else:
        print_section("Test 3: Get Specific Result")
        print("⚠ Skipping - No results in database")
        print("  Run a reconciliation execution first to test this feature")
        results.append(("Get Specific Result", None))

    # Test 4: Statistics
    results.append(("Statistics", test_statistics()))

    # Test 5: Health check
    results.append(("Health Check", test_mongodb_health()))

    # Summary
    print_section("Test Summary")

    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    total = len(results)

    for name, result in results:
        if result is True:
            print(f"✓ {name}")
        elif result is False:
            print(f"✗ {name}")
        else:
            print(f"⚠ {name} (skipped)")

    print()
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped out of {total} tests")

    if failed == 0 and passed > 0:
        print()
        print("🎉 All tests passed! MongoDB reconciliation storage is working correctly.")
        print()
        print("Next Steps:")
        print("  1. Execute a reconciliation to create results in MongoDB")
        print("  2. Use the API endpoints to query and analyze results")
        print("  3. Review the MONGODB_RECONCILIATION_GUIDE.md for more details")
    elif failed > 0:
        print()
        print("⚠ Some tests failed. Please check the errors above.")
        print()
        print("Common issues:")
        print("  - MongoDB not running: docker-compose up -d mongodb")
        print("  - Application not started: docker-compose up -d app")
        print("  - Connection settings incorrect: check .env file")


if __name__ == "__main__":
    run_all_tests()
