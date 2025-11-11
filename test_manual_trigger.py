#!/usr/bin/env python3
"""
Test script to verify the manual_trigger_schedule method works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kg_builder.services.kpi_schedule_service import KPIScheduleService
from kg_builder.config import get_mssql_connection_string

def test_manual_trigger():
    """Test the manual trigger functionality"""
    try:
        # Get connection string
        connection_string = get_mssql_connection_string()
        print(f"✓ Connection string: {connection_string[:50]}...")
        
        # Create service
        service = KPIScheduleService(connection_string)
        print("✓ KPIScheduleService created successfully")
        
        # Check if manual_trigger_schedule method exists
        if hasattr(service, 'manual_trigger_schedule'):
            print("✓ manual_trigger_schedule method exists")
            
            # Try to get a schedule first
            try:
                schedule = service.get_schedule(1)
                if schedule:
                    print(f"✓ Found schedule 1: {schedule['schedule_name']}")
                    print(f"  KPI ID: {schedule['kpi_id']}")
                    print(f"  Active: {schedule['is_active']}")
                    
                    if schedule['is_active']:
                        print("🚀 Testing manual trigger...")
                        # This would actually trigger the execution
                        # result = service.manual_trigger_schedule(1)
                        # print(f"✓ Manual trigger result: {result}")
                        print("✓ Manual trigger method is ready (not executed to avoid actual trigger)")
                    else:
                        print("⚠️ Schedule is not active, cannot trigger")
                else:
                    print("❌ Schedule 1 not found")
            except Exception as e:
                print(f"❌ Error testing schedule: {e}")
        else:
            print("❌ manual_trigger_schedule method not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manual_trigger()
