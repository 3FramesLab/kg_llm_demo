"""Test SQL Server connection with improved error messages."""
import requests
import json

BASE_URL = "http://localhost:8000/v1"

def test_connection(payload, description):
    """Test database connection."""
    print("\n" + "=" * 80)
    print(f"TEST: {description}")
    print("=" * 80)
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/database/test-connection",
            json=payload,
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✓ SUCCESS!")
            return True
        else:
            print("\n✗ FAILED")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

# Test 1: SQL Server on port 1433 (will fail with helpful message)
test_connection({
    "name": "Test_SQL Server Port 1433",
    "type": "sqlserver",
    "host": "localhost",
    "port": "1433",
    "database": "NewDQ",
    "username": "root",
    "password": "3frames",
    "service_name": ""
}, "SQL Server on Port 1433 (Expected to fail with helpful error)")

# Test 2: SQL Server on port 1434 (detected as listening)
test_connection({
    "name": "Test_SQL Server Port 1434",
    "type": "sqlserver",
    "host": "localhost",
    "port": "1434",
    "database": "NewDQ",
    "username": "sa",
    "password": "your_password",
    "service_name": ""
}, "SQL Server on Port 1434 (Detected as listening)")

# Test 3: MySQL on port 3306 (should work if credentials are correct)
test_connection({
    "name": "Test_MySQL",
    "type": "mysql",
    "host": "localhost",
    "port": "3306",
    "database": "NewDQ",
    "username": "root",
    "password": "3frames",
    "service_name": ""
}, "MySQL on Port 3306")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nBased on diagnostic results:")
print("1. SQL Server is running but NOT listening on port 1433")
print("2. SQL Server IS listening on port 1434 (unusual)")
print("3. MySQL is running on port 3306")
print("\nRecommendations:")
print("• Follow SQL_SERVER_TCP_IP_SETUP.md to enable TCP/IP on port 1433")
print("• Or use port 1434 for SQL Server (if that's your configuration)")
print("• Or use MySQL on port 3306 if NewDQ database is there")
print()

