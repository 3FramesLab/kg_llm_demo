"""
Test script for JDBC Database Connection API
Tests all database connection management endpoints.
"""
import requests
import json
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000/v1"
API_ENDPOINTS = {
    "test_connection": f"{BASE_URL}/database/test-connection",
    "add_connection": f"{BASE_URL}/database/connections",
    "list_connections": f"{BASE_URL}/database/connections",
    "remove_connection": f"{BASE_URL}/database/connections/{{connection_id}}",
    "list_databases": f"{BASE_URL}/database/connections/{{connection_id}}/databases",
    "list_tables": f"{BASE_URL}/database/connections/{{connection_id}}/databases/{{database_name}}/tables",
    "get_columns": f"{BASE_URL}/database/connections/{{connection_id}}/databases/{{database_name}}/tables/{{table_name}}/columns",
}


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_response(response: requests.Response):
    """Print formatted response."""
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_connection(connection_data: Dict[str, Any]):
    """Test 1: Test database connection."""
    print_section("TEST 1: Test Database Connection")
    
    try:
        response = requests.post(API_ENDPOINTS["test_connection"], json=connection_data)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def add_connection(connection_data: Dict[str, Any]) -> str:
    """Test 2: Add database connection."""
    print_section("TEST 2: Add Database Connection")
    
    try:
        response = requests.post(API_ENDPOINTS["add_connection"], json=connection_data)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                connection_id = data.get("connection", {}).get("id")
                print(f"\n✓ Connection added successfully! ID: {connection_id}")
                return connection_id
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def list_connections():
    """Test 3: List all connections."""
    print_section("TEST 3: List All Connections")
    
    try:
        response = requests.get(API_ENDPOINTS["list_connections"])
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            print(f"\n✓ Found {count} connection(s)")
            return data.get("connections", [])
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def list_databases(connection_id: str):
    """Test 4: List databases from connection."""
    print_section("TEST 4: List Databases from Connection")
    
    try:
        url = API_ENDPOINTS["list_databases"].format(connection_id=connection_id)
        response = requests.get(url)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            databases = data.get("databases", [])
            print(f"\n✓ Found {len(databases)} database(s)")
            return databases
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def list_tables(connection_id: str, database_name: str):
    """Test 5: List tables from database."""
    print_section(f"TEST 5: List Tables from Database '{database_name}'")
    
    try:
        url = API_ENDPOINTS["list_tables"].format(
            connection_id=connection_id,
            database_name=database_name
        )
        response = requests.get(url)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            tables = data.get("tables", [])
            print(f"\n✓ Found {len(tables)} table(s)")
            return tables
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_columns(connection_id: str, database_name: str, table_name: str):
    """Test 6: Get columns from table."""
    print_section(f"TEST 6: Get Columns from Table '{database_name}.{table_name}'")
    
    try:
        url = API_ENDPOINTS["get_columns"].format(
            connection_id=connection_id,
            database_name=database_name,
            table_name=table_name
        )
        response = requests.get(url)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            columns = data.get("columns", [])
            print(f"\n✓ Found {len(columns)} column(s)")
            return columns
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def remove_connection(connection_id: str):
    """Test 7: Remove connection."""
    print_section("TEST 7: Remove Database Connection")
    
    try:
        url = API_ENDPOINTS["remove_connection"].format(connection_id=connection_id)
        response = requests.delete(url)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print_section("JDBC Database Connection API Test Suite")
    print("This script tests all database connection management endpoints.")
    print("\nNOTE: Update the connection_data below with your actual database credentials.")
    
    # Example connection data - UPDATE WITH YOUR DATABASE CREDENTIALS
    connection_data = {
        "name": "Test MySQL Connection",
        "type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database": "",  # Empty for listing databases
        "username": "root",
        "password": "password"
    }
    
    print(f"\nUsing connection data:")
    print(json.dumps({**connection_data, "password": "***"}, indent=2))
    
    # Run tests
    connection_id = None
    
    try:
        # Test 1: Test connection
        if not test_connection(connection_data):
            print("\n❌ Connection test failed. Please check your credentials.")
            return
        
        # Test 2: Add connection
        connection_id = add_connection(connection_data)
        if not connection_id:
            print("\n❌ Failed to add connection.")
            return
        
        # Test 3: List connections
        connections = list_connections()
        
        # Test 4: List databases
        databases = list_databases(connection_id)
        if not databases:
            print("\n⚠ No databases found or failed to retrieve databases.")
            return
        
        # Test 5: List tables (use first database)
        if databases:
            first_db = databases[0]
            tables = list_tables(connection_id, first_db)
            
            # Test 6: Get columns (use first table if available)
            if tables:
                first_table = tables[0]
                get_columns(connection_id, first_db, first_table)
        
    finally:
        # Test 7: Cleanup - Remove connection
        if connection_id:
            remove_connection(connection_id)
    
    print_section("Test Suite Complete")
    print("All tests executed. Check the output above for results.")


if __name__ == "__main__":
    main()

