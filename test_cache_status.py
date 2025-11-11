#!/usr/bin/env python3
"""
Test script to check KPI cache status and database migration.
"""

import sys
import os
import requests
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cache_status():
    """Test the cache status for a specific KPI."""
    
    # Configuration
    BASE_URL = "http://localhost:8000/v1"  # Adjust if different
    KPI_ID = 28  # The KPI you've been testing
    
    print("🔍 Testing KPI Cache Status")
    print("=" * 50)
    
    try:
        # Test 1: Check if debug endpoint exists
        print("1. Testing debug endpoint...")
        debug_url = f"{BASE_URL}/landing-kpi-mssql/kpis/{KPI_ID}/debug-cache"
        
        try:
            response = requests.get(debug_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Debug endpoint working")
                print(f"   Service Type: {data.get('service_type')}")
                
                cache_status = data.get('cache_status', {})
                print(f"   isAccept: {cache_status.get('isAccept')}")
                print(f"   isSQLCached: {cache_status.get('isSQLCached')}")
                print(f"   cached_sql_exists: {cache_status.get('cached_sql_exists')}")
                print(f"   cached_sql_length: {cache_status.get('cached_sql_length')}")
                
                if cache_status.get('cached_sql_preview'):
                    print(f"   cached_sql_preview: {cache_status.get('cached_sql_preview')}")
                
                print(f"   KPI keys: {data.get('all_kpi_keys')}")
                
            else:
                print(f"❌ Debug endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend server")
            print("   Make sure the backend is running on http://localhost:8000")
            return False
        except Exception as e:
            print(f"❌ Debug endpoint error: {e}")
        
        # Test 2: Check regular KPI list
        print("\n2. Testing KPI list endpoint...")
        list_url = f"{BASE_URL}/landing-kpi-mssql/kpis"
        
        try:
            response = requests.get(list_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                kpis = data.get('data', {}).get('kpis', [])
                
                target_kpi = None
                for kpi in kpis:
                    if kpi.get('id') == KPI_ID:
                        target_kpi = kpi
                        break
                
                if target_kpi:
                    print(f"✅ Found KPI {KPI_ID} in list")
                    print(f"   isAccept: {target_kpi.get('isAccept', 'NOT_FOUND')}")
                    print(f"   isSQLCached: {target_kpi.get('isSQLCached', 'NOT_FOUND')}")
                    print(f"   cached_sql: {bool(target_kpi.get('cached_sql'))}")
                else:
                    print(f"❌ KPI {KPI_ID} not found in list")
            else:
                print(f"❌ KPI list failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ KPI list error: {e}")
        
        # Test 3: Try to set cache flags
        print("\n3. Testing cache flag update...")
        cache_url = f"{BASE_URL}/landing-kpi-mssql/kpis/{KPI_ID}/cache-flags"
        
        try:
            # Try to set both flags to true
            payload = {
                "isAccept": True,
                "isSQLCached": True,
                "cached_sql": "SELECT 1 as test_cache"
            }
            
            response = requests.patch(cache_url, json=payload, timeout=10)
            if response.status_code == 200:
                print("✅ Cache flags updated successfully")
                data = response.json()
                kpi_data = data.get('data', {})
                print(f"   Updated isAccept: {kpi_data.get('isAccept')}")
                print(f"   Updated isSQLCached: {kpi_data.get('isSQLCached')}")
            else:
                print(f"❌ Cache update failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Cache update error: {e}")
        
        print("\n" + "=" * 50)
        print("📋 Summary:")
        print("If you see 'NOT_FOUND' or errors above, the database migration hasn't been run.")
        print("If cache flags show as False/True, the migration worked but caching logic needs debugging.")
        print("\n💡 Next Steps:")
        print("1. If migration needed: Run the SQL from quick_migration.sql")
        print("2. Restart backend server after migration")
        print("3. Test cache workflow: Execute → Accept → Cache → Execute again")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_cache_status()
