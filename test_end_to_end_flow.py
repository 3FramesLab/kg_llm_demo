"""
End-to-End Test for Database Schema Retrieval via JDBC
Tests the complete flow from API endpoint to JDBC connection to metadata retrieval.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/v1"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_connection_api(connection_data):
    """Test the database connection via API."""
    print_section("TEST 1: Test Database Connection API")
    
    print(f"\n[1/2] Testing connection to {connection_data['type']} at {connection_data['host']}:{connection_data['port']}")
    print(f"  Database: {connection_data['database']}")
    print(f"  Username: {connection_data['username']}")
    
    try:
        response = requests.post(f"{BASE_URL}/database/test-connection", json=connection_data)
        print(f"\n[2/2] Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success: {result.get('message', 'Connection successful')}")
            return True
        else:
            print(f"✗ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def add_connection_api(connection_data):
    """Add a database connection via API."""
    print_section("TEST 2: Add Database Connection API")
    
    print(f"\n[1/3] Adding connection '{connection_data['name']}'...")
    
    try:
        response = requests.post(f"{BASE_URL}/database/connections", json=connection_data)
        print(f"\n[2/3] Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                connection_id = result['connection']['id']
                print(f"✓ Connection added successfully!")
                print(f"  Connection ID: {connection_id}")
                print(f"  Name: {result['connection']['name']}")
                print(f"  Type: {result['connection']['type']}")
                print(f"  Status: {result['connection']['status']}")
                return connection_id
            else:
                print(f"✗ Failed: {result.get('message', 'Unknown error')}")
                return None
        else:
            print(f"✗ Failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def list_connections_api():
    """List all database connections via API."""
    print_section("TEST 3: List Database Connections API")
    
    try:
        response = requests.get(f"{BASE_URL}/database/connections")
        
        if response.status_code == 200:
            result = response.json()
            connections = result.get('connections', [])
            print(f"\n✓ Found {len(connections)} connection(s):")
            for conn in connections:
                print(f"  - {conn['name']} ({conn['type']}) - {conn['host']}:{conn['port']}")
            return connections
        else:
            print(f"✗ Failed: {response.text}")
            return []
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def list_databases_api(connection_id):
    """List databases from a connection via API."""
    print_section("TEST 4: List Databases via JDBC")
    
    print(f"\n[1/2] Retrieving databases for connection {connection_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/database/connections/{connection_id}/databases")
        print(f"\n[2/2] Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                databases = result.get('databases', [])
                print(f"✓ Found {len(databases)} database(s):")
                for db in databases:
                    print(f"  - {db}")
                return databases
            else:
                print(f"✗ Failed: {result.get('message', 'Unknown error')}")
                return []
        else:
            print(f"✗ Failed: {response.text}")
            return []
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def list_tables_api(connection_id, database_name):
    """List tables from a database via API."""
    print_section("TEST 5: List Tables via JDBC")
    
    print(f"\n[1/2] Retrieving tables from database '{database_name}'...")
    
    try:
        response = requests.get(f"{BASE_URL}/database/connections/{connection_id}/databases/{database_name}/tables")
        print(f"\n[2/2] Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                tables = result.get('tables', [])
                print(f"✓ Found {len(tables)} table(s):")
                for table in tables[:10]:  # Show first 10
                    print(f"  - {table}")
                if len(tables) > 10:
                    print(f"  ... and {len(tables) - 10} more")
                return tables
            else:
                print(f"✗ Failed: {result.get('message', 'Unknown error')}")
                return []
        else:
            print(f"✗ Failed: {response.text}")
            return []
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def get_table_columns_api(connection_id, database_name, table_name):
    """Get columns from a table via API."""
    print_section("TEST 6: Get Table Columns via JDBC")

    print(f"\n[1/2] Retrieving columns from table '{database_name}.{table_name}'...")

    try:
        response = requests.get(f"{BASE_URL}/database/connections/{connection_id}/databases/{database_name}/tables/{table_name}/columns")
        print(f"\n[2/2] Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                columns = result.get('columns', [])
                print(f"✓ Found {len(columns)} column(s):")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                return columns
            else:
                print(f"✗ Failed: {result.get('message', 'Unknown error')}")
                return []
        else:
            print(f"✗ Failed: {response.text}")
            return []
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def delete_connection_api(connection_id):
    """Delete a database connection via API."""
    print_section("TEST 7: Delete Database Connection API")

    print(f"\n[1/2] Deleting connection {connection_id}...")

    try:
        response = requests.delete(f"{BASE_URL}/database/connections/{connection_id}")
        print(f"\n[2/2] Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✓ Connection deleted successfully")
                return True
            else:
                print(f"✗ Failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"✗ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run the complete end-to-end test."""
    print("\n" + "=" * 80)
    print("  END-TO-END DATABASE SCHEMA RETRIEVAL TEST")
    print("  Testing complete flow: Frontend → Backend API → JDBC → Database")
    print("=" * 80)

    # Test configuration - Use an existing database
    connection_data = {
        "name": "Test MySQL Connection",
        "type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database": "demo_server_db",  # Use existing database
        "username": "root",
        "password": "3frames",
        "service_name": ""
    }

    print("\nTest Configuration:")
    print(f"  Database Type: {connection_data['type']}")
    print(f"  Host: {connection_data['host']}:{connection_data['port']}")
    print(f"  Database: {connection_data['database']}")
    print(f"  Username: {connection_data['username']}")

    results = []

    # Test 1: Test Connection
    results.append(("Test Connection", test_connection_api(connection_data)))

    if not results[0][1]:
        print("\n⚠ Connection test failed. Stopping tests.")
        return

    # Test 2: Add Connection
    connection_id = add_connection_api(connection_data)
    results.append(("Add Connection", connection_id is not None))

    if not connection_id:
        print("\n⚠ Failed to add connection. Stopping tests.")
        return

    # Test 3: List Connections
    connections = list_connections_api()
    results.append(("List Connections", len(connections) > 0))

    # Test 4: List Databases
    databases = list_databases_api(connection_id)
    results.append(("List Databases", len(databases) > 0))

    # Test 5: List Tables (if we have databases)
    tables = []
    if databases:
        # Use the first non-system database or the specified database
        test_db = connection_data['database'] if connection_data['database'] in databases else databases[0]
        tables = list_tables_api(connection_id, test_db)
        results.append(("List Tables", len(tables) > 0))

        # Test 6: Get Table Columns (if we have tables)
        if tables:
            test_table = tables[0]
            columns = get_table_columns_api(connection_id, test_db, test_table)
            results.append(("Get Table Columns", len(columns) > 0))

    # Test 7: Delete Connection
    results.append(("Delete Connection", delete_connection_api(connection_id)))

    # Summary
    print_section("TEST SUMMARY")

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! End-to-end flow is working correctly.")
        print("\nThe complete flow is verified:")
        print("  ✓ Frontend can test database connections")
        print("  ✓ Frontend can add database connections")
        print("  ✓ Backend can list all connections")
        print("  ✓ Backend can retrieve databases via JDBC")
        print("  ✓ Backend can retrieve tables via JDBC")
        print("  ✓ Backend can retrieve columns via JDBC")
        print("  ✓ Frontend can delete connections")
    else:
        print("\n⚠ Some tests failed. Check the error messages above for details.")

    print("=" * 80)

if __name__ == "__main__":
    main()


