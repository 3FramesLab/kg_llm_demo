#!/usr/bin/env python3
"""
Installation script for SQL Preview dependencies
This script helps install the required dependencies for the SQL preview scripts.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def check_python_version():
    """Check Python version."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - UNSUPPORTED")
        print("   Python 3.7+ is required")
        return False

def install_python_packages():
    """Install required Python packages."""
    packages = [
        ("openai", "OpenAI API client"),
        ("pyodbc", "Database connectivity")
    ]
    
    success = True
    for package, description in packages:
        if not run_command(f"{sys.executable} -m pip install {package}", f"Installing {package} ({description})"):
            success = False
    
    return success

def check_odbc_driver():
    """Check if ODBC driver is available."""
    print("🔌 Checking ODBC Driver...")
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        sql_server_drivers = [d for d in drivers if 'SQL Server' in d]
        
        if sql_server_drivers:
            print(f"✅ ODBC drivers found: {', '.join(sql_server_drivers)}")
            return True
        else:
            print("❌ No SQL Server ODBC drivers found")
            print("   Please install 'ODBC Driver 17 for SQL Server'")
            print("   Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
            return False
    except ImportError:
        print("❌ pyodbc not available - cannot check ODBC drivers")
        return False
    except Exception as e:
        print(f"❌ Error checking ODBC drivers: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported."""
    print("📦 Testing imports...")
    
    modules = [
        ("openai", "OpenAI API client"),
        ("pyodbc", "Database connectivity")
    ]
    
    success = True
    for module, description in modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK ({description})")
        except ImportError as e:
            print(f"❌ {module} - FAILED ({description}): {e}")
            success = False
    
    return success

def create_test_script():
    """Create a simple test script."""
    test_script = """#!/usr/bin/env python3
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

print("\\n🎉 Installation test completed!")
"""
    
    with open("test_installation.py", "w") as f:
        f.write(test_script)
    
    print("📝 Created test_installation.py")

def main():
    """Main installation function."""
    print("="*60)
    print("SQL PREVIEW DEPENDENCIES INSTALLER")
    print("="*60)
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Python Packages", install_python_packages),
        ("Test Imports", test_imports),
        ("Check ODBC Driver", check_odbc_driver),
        ("Create Test Script", lambda: (create_test_script(), True)[1])
    ]
    
    results = []
    for step_name, step_func in steps:
        print(f"\n--- {step_name} ---")
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
            results.append((step_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("INSTALLATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for step_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{status}: {step_name}")
    
    print(f"\nSteps completed: {passed}/{len(results)}")
    
    if failed == 0:
        print("\n🎉 Installation completed successfully!")
        print("\nNext steps:")
        print("1. Run: python test_installation.py")
        print("2. Update configuration in sql_preview_simple.py")
        print("3. Run: python sql_preview_simple.py")
    else:
        print(f"\n❌ {failed} step(s) failed")
        print("\nPlease address the failed steps above before proceeding.")
        
        if any("ODBC" in step for step, result in results if not result):
            print("\n💡 ODBC Driver Installation:")
            print("   Windows: Download from Microsoft's official page")
            print("   Linux: sudo apt-get install msodbcsql17")
            print("   macOS: brew install msodbcsql17")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
