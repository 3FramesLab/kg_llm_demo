#!/usr/bin/env python3
"""Simple JDBC test"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Testing JDBC availability...")

try:
    import jaydebeapi
    print("SUCCESS: jaydebeapi is available")
    
    # Test service import
    from kg_builder.services.landing_kpi_service_jdbc import LandingKPIServiceJDBC
    print("SUCCESS: Service imported")
    
    # Test service creation
    service = LandingKPIServiceJDBC()
    print("SUCCESS: Service created")
    
    # Test connection
    conn = service._get_connection()
    print("SUCCESS: Database connection established")
    
    # Test simple query
    cursor = conn.cursor()
    cursor.execute("SELECT 1 as test")
    result = cursor.fetchone()
    print(f"SUCCESS: Query executed, result: {result}")
    
    cursor.close()
    conn.close()
    
    print("ALL TESTS PASSED - JDBC KPI service should work!")
    
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
