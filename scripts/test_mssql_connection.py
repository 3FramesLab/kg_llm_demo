#!/usr/bin/env python3
"""Test MS SQL Server connection directly"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_mssql_connection():
    """Test MS SQL Server connection without FastAPI dependencies."""
    print("🧪 Testing MS SQL Server Connection...")
    
    try:
        # Test pyodbc import
        try:
            import pyodbc
            print("✅ pyodbc module available")
        except ImportError:
            print("❌ pyodbc module not available")
            print("   Install with: pip install pyodbc")
            return False
        
        # Test ODBC drivers
        drivers = pyodbc.drivers()
        print(f"📋 Available ODBC drivers: {drivers}")
        
        sql_server_drivers = [d for d in drivers if 'SQL Server' in d]
        if not sql_server_drivers:
            print("❌ No SQL Server ODBC drivers found")
            print("   Install ODBC Driver 17 for SQL Server")
            return False
        
        print(f"✅ SQL Server drivers available: {sql_server_drivers}")
        
        # Try to import the service
        try:
            from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL
            print("✅ LandingKPIServiceMSSQL imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import LandingKPIServiceMSSQL: {e}")
            return False
        
        # Try to create service instance
        try:
            service = LandingKPIServiceMSSQL()
            print("✅ Service instance created")
        except Exception as e:
            print(f"❌ Failed to create service instance: {e}")
            return False
        
        # Try to connect to database
        try:
            conn = service._get_connection()
            print("✅ Database connection successful")
            conn.close()
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("   Check:")
            print("   - MS SQL Server is running")
            print("   - Connection string is correct")
            print("   - Credentials are valid")
            print("   - Network connectivity")
            return False
        
        # Try to get KPIs
        try:
            kpis = service.get_all_kpis(include_inactive=False)
            print(f"✅ Retrieved {len(kpis)} KPIs successfully")
            
            if kpis:
                print("📋 Sample KPIs:")
                for kpi in kpis[:3]:
                    print(f"   - {kpi.get('name')} ({kpi.get('group_name', 'No Group')})")
            else:
                print("📋 No KPIs found (database might be empty)")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to retrieve KPIs: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("="*60)
    print("🔍 MS SQL SERVER CONNECTION TEST")
    print("="*60)
    
    success = test_mssql_connection()
    
    print("\n" + "="*60)
    if success:
        print("🎉 MS SQL Server connection test PASSED!")
        print("✅ The enhanced KPI API should work")
    else:
        print("❌ MS SQL Server connection test FAILED!")
        print("🔧 Fix the issues above before using the enhanced API")
    print("="*60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
