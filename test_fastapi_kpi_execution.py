#!/usr/bin/env python3
"""
Test script to verify the FastAPI KPI execution fix.

This script tests the fixed execute_kpi method to ensure it now properly
executes KPI queries instead of just creating pending records.
"""

import requests
import json
import time
from typing import Dict, Any


def test_kpi_execution(api_base: str = "http://localhost:8000", kpi_id: int = 28):
    """Test the fixed KPI execution endpoint."""
    
    print("🧪 Testing Fixed FastAPI KPI Execution")
    print("=" * 60)
    print(f"API Base: {api_base}")
    print(f"KPI ID: {kpi_id}")
    print()
    
    # Test payload matching the original request
    test_payload = {
        "kg_name": "New_KG_100",
        "schemas": ["newdqnov7"],
        "select_schema": "newdqnov7",  # Direct schema field
        "definitions": ["get products from gpu product master and hana master where marketing code is missing in both"],
        "use_llm": True,
        "min_confidence": 0.8,
        "limit": 1000,
        "db_type": "sqlserver"
    }
    
    print("📤 Request Payload:")
    print(json.dumps(test_payload, indent=2))
    print()
    
    try:
        # Make the API request
        url = f"{api_base}/v1/landing-kpi-mssql/kpis/{kpi_id}/execute"
        print(f"🌐 POST {url}")
        
        start_time = time.time()
        response = requests.post(url, json=test_payload, timeout=60)
        request_time = (time.time() - start_time) * 1000
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"⏱️ Request Time: {request_time:.2f}ms")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("📊 Response Analysis:")
            print("-" * 40)
            
            # Check top-level response
            success = result.get('success', False)
            storage_type = result.get('storage_type', 'unknown')
            data = result.get('data', {})
            
            print(f"✅ Success: {success}")
            print(f"🗄️ Storage Type: {storage_type}")
            print()
            
            # Analyze the data section
            if data:
                print("📋 Execution Data:")
                print("-" * 20)
                
                # Key fields to check
                key_fields = [
                    'execution_id', 'kpi_id', 'kpi_name', 'execution_status',
                    'number_of_records', 'execution_time_ms', 'generated_sql',
                    'enhanced_sql', 'confidence_score', 'error_message'
                ]
                
                for field in key_fields:
                    value = data.get(field)
                    if value is not None:
                        if field == 'generated_sql' and value:
                            print(f"  {field}: [SQL Present - {len(value)} chars]")
                        elif field == 'enhanced_sql' and value:
                            print(f"  {field}: [Enhanced SQL Present - {len(value)} chars]")
                        elif isinstance(value, str) and len(value) > 50:
                            print(f"  {field}: {value[:50]}...")
                        else:
                            print(f"  {field}: {value}")
                    else:
                        print(f"  {field}: NULL")
                
                print()
                
                # Check if execution was successful
                execution_status = data.get('execution_status')
                execution_id = data.get('execution_id')
                generated_sql = data.get('generated_sql')
                
                print("🔍 Fix Verification:")
                print("-" * 20)
                
                if execution_id is not None:
                    print("✅ FIXED: execution_id is no longer null")
                else:
                    print("❌ ISSUE: execution_id is still null")
                
                if execution_status and execution_status != 'pending':
                    print(f"✅ FIXED: execution_status is '{execution_status}' (not pending)")
                else:
                    print(f"❌ ISSUE: execution_status is '{execution_status}' (still pending)")
                
                if generated_sql:
                    print("✅ FIXED: generated_sql is present")
                else:
                    print("❌ ISSUE: generated_sql is still null")
                
                # Check data array
                result_data = data.get('data', [])
                if isinstance(result_data, list):
                    print(f"📊 Result Data: {len(result_data)} records")
                else:
                    print("📊 Result Data: Not an array")
                
            else:
                print("❌ No data section in response")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Expected vs Actual:")
    print("Expected: execution_id with actual number, execution_status='success', generated_sql present")
    print("Previous: execution_id=null, execution_status='pending', generated_sql=null")
    print("=" * 60)


def main():
    """Run the test."""
    print("FASTAPI KPI EXECUTION FIX VERIFICATION")
    print("=" * 60)
    print("This script tests the fixed execute_kpi method to ensure")
    print("it now properly executes KPI queries instead of just")
    print("creating pending records.")
    print()
    
    # Test with the same KPI ID from the original issue
    test_kpi_execution(kpi_id=28)
    
    print("\n🎉 TEST COMPLETED!")
    print("Check the results above to verify the fix is working.")


if __name__ == "__main__":
    main()
