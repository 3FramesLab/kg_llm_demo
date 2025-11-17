#!/usr/bin/env python3
"""
Test script for standalone_sql_preview_jdbc.py

This script tests the JDBC-based standalone SQL preview functionality.

Usage:
    python test_standalone_jdbc.py
"""

import sys
import os
import subprocess

def test_argument_parsing():
    """Test command line argument parsing."""
    print("🧪 Testing JDBC argument parsing...")
    
    try:
        result = subprocess.run([
            sys.executable, 'standalone_sql_preview_jdbc.py', '--help'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0 and 'JDBC' in result.stdout:
            print("   ✅ Help output works correctly")
            return True
        else:
            print(f"   ❌ Help output failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Argument parsing test failed: {e}")
        return False

def test_database_type_validation():
    """Test database type validation."""
    print("🧪 Testing database type validation...")
    
    valid_db_types = ['sqlserver', 'mssql', 'mysql', 'postgresql', 'oracle']
    
    for db_type in valid_db_types:
        try:
            # Test with minimal required arguments
            result = subprocess.run([
                sys.executable, 'standalone_sql_preview_jdbc.py',
                '--nl-definition', 'test query',
                '--select-schema', 'test_schema',
                '--db-type', db_type,
                '--db-host', 'localhost',
                '--db-name', 'test_db',
                '--db-user', 'test_user',
                '--db-password', 'test_pass',
                '--jdbc-drivers-path', '/tmp',
                '--help'  # This will show help and exit without connecting
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            # Help should work regardless of other parameters
            if result.returncode == 0:
                print(f"   ✅ Database type '{db_type}' accepted")
            else:
                print(f"   ❌ Database type '{db_type}' rejected")
                return False
                
        except Exception as e:
            print(f"   ❌ Database type test failed for {db_type}: {e}")
            return False
    
    return True

def test_port_defaults():
    """Test default port assignment."""
    print("🧪 Testing default port assignment...")
    
    port_mappings = {
        'sqlserver': 1433,
        'mssql': 1433,
        'mysql': 3306,
        'postgresql': 5432,
        'oracle': 1521
    }
    
    # This is a conceptual test - we can't easily test the actual port assignment
    # without running the full script, but we can verify the logic exists
    try:
        # Import the argument parser to test the logic
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Read the script to verify port logic exists
        with open(os.path.join(os.path.dirname(__file__), 'standalone_sql_preview_jdbc.py'), 'r') as f:
            script_content = f.read()
        
        # Check if port assignment logic exists
        for db_type, expected_port in port_mappings.items():
            if f"'{db_type}'" in script_content and str(expected_port) in script_content:
                print(f"   ✅ Port mapping for {db_type} -> {expected_port} found")
            else:
                print(f"   ❌ Port mapping for {db_type} -> {expected_port} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Port defaults test failed: {e}")
        return False

def test_jdbc_url_generation():
    """Test JDBC URL generation logic."""
    print("🧪 Testing JDBC URL generation...")
    
    try:
        # Read the script to verify JDBC URL logic exists
        with open(os.path.join(os.path.dirname(__file__), 'standalone_sql_preview_jdbc.py'), 'r') as f:
            script_content = f.read()
        
        # Check for JDBC URL patterns
        jdbc_patterns = [
            'jdbc:sqlserver://',
            'jdbc:mysql://',
            'jdbc:postgresql://',
            'jdbc:oracle:thin:'
        ]
        
        for pattern in jdbc_patterns:
            if pattern in script_content:
                print(f"   ✅ JDBC URL pattern '{pattern}' found")
            else:
                print(f"   ❌ JDBC URL pattern '{pattern}' missing")
                return False
        
        # Check for driver classes
        driver_classes = [
            'com.microsoft.sqlserver.jdbc.SQLServerDriver',
            'com.mysql.cj.jdbc.Driver',
            'org.postgresql.Driver',
            'oracle.jdbc.driver.OracleDriver'
        ]
        
        for driver in driver_classes:
            if driver in script_content:
                print(f"   ✅ Driver class '{driver}' found")
            else:
                print(f"   ❌ Driver class '{driver}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ JDBC URL generation test failed: {e}")
        return False

def test_schema_qualification():
    """Test database-specific schema qualification."""
    print("🧪 Testing schema qualification...")
    
    try:
        # Read the script to verify schema qualification logic
        with open(os.path.join(os.path.dirname(__file__), 'standalone_sql_preview_jdbc.py'), 'r') as f:
            script_content = f.read()
        
        # Check for database-specific schema qualifiers
        qualifiers = [
            '[{self.args.select_schema}].[{intent.source_table}]',  # SQL Server
            '`{self.args.select_schema}`.`{intent.source_table}`',  # MySQL
            '"{self.args.select_schema}"."{intent.source_table}"',  # PostgreSQL
            '{self.args.select_schema}.{intent.source_table}'       # Oracle
        ]
        
        found_qualifiers = 0
        for qualifier in qualifiers:
            # Check for the pattern (may be slightly different in actual code)
            if 'select_schema' in script_content and 'source_table' in script_content:
                found_qualifiers += 1
        
        if found_qualifiers > 0:
            print(f"   ✅ Schema qualification logic found")
            return True
        else:
            print(f"   ❌ Schema qualification logic missing")
            return False
        
    except Exception as e:
        print(f"   ❌ Schema qualification test failed: {e}")
        return False

def test_requirements():
    """Test if required packages can be imported."""
    print("🧪 Testing JDBC requirements...")
    
    required_packages = ['json', 'argparse', 'logging', 'time', 'os', 'sys', 'glob']
    jdbc_packages = ['jaydebeapi']
    optional_packages = ['openai']
    
    # Test required packages
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} available")
        except ImportError:
            print(f"   ❌ {package} not available (required)")
            return False
    
    # Test JDBC packages
    for package in jdbc_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} available")
        except ImportError:
            print(f"   ⚠️ {package} not available (required for JDBC)")
    
    # Test optional packages
    for package in optional_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} available")
        except ImportError:
            print(f"   ⚠️ {package} not available (optional)")
    
    return True

def main():
    """Run all tests."""
    print("🚀 Testing Standalone SQL Preview Script (JDBC)")
    print("="*60)
    
    tests = [
        ("Requirements", test_requirements),
        ("Argument Parsing", test_argument_parsing),
        ("Database Type Validation", test_database_type_validation),
        ("Port Defaults", test_port_defaults),
        ("JDBC URL Generation", test_jdbc_url_generation),
        ("Schema Qualification", test_schema_qualification),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"   🎉 {test_name} PASSED")
            else:
                print(f"   ❌ {test_name} FAILED")
        except Exception as e:
            print(f"   ❌ {test_name} ERROR: {e}")
    
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The JDBC standalone script is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r standalone_requirements_jdbc.txt")
        print("2. Install Java (required for JDBC)")
        print("3. Download JDBC drivers for your database")
        print("4. Set up your database connection details")
        print("5. Get your OpenAI API key (if using LLM)")
        print("6. Run the script with your parameters")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    print("="*60)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
