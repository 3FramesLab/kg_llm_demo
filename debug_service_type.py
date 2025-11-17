#!/usr/bin/env python3
"""
Debug script to check which service is actually being used.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_service_type():
    """Test which service is actually being returned."""
    print("🔍 SERVICE TYPE DEBUG")
    print("=" * 50)
    
    try:
        # Test the route function
        from kg_builder.routes import get_kpi_analytics_service
        
        service = get_kpi_analytics_service()
        print(f"✅ Service type: {type(service).__name__}")
        print(f"✅ Service module: {type(service).__module__}")
        print(f"✅ Service class: {service.__class__}")
        
        # Check if it has the expected methods
        methods = ['execute_kpi', 'create_execution_record', 'get_kpi']
        for method in methods:
            has_method = hasattr(service, method)
            print(f"   {method}: {'✅' if has_method else '❌'}")
        
        # Check if it's the JDBC service
        is_jdbc = 'jdbc' in type(service).__module__.lower()
        is_mssql = 'mssql' in type(service).__module__.lower()
        
        print(f"\n📊 Service Analysis:")
        print(f"   Is JDBC Service: {'✅' if is_jdbc else '❌'}")
        print(f"   Is MSSQL Service: {'✅' if is_mssql else '❌'}")
        
        # Test database connection capability
        print(f"\n🔌 Connection Test:")
        try:
            # Try to get a connection (this will fail if jaydebeapi is missing)
            conn = service._get_connection()
            print("✅ Database connection successful")
            conn.close()
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # Check if it's the jaydebeapi error
            if 'jaydebeapi' in str(e).lower():
                print("🎯 ROOT CAUSE: jaydebeapi dependency is missing!")
                print("   This explains why KPI execution returns null values.")
                print("   The JDBC service can't connect to the database.")
        
        # Test KPI retrieval
        print(f"\n📋 KPI Retrieval Test:")
        try:
            kpi = service.get_kpi(28)
            if kpi:
                print(f"✅ KPI 28 found: {kpi.get('name', 'Unknown')}")
            else:
                print("❌ KPI 28 not found")
        except Exception as e:
            print(f"❌ KPI retrieval failed: {e}")
            print(f"   Error type: {type(e).__name__}")
        
        return service
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return None

def test_execute_kpi_method():
    """Test the execute_kpi method directly."""
    print("\n🚀 EXECUTE_KPI METHOD TEST")
    print("=" * 50)
    
    try:
        service = test_service_type()
        if not service:
            print("❌ Cannot test execute_kpi - service not available")
            return
        
        # Test parameters
        test_params = {
            'kg_name': 'New_KG_100',
            'schemas': ['newdqnov7'],
            'select_schema': 'newdqnov7',
            'use_llm': True,
            'limit': 10,
            'db_type': 'sqlserver'
        }
        
        print(f"📤 Testing with params: {test_params}")
        
        # This should fail with the jaydebeapi error
        result = service.execute_kpi(28, test_params)
        
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            # Check key fields
            key_fields = ['success', 'execution_id', 'execution_status', 'error_message']
            for field in key_fields:
                value = result.get(field, 'NOT_FOUND')
                print(f"   {field}: {value}")
        
    except Exception as e:
        print(f"❌ execute_kpi test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Check if this is the expected jaydebeapi error
        if 'jaydebeapi' in str(e).lower():
            print("🎯 CONFIRMED: jaydebeapi dependency is missing!")
            print("   This is why the KPI execution is failing.")
        else:
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🔍 KPI SERVICE DEBUG SCRIPT")
    print("=" * 60)
    print("This script identifies which service is being used")
    print("and why KPI execution is returning null values.")
    print()
    
    test_service_type()
    test_execute_kpi_method()
    
    print("\n" + "=" * 60)
    print("🎯 EXPECTED FINDINGS:")
    print("1. Service type should be LandingKPIServiceJDBC")
    print("2. Database connection should fail with 'jaydebeapi not available'")
    print("3. This explains why execute_kpi returns null values")
    print("=" * 60)
