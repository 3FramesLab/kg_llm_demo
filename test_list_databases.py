"""Test listing databases."""
import requests
import json

# First add a connection
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

print("Adding connection...")
response = requests.post("http://localhost:8000/v1/database/connections", json=payload)
if response.status_code == 200:
    result = response.json()
    connection_id = result['connection']['id']
    print(f"✓ Connection added: {connection_id}")
    
    print("\nListing databases...")
    response = requests.get(f"http://localhost:8000/v1/database/connections/{connection_id}/databases")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Clean up
    requests.delete(f"http://localhost:8000/v1/database/connections/{connection_id}")
else:
    print(f"✗ Failed to add connection: {response.text}")

