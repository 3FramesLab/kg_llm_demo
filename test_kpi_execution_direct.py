#!/usr/bin/env python3
"""
Direct test of KPI execution to see what's happening.
"""

import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_direct_execution():
    """Test KPI execution directly."""
    print("🧪 DIRECT KPI EXECUTION TEST")
    print("=" * 60)
    
    try:
        # Import the service
        from kg_builder.services.landing_kpi_service_jdbc import LandingKPIServiceJDBC
        print("✅ Service imported successfully")
        
        # Create service instance
        service = LandingKPIServiceJDBC()
        print("✅ Service instance created")
        
        # Test parameters (matching the original request)
        test_params = {
            'kg_name': 'New_KG_100',  # Valid KG name
            'schemas': ['newdqnov7'],
            'select_schema': 'newdqnov7',  # Direct schema
            'definitions': ['get products from gpu product master and hana master where marketing code is missing in both'],
            'use_llm': True,
            'min_confidence': 0.8,
            'limit': 1000,
            'db_type': 'sqlserver'
        }
        
        print(f"📤 Test Parameters:")
        for key, value in test_params.items():
            print(f"   {key}: {value}")
        print()
        
        # Test KPI retrieval first
        print("📋 Testing KPI retrieval...")
        try:
            kpi = service.get_kpi(28)
            if kpi:
                print(f"✅ KPI 28 found: {kpi.get('name', 'Unknown')}")
            else:
                print("❌ KPI 28 not found")
                return
        except Exception as e:
            print(f"❌ KPI retrieval failed: {e}")
            return
        
        # Test execution
        print("\n🚀 Testing KPI execution...")
        try:
            result = service.execute_kpi(28, test_params)
            print("✅ Execution completed!")
            
            print(f"\n📊 Result Analysis:")
            print(f"   Type: {type(result)}")
            print(f"   Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            if isinstance(result, dict):
                key_fields = [
                    'success', 'execution_id', 'kpi_id', 'execution_status',
                    'record_count', 'generated_sql', 'error_message'
                ]
                
                for field in key_fields:
                    value = result.get(field, 'NOT_FOUND')
                    if field == 'generated_sql' and value and value != 'NOT_FOUND':
                        print(f"   {field}: [SQL Present - {len(str(value))} chars]")
                    else:
                        print(f"   {field}: {value}")
            
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            print(f"   Error type: {type(e)}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

def test_route_function():
    """Test the route function."""
    print("\n🌐 ROUTE FUNCTION TEST")
    print("=" * 60)
    
    try:
        from kg_builder.routes import get_kpi_analytics_service
        
        service = get_kpi_analytics_service()
        print(f"✅ Service from route: {type(service).__name__}")
        
        # Same test parameters
        test_params = {
            'kg_name': 'New_KG_100',
            'schemas': ['newdqnov7'],
            'select_schema': 'newdqnov7',
            'definitions': ['test query'],
            'use_llm': True,
            'limit': 1000,
            'db_type': 'sqlserver'
        }
        
        print("🚀 Testing route service execution...")
        result = service.execute_kpi(28, test_params)
        
        print("✅ Route execution completed!")
        print(f"📊 Result: {result}")
        
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_direct_execution()
    test_route_function()
    
    print("\n" + "=" * 60)
    print("🎯 This test should help identify where the issue is occurring.")
    print("Check the output above for clues about the execution flow.")
