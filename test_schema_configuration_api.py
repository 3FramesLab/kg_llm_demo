"""
Test script for schema configuration API endpoints.
Tests both POST (save) and GET (retrieve) endpoints.
"""
import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/v1"

def test_get_schema_configurations():
    """Test retrieving all schema configurations."""
    print("\n" + "="*80)
    print("TEST 1: GET /database/schema-configuration")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/database/schema-configuration")
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"\nResponse:")
            print(f"  - Success: {data.get('success')}")
            print(f"  - Count: {data.get('count')}")
            print(f"  - Message: {data.get('message')}")
            
            if data.get('configurations'):
                print(f"\n📋 Configurations Found:")
                for idx, config in enumerate(data['configurations'], 1):
                    print(f"\n  Configuration {idx}:")
                    print(f"    - ID: {config.get('id')}")
                    print(f"    - Created: {config.get('created_at')}")
                    print(f"    - Tables: {config.get('summary', {}).get('total_tables')}")
                    print(f"    - Columns: {config.get('summary', {}).get('total_columns')}")
                    print(f"    - Databases: {', '.join(config.get('summary', {}).get('databases', []))}")
                    print(f"    - Connections: {', '.join(config.get('summary', {}).get('connections', []))}")
            else:
                print("\n  No configurations found.")
            
            return data
        else:
            print(f"\n❌ FAILED")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None


def test_save_schema_configuration():
    """Test saving a new schema configuration."""
    print("\n" + "="*80)
    print("TEST 2: POST /database/schema-configuration")
    print("="*80)
    
    # Sample configuration data
    test_config = {
        "tables": [
            {
                "connectionId": "test-connection-123",
                "connectionName": "Test MySQL Connection",
                "databaseName": "test_database",
                "tableName": "users",
                "tableAliases": ["user", "customer"],
                "columns": [
                    {
                        "name": "id",
                        "aliases": ["user_id", "customer_id"]
                    },
                    {
                        "name": "email",
                        "aliases": ["user_email"]
                    },
                    {
                        "name": "name",
                        "aliases": ["full_name", "username"]
                    }
                ]
            },
            {
                "connectionId": "test-connection-123",
                "connectionName": "Test MySQL Connection",
                "databaseName": "test_database",
                "tableName": "orders",
                "tableAliases": ["order", "purchase"],
                "columns": [
                    {
                        "name": "order_id",
                        "aliases": ["id"]
                    },
                    {
                        "name": "user_id",
                        "aliases": ["customer_id"]
                    },
                    {
                        "name": "total",
                        "aliases": ["amount", "order_total"]
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/database/schema-configuration",
            json=test_config
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"\nResponse:")
            print(f"  - Success: {data.get('success')}")
            print(f"  - Config ID: {data.get('config_id')}")
            print(f"  - Message: {data.get('message')}")
            print(f"  - File Path: {data.get('file_path')}")
            
            if data.get('summary'):
                summary = data['summary']
                print(f"\n📊 Summary:")
                print(f"  - Total Tables: {summary.get('total_tables')}")
                print(f"  - Total Columns: {summary.get('total_columns')}")
                print(f"  - Databases: {', '.join(summary.get('databases', []))}")
                print(f"  - Connections: {', '.join(summary.get('connections', []))}")
            
            return data
        else:
            print(f"\n❌ FAILED")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("SCHEMA CONFIGURATION API TESTS")
    print("="*80)
    print(f"Testing API at: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Get existing configurations
    get_result = test_get_schema_configurations()
    
    # Test 2: Save a new configuration
    save_result = test_save_schema_configuration()
    
    # Test 3: Get configurations again to verify the new one was saved
    if save_result:
        print("\n" + "="*80)
        print("TEST 3: Verify new configuration was saved")
        print("="*80)
        get_result_after = test_get_schema_configurations()
        
        if get_result and get_result_after:
            count_before = get_result.get('count', 0)
            count_after = get_result_after.get('count', 0)
            
            if count_after > count_before:
                print(f"\n✅ Verification successful! Configuration count increased from {count_before} to {count_after}")
            else:
                print(f"\n⚠️  Warning: Configuration count did not increase (Before: {count_before}, After: {count_after})")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

