#!/usr/bin/env python3
"""
MongoDB Connection Test Script
Tests local MongoDB installation and basic operations
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""

    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)

    # Connection string for local MongoDB
    connection_string = "mongodb://localhost:27017/"

    try:
        # Step 1: Connect to MongoDB
        print("\n1. Connecting to MongoDB at localhost:27017...")
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )

        # Step 2: Test connection by running a command
        print("2. Testing connection...")
        client.admin.command('ping')
        print("   [OK] Successfully connected to MongoDB!")

        # Step 3: Get server information
        print("\n3. Server Information:")
        server_info = client.server_info()
        print(f"   MongoDB Version: {server_info['version']}")
        print(f"   Server Type: {server_info.get('storageEngine', {}).get('name', 'N/A')}")

        # Step 4: List existing databases
        print("\n4. Existing Databases:")
        db_list = client.list_database_names()
        for db_name in db_list:
            print(f"   - {db_name}")

        # Step 5: Test CRUD operations
        print("\n5. Testing Basic CRUD Operations...")

        # Use a test database
        test_db = client['test_dq_poc']
        test_collection = test_db['test_collection']

        # Create
        print("   a. Creating a test document...")
        test_doc = {"name": "test", "status": "active", "value": 123}
        insert_result = test_collection.insert_one(test_doc)
        print(f"      [OK] Inserted document with ID: {insert_result.inserted_id}")

        # Read
        print("   b. Reading the test document...")
        found_doc = test_collection.find_one({"name": "test"})
        print(f"      [OK] Found document: {found_doc}")

        # Update
        print("   c. Updating the test document...")
        update_result = test_collection.update_one(
            {"name": "test"},
            {"$set": {"value": 456, "updated": True}}
        )
        print(f"      [OK] Modified {update_result.modified_count} document(s)")

        # Delete
        print("   d. Deleting the test document...")
        delete_result = test_collection.delete_one({"name": "test"})
        print(f"      [OK] Deleted {delete_result.deleted_count} document(s)")

        # Cleanup
        print("\n6. Cleaning up test database...")
        client.drop_database('test_dq_poc')
        print("   [OK] Test database dropped")

        print("\n" + "=" * 60)
        print("[SUCCESS] All MongoDB tests passed successfully!")
        print("=" * 60)

        return True

    except ServerSelectionTimeoutError:
        print("   [ERROR] Could not connect to MongoDB server")
        print("   Make sure MongoDB is running on localhost:27017")
        return False

    except ConnectionFailure:
        print("   [ERROR] Connection to MongoDB failed")
        return False

    except Exception as e:
        print(f"   [ERROR] {type(e).__name__}: {str(e)}")
        return False

    finally:
        try:
            client.close()
            print("\n7. Connection closed")
        except:
            pass

if __name__ == "__main__":
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)
