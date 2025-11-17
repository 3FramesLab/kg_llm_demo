#!/usr/bin/env python3
# Simple test script to verify installation
try:
    import pyodbc
    print("✅ pyodbc imported successfully")
    drivers = pyodbc.drivers()
    print(f"   Available drivers: {len(drivers)}")
    sql_drivers = [d for d in drivers if 'SQL Server' in d]
    if sql_drivers:
        print(f"   SQL Server drivers: {sql_drivers}")
    else:
        print("   ⚠️  No SQL Server drivers found")
except Exception as e:
    print(f"❌ pyodbc test failed: {e}")

try:
    from openai import OpenAI
    print("✅ openai imported successfully")
    # Test client creation (without API key)
    try:
        client = OpenAI(api_key="test")
        print("   OpenAI client creation - OK")
    except Exception as e:
        print(f"   OpenAI client test: {e}")
except Exception as e:
    print(f"❌ openai test failed: {e}")

print("\n🎉 Installation test completed!")
