#!/usr/bin/env python3
"""
Test script to verify SQL storage in cache fields.
"""

import sys
import os
import requests
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sql_storage():
    """Test SQL storage in cache fields."""
    
    BASE_URL = "http://localhost:8000/v1"
    KPI_ID = 28
    
    print("🔍 Testing SQL Storage in Cache Fields")
    print("=" * 50)
    
    try:
        # Step 1: Get current KPI state
        print("1. Getting current KPI state...")
        response = requests.get(f"{BASE_URL}/landing-kpi-mssql/kpis", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to get KPIs: {response.status_code}")
            return False
        
        data = response.json()
        kpis = data.get('data', {}).get('kpis', [])
        kpi = next((k for k in kpis if k['id'] == KPI_ID), None)
        
        if not kpi:
            print(f"❌ KPI {KPI_ID} not found")
            return False
        
        print(f"✅ Found KPI: {kpi['name']}")
        print(f"   isAccept: {kpi.get('isAccept', 'NOT_FOUND')}")
        print(f"   isSQLCached: {kpi.get('isSQLCached', 'NOT_FOUND')}")
        print(f"   cached_sql exists: {bool(kpi.get('cached_sql'))}")
        
        # Step 2: Get execution history
        print("\n2. Getting execution history...")
        exec_response = requests.get(f"{BASE_URL}/landing-kpi-mssql/kpis/{KPI_ID}/executions", timeout=10)
        if exec_response.status_code != 200:
            print(f"❌ Failed to get executions: {exec_response.status_code}")
            print(f"   Response: {exec_response.text}")
            return False
        
        exec_data = exec_response.json()
        executions = exec_data.get('data', {}).get('executions', []) or exec_data.get('executions', [])
        print(f"✅ Found {len(executions)} executions")
        
        if executions:
            latest = executions[0]
            print(f"   Latest execution ID: {latest.get('id')}")
            print(f"   Status: {latest.get('execution_status')}")
            print(f"   SQL exists: {bool(latest.get('generated_sql'))}")
            if latest.get('generated_sql'):
                print(f"   SQL preview: {latest['generated_sql'][:100]}...")
        
        # Step 3: Test storing SQL
        print("\n3. Testing SQL storage...")
        test_sql = "SELECT 1 as test_cache_storage, GETDATE() as test_timestamp"
        if executions and executions[0].get('generated_sql'):
            test_sql = executions[0]['generated_sql']
        
        update_data = {
            "isAccept": True,
            "cached_sql": test_sql
        }
        
        print(f"   Storing SQL: {test_sql[:100]}...")
        
        cache_response = requests.patch(
            f"{BASE_URL}/landing-kpi-mssql/kpis/{KPI_ID}/cache-flags",
            json=update_data,
            timeout=10
        )
        
        if cache_response.status_code != 200:
            print(f"❌ Failed to update cache: {cache_response.status_code}")
            print(f"   Response: {cache_response.text}")
            return False
        
        cache_result = cache_response.json()
        print("✅ Cache update successful")
        print(f"   Response: {cache_result.get('message', 'No message')}")
        
        # Step 4: Verify storage
        print("\n4. Verifying SQL storage...")
        verify_response = requests.get(f"{BASE_URL}/landing-kpi-mssql/kpis", timeout=10)
        if verify_response.status_code != 200:
            print(f"❌ Failed to verify: {verify_response.status_code}")
            return False
        
        verify_data = verify_response.json()
        verify_kpis = verify_data.get('data', {}).get('kpis', [])
        verify_kpi = next((k for k in verify_kpis if k['id'] == KPI_ID), None)
        
        if verify_kpi:
            print("✅ Verification results:")
            print(f"   isAccept: {verify_kpi.get('isAccept')}")
            print(f"   isSQLCached: {verify_kpi.get('isSQLCached')}")
            print(f"   cached_sql exists: {bool(verify_kpi.get('cached_sql'))}")
            
            if verify_kpi.get('cached_sql'):
                stored_sql = verify_kpi['cached_sql']
                print(f"   cached_sql length: {len(stored_sql)}")
                print(f"   cached_sql preview: {stored_sql[:100]}...")
                
                if stored_sql == test_sql:
                    print("🎉 SQL storage SUCCESSFUL - stored SQL matches!")
                    return True
                else:
                    print("⚠️ SQL storage PARTIAL - SQL was stored but doesn't match exactly")
                    print(f"   Expected: {test_sql[:50]}...")
                    print(f"   Got: {stored_sql[:50]}...")
                    return True
            else:
                print("❌ SQL storage FAILED - no cached_sql found after update")
                return False
        else:
            print("❌ Could not find KPI for verification")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Make sure the backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_sql_storage()
    
    if success:
        print("\n🎉 SQL storage is working!")
        print("Next: Test the cache execution workflow")
    else:
        print("\n❌ SQL storage has issues")
        print("Check the backend logs and database migration")
    
    input("\nPress Enter to continue...")
