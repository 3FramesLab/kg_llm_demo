#!/usr/bin/env python3
"""
Debug script to test KPI execution locally and understand why it's not working.
"""

import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_service_import():
    """Test importing the services."""
    print("🧪 Testing Service Imports")
    print("=" * 50)
    
    try:
        from kg_builder.services.landing_kpi_service_jdbc import LandingKPIServiceJDBC
        print("✅ LandingKPIServiceJDBC imported successfully")
        
        from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL
        print("✅ LandingKPIServiceMSSQL imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_service_method():
    """Test the execute_kpi method directly."""
    print("\n🔧 Testing Service Method")
    print("=" * 50)
    
    try:
        from kg_builder.services.landing_kpi_service_jdbc import LandingKPIServiceJDBC
        
        service = LandingKPIServiceJDBC()
        print("✅ Service instance created")
        
        # Check if execute_kpi method exists
        if hasattr(service, 'execute_kpi'):
            print("✅ execute_kpi method exists")
            
            # Check method signature
            import inspect
            sig = inspect.signature(service.execute_kpi)
            print(f"✅ Method signature: {sig}")
            
            return True
        else:
            print("❌ execute_kpi method not found")
            return False
            
    except Exception as e:
        print(f"❌ Service method test failed: {e}")
        return False

def test_kpi_retrieval():
    """Test retrieving KPI 28."""
    print("\n📋 Testing KPI Retrieval")
    print("=" * 50)
    
    try:
        from kg_builder.services.landing_kpi_service_jdbc import LandingKPIServiceJDBC
        
        service = LandingKPIServiceJDBC()
        kpi = service.get_kpi(28)
        
        if kpi:
            print("✅ KPI 28 found")
            print(f"   Name: {kpi.get('name', 'Unknown')}")
            print(f"   Description: {kpi.get('description', 'No description')}")
            print(f"   NL Definition: {kpi.get('nl_definition', 'No NL definition')}")
            print(f"   Active: {kpi.get('is_active', 'Unknown')}")
            return True
        else:
            print("❌ KPI 28 not found")
            return False
            
    except Exception as e:
        print(f"❌ KPI retrieval failed: {e}")
        return False

def test_route_function():
    """Test the route function directly."""
    print("\n🌐 Testing Route Function")
    print("=" * 50)
    
    try:
        # Import the route function
        from kg_builder.routes import get_kpi_analytics_service
        
        service = get_kpi_analytics_service()
        print(f"✅ Service from route: {type(service).__name__}")
        
        # Test with minimal params
        test_params = {
            'kg_name': 'New_KG_100',
            'schemas': ['newdqnov7'],
            'definitions': ['test query'],
            'use_llm': True,
            'limit': 10
        }
        
        print(f"📤 Test params: {test_params}")
        
        # This might fail, but we want to see what happens
        try:
            result = service.execute_kpi(28, test_params)
            print(f"✅ Service call succeeded")
            print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            print(f"📊 Success: {result.get('success', 'Not found')}")
            print(f"📊 Execution ID: {result.get('execution_id', 'Not found')}")
            print(f"📊 Execution Status: {result.get('execution_status', 'Not found')}")
            return True
        except Exception as exec_error:
            print(f"⚠️ Service call failed: {exec_error}")
            print("   This might be expected due to missing dependencies")
            return False
            
    except Exception as e:
        print(f"❌ Route function test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 KPI EXECUTION DEBUG SCRIPT")
    print("=" * 60)
    print("This script tests the KPI execution components locally")
    print("to understand why the API is returning null values.")
    print()
    
    tests = [
        ("Service Import", test_service_import),
        ("Service Method", test_service_method),
        ("KPI Retrieval", test_kpi_retrieval),
        ("Route Function", test_route_function)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The issue might be elsewhere.")
    else:
        print("🔧 Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
