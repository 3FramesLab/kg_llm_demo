"""List all MySQL databases to verify the correct database name."""
import logging

logging.basicConfig(level=logging.INFO)

from kg_builder.services.jdbc_connection_manager import get_jdbc_connection

driver_class = "com.mysql.cj.jdbc.Driver"
jdbc_url = "jdbc:mysql://localhost:3306/?useSSL=false&allowPublicKeyRetrieval=true"
username = "root"
password = "3frames"

print("Connecting to MySQL server...")
conn = get_jdbc_connection(driver_class, jdbc_url, username, password)

if conn:
    print("✓ Connected successfully\n")
    print("Available databases:")
    print("-" * 40)
    
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    
    for db in databases:
        print(f"  - {db[0]}")
    
    cursor.close()
    conn.close()
    
    print("-" * 40)
    print(f"\nTotal: {len(databases)} databases")
    print("\nNote: Database names are case-sensitive in MySQL on some systems.")
    print("Use the exact name shown above in your connection configuration.")
else:
    print("✗ Failed to connect")

