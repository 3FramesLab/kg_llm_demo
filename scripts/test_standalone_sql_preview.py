#!/usr/bin/env python3
"""
Test script for standalone_sql_preview.py

This script tests the standalone SQL preview functionality without requiring
actual database connections or OpenAI API keys.

Usage:
    python test_standalone_sql_preview.py
"""

import sys
import os
import json
import tempfile
import subprocess
from unittest.mock import patch, MagicMock

def test_argument_parsing():
    """Test command line argument parsing."""
    print("🧪 Testing argument parsing...")
    
    # Test help output
    try:
        result = subprocess.run([
            sys.executable, 'standalone_sql_preview.py', '--help'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0 and 'Standalone SQL Preview' in result.stdout:
            print("   ✅ Help output works correctly")
            return True
        else:
            print(f"   ❌ Help output failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Argument parsing test failed: {e}")
        return False

def test_mock_execution():
    """Test script execution with mocked dependencies."""
    print("🧪 Testing mock execution...")
    
    # Create a test script that mocks the dependencies
    test_script = '''
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Mock the dependencies
class MockOpenAI:
    api_key = None
    
    class ChatCompletion:
        @staticmethod
        def create(**kwargs):
            class MockResponse:
                class MockChoice:
                    class MockMessage:
                        content = """
                        {
                            "definition": "test query",
                            "source_table": "hana_material_master",
                            "target_table": null,
                            "operation": "NOT_IN",
                            "filters": [],
                            "confidence": 0.85,
                            "reasoning": "Found table match"
                        }
                        """
                    message = MockMessage()
                choices = [MockChoice()]
            return MockResponse()

class MockPyodbc:
    @staticmethod
    def connect(conn_str):
        class MockConnection:
            def cursor(self):
                class MockCursor:
                    description = [('test', 'varchar')]
                    def execute(self, query, params=None):
                        pass
                    def fetchall(self):
                        return [('hana_material_master',)]
                    def fetchone(self):
                        return (1,)
                return MockCursor()
        return MockConnection()

# Patch the imports
import sys
sys.modules['openai'] = MockOpenAI()
sys.modules['pyodbc'] = MockPyodbc()

# Import and test the main functionality
from standalone_sql_preview import StandaloneSQLPreview, create_argument_parser

# Create mock arguments
class MockArgs:
    nl_definition = "get products from hana_material_master where OPS_PLANNER is missing"
    kg_name = "Test_KG"
    select_schema = "test_schema"
    openai_key = "test-key"
    temperature = 0.7
    db_host = "localhost"
    db_port = 1433
    db_name = "test_db"
    db_user = "test_user"
    db_password = "test_pass"
    use_llm = True
    verbose = True
    output_format = "json"

try:
    # Test initialization
    sql_preview = StandaloneSQLPreview(MockArgs())
    print("✅ Initialization successful")
    
    # Test parsing
    intent = sql_preview.parse_nl_definition()
    print(f"✅ Parsing successful: {intent.source_table}")
    
    # Test SQL generation
    sql = sql_preview.generate_sql(intent)
    print(f"✅ SQL generation successful: {len(sql)} characters")
    
    # Test enhancement
    enhancement = sql_preview.apply_material_master_enhancement(sql)
    print(f"✅ Enhancement successful: {enhancement['enhancement_applied']}")
    
    print("🎉 All mock tests passed!")
    
except Exception as e:
    print(f"❌ Mock test failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    try:
        # Write test script to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            temp_script = f.name
        
        # Run the test script
        result = subprocess.run([
            sys.executable, temp_script
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        # Clean up
        os.unlink(temp_script)
        
        if "All mock tests passed!" in result.stdout:
            print("   ✅ Mock execution test passed")
            return True
        else:
            print(f"   ❌ Mock execution failed:")
            print(f"   STDOUT: {result.stdout}")
            print(f"   STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Mock execution test failed: {e}")
        return False

def test_output_formats():
    """Test different output formats."""
    print("🧪 Testing output formats...")
    
    try:
        # Import the format function
        sys.path.insert(0, os.path.dirname(__file__))
        from standalone_sql_preview import format_output
        
        # Test data
        test_result = {
            "success": True,
            "generated_sql": "SELECT * FROM test_table",
            "enhanced_sql": "SELECT * FROM test_table LEFT JOIN...",
            "enhancement_applied": True,
            "material_master_added": True,
            "ops_planner_added": True,
            "storage_type": "mssql",
            "intent": {
                "definition": "test query",
                "confidence": 0.85,
                "query_type": "comparison_query",
                "operation": "NOT_IN",
                "source_table": "test_table"
            },
            "performance": {
                "total_time_ms": 1234.56,
                "process_time_ms": 567.89
            }
        }
        
        # Test JSON format
        json_output = format_output(test_result, 'json')
        json.loads(json_output)  # Validate JSON
        print("   ✅ JSON format works")
        
        # Test pretty format
        pretty_output = format_output(test_result, 'pretty')
        if "SQL PREVIEW RESULT" in pretty_output and "SELECT * FROM test_table" in pretty_output:
            print("   ✅ Pretty format works")
        else:
            print("   ❌ Pretty format failed")
            return False
        
        # Test SQL-only format
        sql_output = format_output(test_result, 'sql-only')
        if "SELECT * FROM test_table LEFT JOIN" in sql_output:
            print("   ✅ SQL-only format works")
        else:
            print("   ❌ SQL-only format failed")
            return False
        
        # Test error format
        error_result = {
            "success": False,
            "error": "Test error",
            "error_type": "TestError",
            "total_time_ms": 123.45
        }
        
        error_output = format_output(error_result, 'pretty')
        if "SQL PREVIEW ERROR" in error_output and "Test error" in error_output:
            print("   ✅ Error format works")
        else:
            print("   ❌ Error format failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Output format test failed: {e}")
        return False

def test_requirements():
    """Test if required packages can be imported."""
    print("🧪 Testing requirements...")
    
    required_packages = ['json', 'argparse', 'logging', 'time', 'os', 'sys']
    optional_packages = ['openai', 'pyodbc']
    
    # Test required packages
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} available")
        except ImportError:
            print(f"   ❌ {package} not available (required)")
            return False
    
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
    print("🚀 Testing Standalone SQL Preview Script")
    print("="*60)
    
    tests = [
        ("Requirements", test_requirements),
        ("Argument Parsing", test_argument_parsing),
        ("Output Formats", test_output_formats),
        ("Mock Execution", test_mock_execution),
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
        print("🎉 ALL TESTS PASSED! The standalone script is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r standalone_requirements.txt")
        print("2. Set up your database connection details")
        print("3. Get your OpenAI API key (if using LLM)")
        print("4. Run the script with your parameters")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    print("="*60)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
