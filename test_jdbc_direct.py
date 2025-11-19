"""
Direct JDBC Connection Test
Tests JDBC connection manager directly without going through the API.
"""
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_jvm_initialization():
    """Test JVM initialization."""
    print("=" * 80)
    print("TEST 1: JVM Initialization")
    print("=" * 80)
    
    try:
        from kg_builder.services.jdbc_connection_manager import ensure_jvm_initialized
        
        print("\n[1/2] Attempting to initialize JVM...")
        result = ensure_jvm_initialized()
        
        if result:
            print("✓ JVM initialized successfully")
            return True
        else:
            print("✗ JVM initialization failed")
            return False
            
    except Exception as e:
        print(f"✗ Error during JVM initialization: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mysql_connection():
    """Test MySQL connection."""
    print("\n" + "=" * 80)
    print("TEST 2: MySQL Connection")
    print("=" * 80)
    
    try:
        from kg_builder.services.jdbc_connection_manager import get_jdbc_connection
        
        # MySQL connection parameters
        driver_class = "com.mysql.cj.jdbc.Driver"
        jdbc_url = "jdbc:mysql://localhost:3306/NewDQ?useSSL=false&allowPublicKeyRetrieval=true"
        username = "root"
        password = "3frames"
        
        print(f"\n[1/4] Connection parameters:")
        print(f"  Driver: {driver_class}")
        print(f"  URL: {jdbc_url}")
        print(f"  Username: {username}")
        print(f"  Password: {'*' * len(password)}")
        
        print(f"\n[2/4] Attempting to connect to MySQL...")
        conn = get_jdbc_connection(driver_class, jdbc_url, username, password)
        
        if not conn:
            print("✗ Failed to get connection (returned None)")
            return False
        
        print("✓ Connection established successfully")
        
        print(f"\n[3/4] Testing connection with a simple query...")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"✓ Query result: {result}")
        
        print(f"\n[4/4] Closing connection...")
        cursor.close()
        conn.close()
        print("✓ Connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during MySQL connection test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_list_databases():
    """Test listing databases."""
    print("\n" + "=" * 80)
    print("TEST 3: List Databases")
    print("=" * 80)
    
    try:
        from kg_builder.services.jdbc_connection_manager import get_jdbc_connection
        
        driver_class = "com.mysql.cj.jdbc.Driver"
        jdbc_url = "jdbc:mysql://localhost:3306/?useSSL=false&allowPublicKeyRetrieval=true"
        username = "root"
        password = "3frames"
        
        print(f"\n[1/3] Connecting to MySQL server...")
        conn = get_jdbc_connection(driver_class, jdbc_url, username, password)
        
        if not conn:
            print("✗ Failed to get connection")
            return False
        
        print("✓ Connected successfully")
        
        print(f"\n[2/3] Executing SHOW DATABASES...")
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        print(f"✓ Found {len(databases)} databases:")
        for db in databases:
            print(f"  - {db[0]}")
        
        print(f"\n[3/3] Closing connection...")
        cursor.close()
        conn.close()
        print("✓ Connection closed")
        
        return True
        
    except Exception as e:
        print(f"✗ Error listing databases: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("JDBC CONNECTION DIRECT TEST SUITE")
    print("=" * 80)
    print("\nThis script tests JDBC connectivity directly without the API layer.")
    print("It will help identify if the issue is with JVM, JDBC drivers, or connection.")
    
    results = []
    
    # Test 1: JVM Initialization
    results.append(("JVM Initialization", test_jvm_initialization()))
    
    # Test 2: MySQL Connection (only if JVM initialized)
    if results[0][1]:
        results.append(("MySQL Connection", test_mysql_connection()))
        
        # Test 3: List Databases (only if connection works)
        if results[1][1]:
            results.append(("List Databases", test_list_databases()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! JDBC connection is working correctly.")
        print("The issue might be with the API layer or request handling.")
    else:
        print("\n⚠ Some tests failed. Check the error messages above for details.")
    
    print("=" * 80)


if __name__ == "__main__":
    main()

