"""
Database Connection Diagnostic Tool
Helps identify the correct database type and connection parameters.
"""
import socket
import sys


def check_port(host, port):
    """Check if a port is open on the host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error checking port: {e}")
        return False


def diagnose_connection(host, port):
    """Diagnose database connection issues."""
    print("=" * 80)
    print("DATABASE CONNECTION DIAGNOSTIC TOOL")
    print("=" * 80)
    print()
    
    print(f"Testing connection to: {host}:{port}")
    print()
    
    # Check if port is open
    print(f"[1/3] Checking if port {port} is open...")
    if check_port(host, port):
        print(f"✓ Port {port} is OPEN on {host}")
    else:
        print(f"✗ Port {port} is CLOSED or unreachable on {host}")
        print()
        print("Possible issues:")
        print("  - Database server is not running")
        print("  - Firewall is blocking the connection")
        print("  - Wrong host or port number")
        print()
        return False
    
    print()
    
    # Identify likely database type based on port
    print(f"[2/3] Identifying database type based on port {port}...")
    
    common_ports = {
        3306: "MySQL/MariaDB",
        5432: "PostgreSQL",
        1433: "Microsoft SQL Server",
        1521: "Oracle",
        27017: "MongoDB",
        5984: "CouchDB",
        9042: "Cassandra",
        7474: "Neo4j"
    }
    
    if port in common_ports:
        db_type = common_ports[port]
        print(f"✓ Port {port} is typically used by: {db_type}")
    else:
        print(f"⚠ Port {port} is not a standard database port")
        db_type = "Unknown"
    
    print()
    
    # Provide connection recommendations
    print(f"[3/3] Connection recommendations:")
    print()
    
    if port == 1433:
        print("This appears to be SQL Server. Use these settings:")
        print("  - Type: sqlserver")
        print("  - Port: 1433")
        print("  - Database: NewDQ (or your database name)")
        print()
        print("Example connection JSON:")
        print("""
{
    "name": "DQ SQL Server",
    "type": "sqlserver",
    "host": "localhost",
    "port": 1433,
    "database": "NewDQ",
    "username": "sa",
    "password": "your_password"
}
        """)
    elif port == 3306:
        print("This appears to be MySQL. Use these settings:")
        print("  - Type: mysql")
        print("  - Port: 3306")
        print("  - Database: NewDQ (or your database name)")
        print()
        print("Example connection JSON:")
        print("""
{
    "name": "DQ MySQL",
    "type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "NewDQ",
    "username": "root",
    "password": "your_password"
}
        """)
    elif port == 5432:
        print("This appears to be PostgreSQL. Use these settings:")
        print("  - Type: postgresql")
        print("  - Port: 5432")
        print("  - Database: NewDQ (or your database name)")
        print()
        print("Example connection JSON:")
        print("""
{
    "name": "DQ PostgreSQL",
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "NewDQ",
    "username": "postgres",
    "password": "your_password"
}
        """)
    elif port == 1521:
        print("This appears to be Oracle. Use these settings:")
        print("  - Type: oracle")
        print("  - Port: 1521")
        print("  - Database: ORCL (or your SID)")
        print("  - Service Name: (optional, e.g., ORCLPDB)")
        print()
        print("Example connection JSON:")
        print("""
{
    "name": "DQ Oracle",
    "type": "oracle",
    "host": "localhost",
    "port": 1521,
    "database": "ORCL",
    "username": "system",
    "password": "your_password",
    "service_name": "ORCLPDB"
}
        """)
    
    print()
    print("=" * 80)
    return True


def main():
    """Main function."""
    if len(sys.argv) > 2:
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        print("Usage: python diagnose_database.py <host> <port>")
        print()
        print("Based on your error, testing with your parameters:")
        host = "localhost"
        port = 1433
    
    diagnose_connection(host, port)


if __name__ == "__main__":
    main()

