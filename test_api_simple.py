"""Simple API test to check JDBC initialization."""
import requests
import json

# Test connection payload
payload = {
    "name": "Test MySQL",
    "type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "demo_server_db",
    "username": "root",
    "password": "3frames",
    "service_name": ""
}

print("Testing database connection API...")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(
        "http://localhost:8000/v1/database/test-connection",
        json=payload,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ SUCCESS!")
    else:
        print("\n✗ FAILED")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")

