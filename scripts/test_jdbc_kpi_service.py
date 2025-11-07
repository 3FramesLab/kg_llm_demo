#!/usr/bin/env python3
"""Test JDBC-based KPI service"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_jdbc_kpi_service():
    """Test JDBC-based KPI service."""
    print("🧪 Testing JDBC-based KPI Service...")
    
    try:
        # Test jaydebeapi import
        try:
            import jaydebeapi
            print("✅ jaydebeapi module available")
        except ImportError:
            print("❌ jaydebeapi module not available")
            return False
        
        # Test service import
        try:
            from kg_builder.services.landing_kpi_service_jdbc import LandingKPIServiceJDBC
            print("✅ LandingKPIServiceJDBC imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import LandingKPIServiceJDBC: {e}")
            return False
        
        # Test service creation
        try:
            service = LandingKPIServiceJDBC()
            print("✅ Service instance created")
        except Exception as e:
            print(f"❌ Failed to create service instance: {e}")
            return False
        
        # Test connection
        try:
            connection_ok = service.test_connection()
            if connection_ok:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
                return False
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
        
        # Test getting KPIs
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
    print("🔍 JDBC KPI SERVICE TEST")
    print("="*60)
    
    success = test_jdbc_kpi_service()
    
    print("\n" + "="*60)
    if success:
        print("🎉 JDBC KPI service test PASSED!")
        print("✅ The enhanced KPI API should work now")
    else:
        print("❌ JDBC KPI service test FAILED!")
        print("🔧 Check JDBC drivers and database connectivity")
    print("="*60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
