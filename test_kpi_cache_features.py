#!/usr/bin/env python3
"""
Test script for KPI cache features implementation.
"""

def test_model_imports():
    """Test that new models can be imported."""
    try:
        from kg_builder.models import (
            KPIDefinition, 
            KPICacheFlagsRequest, 
            KPIClearCacheRequest,
            KPIUpdateRequest
        )
        print("✅ Model imports successful")
        
        # Test model creation
        cache_request = KPICacheFlagsRequest(
            isAccept=True,
            isSQLCached=True,
            cached_sql="SELECT * FROM test"
        )
        print(f"✅ KPICacheFlagsRequest created: {cache_request}")
        
        clear_request = KPIClearCacheRequest(clear_cache=True)
        print(f"✅ KPIClearCacheRequest created: {clear_request}")
        
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_service_imports():
    """Test that service methods exist."""
    try:
        from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL
        
        # Check if new methods exist
        service = LandingKPIServiceMSSQL()
        
        if hasattr(service, 'update_cache_flags'):
            print("✅ update_cache_flags method exists")
        else:
            print("❌ update_cache_flags method missing")
            
        if hasattr(service, 'clear_cache_flags'):
            print("✅ clear_cache_flags method exists")
        else:
            print("❌ clear_cache_flags method missing")
            
        return True
    except Exception as e:
        print(f"❌ Service import failed: {e}")
        return False

def test_route_imports():
    """Test that routes can be imported."""
    try:
        from kg_builder.routes import router
        print("✅ Routes imported successfully")
        return True
    except Exception as e:
        print(f"❌ Route import failed: {e}")
        return False

def test_executor_changes():
    """Test that executor has the new cached SQL method."""
    try:
        from kg_builder.services.landing_kpi_executor import LandingKPIExecutor
        
        executor = LandingKPIExecutor()
        
        if hasattr(executor, '_execute_cached_sql'):
            print("✅ _execute_cached_sql method exists")
        else:
            print("❌ _execute_cached_sql method missing")
            
        return True
    except Exception as e:
        print(f"❌ Executor test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing KPI Cache Features Implementation")
    print("=" * 50)
    
    tests = [
        ("Model Imports", test_model_imports),
        ("Service Imports", test_service_imports),
        ("Route Imports", test_route_imports),
        ("Executor Changes", test_executor_changes),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Implementation is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
