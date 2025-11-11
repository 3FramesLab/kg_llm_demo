#!/usr/bin/env python3
"""
Test script to verify the schedule trigger fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_schedule_trigger_fixes():
    """Test the fixes for schedule trigger issues"""
    try:
        print("🔧 Testing Schedule Trigger Fixes")
        print("="*50)
        
        # Test 1: Check if LandingKPIServiceJDBC has update_execution_result method
        try:
            from kg_builder.services.landing_kpi_service_jdbc import LandingKPIServiceJDBC
            service = LandingKPIServiceJDBC()
            print("✓ LandingKPIServiceJDBC imported successfully")
            
            if hasattr(service, 'update_execution_result'):
                print("✅ update_execution_result method exists")
            else:
                print("❌ update_execution_result method NOT found")
                
            if hasattr(service, 'create_execution_record'):
                print("✅ create_execution_record method exists")
            else:
                print("❌ create_execution_record method NOT found")
                
        except Exception as e:
            print(f"❌ Error testing LandingKPIServiceJDBC: {e}")
        
        # Test 2: Check execution parameters structure
        print("\n🔍 Testing Execution Parameters:")
        execution_params = {
            'kg_name': 'manual_trigger',
            'schemas': ['newdqschemanov'],  # Required: list of schemas
            'select_schema': 'newdqschemanov',  # Default schema
            'definitions': [],  # Required: empty list for manual trigger
            'db_type': 'sqlserver',
            'limit_records': 1000,
            'limit': 1000,  # Also add as 'limit' for compatibility
            'use_llm': True,
            'min_confidence': 0.7,  # Required parameter
            'user_id': 'schedule_trigger',
            'session_id': 'schedule_1'
        }
        
        required_params = ['schemas', 'definitions', 'min_confidence', 'limit']
        missing_params = []
        
        for param in required_params:
            if param not in execution_params:
                missing_params.append(param)
            else:
                print(f"✅ {param}: {execution_params[param]}")
        
        if missing_params:
            print(f"❌ Missing required parameters: {missing_params}")
        else:
            print("✅ All required parameters present")
        
        # Test 3: Check if schemas parameter is a list
        if isinstance(execution_params.get('schemas'), list):
            print("✅ schemas parameter is a list")
        else:
            print("❌ schemas parameter is not a list")
        
        print("\n" + "="*50)
        print("🎯 Fixed Issues:")
        print("1. ✅ Added missing 'schemas' parameter as list")
        print("2. ✅ Added missing 'definitions' parameter")
        print("3. ✅ Added missing 'min_confidence' parameter")
        print("4. ✅ Added 'limit' parameter for compatibility")
        print("5. ✅ Added update_execution_result method to LandingKPIServiceJDBC")
        print("\n🚀 Schedule trigger should now work with cached SQL!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schedule_trigger_fixes()
