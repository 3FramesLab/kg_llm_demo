"""
Quick test script to verify hints API is working.
Run this after starting the backend server.
"""
import requests
import json

BASE_URL = "http://localhost:8000/v1"

def test_hints_api():
    """Test hints API endpoints."""
    print("Testing Column Hints API...\n")

    # Test 1: Get statistics
    print("1. Testing GET /hints/statistics")
    try:
        response = requests.get(f"{BASE_URL}/hints/statistics")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Total tables: {data['data']['total_tables']}")
            print(f"   ✓ Total columns: {data['data']['total_columns']}")
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

    print()

    # Test 2: Get all hints
    print("2. Testing GET /hints/")
    try:
        response = requests.get(f"{BASE_URL}/hints/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tables = data['data']['tables']
            print(f"   ✓ Loaded {len(tables)} tables")
            print(f"   ✓ Tables: {', '.join(list(tables.keys())[:3])}...")
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

    print()

    # Test 3: Get table hints
    print("3. Testing GET /hints/table/hana_material_master")
    try:
        response = requests.get(f"{BASE_URL}/hints/table/hana_material_master")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            table_hints = data['data']['table_hints']
            columns = data['data']['columns']
            print(f"   ✓ Business Name: {table_hints['business_name']}")
            print(f"   ✓ Columns: {len(columns)}")
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

    print()

    # Test 4: Search hints
    print("4. Testing POST /hints/search (search term: 'material')")
    try:
        response = requests.post(
            f"{BASE_URL}/hints/search",
            json={"search_term": "material", "limit": 5}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data['data']
            print(f"   ✓ Found {data['total_found']} matches")
            if results:
                print(f"   ✓ First match: {results[0]['table_name']}.{results[0]['column_name']}")
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    print("\nIf all tests passed, the API is working correctly.")
    print("You can now access the UI at: http://localhost:3000/hints-management")

if __name__ == "__main__":
    print("="*60)
    print("Column Hints API Test")
    print("="*60)
    print("Make sure the backend is running: uvicorn kg_builder.main:app --reload")
    print("="*60 + "\n")

    test_hints_api()
