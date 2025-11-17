#!/usr/bin/env python3
"""
Test Setup Script for Standalone KPI Executor

This script validates that all prerequisites are properly installed
and configured before running the main KPI executor.
"""

import sys
import subprocess
import importlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_python_version():
    """Test Python version compatibility."""
    logger.info("Testing Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        logger.error(f"Python {version.major}.{version.minor} detected. Python 3.7+ required.")
        return False
    
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def test_required_packages():
    """Test required Python packages."""
    logger.info("Testing required packages...")
    
    required_packages = {
        'pyodbc': 'Database connectivity',
        'openai': 'OpenAI API client'
    }
    
    all_ok = True
    
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            logger.info(f"✅ {package} - OK ({description})")
        except ImportError:
            logger.error(f"❌ {package} - MISSING ({description})")
            all_ok = False
    
    return all_ok

def test_odbc_driver():
    """Test ODBC driver availability."""
    logger.info("Testing ODBC driver...")
    
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        
        sql_server_drivers = [d for d in drivers if 'SQL Server' in d]
        
        if not sql_server_drivers:
            logger.error("❌ No SQL Server ODBC drivers found")
            logger.error("   Please install 'ODBC Driver 17 for SQL Server'")
            return False
        
        logger.info(f"✅ ODBC drivers found: {', '.join(sql_server_drivers)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing ODBC driver: {e}")
        return False

def test_file_existence():
    """Test required files exist."""
    logger.info("Testing required files...")
    
    import os
    
    required_files = [
        'kpi_executor_standalone.py',
        'requirements_standalone.txt',
        'README_KPI_Executor.md'
    ]
    
    all_ok = True
    
    for filename in required_files:
        if os.path.exists(filename):
            logger.info(f"✅ {filename} - Found")
        else:
            logger.error(f"❌ {filename} - Missing")
            all_ok = False
    
    return all_ok

def test_openai_import():
    """Test OpenAI package import and basic functionality."""
    logger.info("Testing OpenAI package...")
    
    try:
        from openai import OpenAI
        logger.info("✅ OpenAI package import - OK")
        
        # Test client creation (without API key)
        try:
            client = OpenAI(api_key="test-key")
            logger.info("✅ OpenAI client creation - OK")
        except Exception as e:
            logger.warning(f"⚠️  OpenAI client creation warning: {e}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ OpenAI package import failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("="*60)
    logger.info("STANDALONE KPI EXECUTOR - SETUP VALIDATION")
    logger.info("="*60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Required Packages", test_required_packages),
        ("ODBC Driver", test_odbc_driver),
        ("Required Files", test_file_existence),
        ("OpenAI Package", test_openai_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            logger.info(f"✅ {test_name}")
            passed += 1
        else:
            logger.error(f"❌ {test_name}")
            failed += 1
    
    logger.info(f"\nTests passed: {passed}")
    logger.info(f"Tests failed: {failed}")
    
    if failed == 0:
        logger.info("\n🎉 All tests passed! You're ready to run the KPI executor.")
        logger.info("\nNext steps:")
        logger.info("1. Set up your configuration (see example_config.env)")
        logger.info("2. Run: python kpi_executor_standalone.py --help")
        logger.info("3. Or use the interactive scripts: run_kpi_executor.bat or ./run_kpi_executor.sh")
        return 0
    else:
        logger.error(f"\n❌ {failed} test(s) failed. Please fix the issues above before proceeding.")
        logger.error("\nCommon fixes:")
        logger.error("- Install missing packages: pip install -r requirements_standalone.txt")
        logger.error("- Install ODBC Driver 17 for SQL Server")
        logger.error("- Ensure all required files are in the current directory")
        return 1

if __name__ == "__main__":
    sys.exit(main())
