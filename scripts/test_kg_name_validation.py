#!/usr/bin/env python3
"""
Test script to verify kg_name validation works correctly.

This script tests various scenarios to ensure kg_name validation
throws appropriate exceptions when kg_name is missing, empty, or "default".
"""

import sys
import os
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000/v1/landing-kpi-mssql"
TEST_KPI_ID = 21  # Adjust this to a valid KPI ID in your system

def test_kg_name_validation():
    """Test kg_name validation in various scenarios."""
    print("🧪 Testing kg_name Validation")
    print("="*60)
    
    test_cases = [
        {
            "name": "Empty Request Body",
            "payload": {},
            "should_fail": True,
            "expected_error": "kg_name is required"
        },
        {
            "name": "Missing kg_name",
            "payload": {
                "schemas": ["newdqnov7"],
                "use_llm": True,
                "limit": 1000
            },
            "should_fail": True,
            "expected_error": "kg_name is required"
        },
        {
            "name": "Empty kg_name",
            "payload": {
                "kg_name": "",
                "schemas": ["newdqnov7"],
                "use_llm": True
            },
            "should_fail": True,
            "expected_error": "kg_name is required"
        },
        {
            "name": "Whitespace kg_name",
            "payload": {
                "kg_name": "   ",
                "schemas": ["newdqnov7"],
                "use_llm": True
            },
            "should_fail": True,
            "expected_error": "kg_name is required"
        },
        {
            "name": "Default kg_name (lowercase)",
            "payload": {
                "kg_name": "default",
                "schemas": ["newdqnov7"],
                "use_llm": True
            },
            "should_fail": True,
            "expected_error": "kg_name is required"
        },
        {
            "name": "Default kg_name (uppercase)",
            "payload": {
                "kg_name": "DEFAULT",
                "schemas": ["newdqnov7"],
                "use_llm": True
            },
            "should_fail": True,
            "expected_error": "kg_name is required"
        },
        {
            "name": "Default kg_name (mixed case)",
            "payload": {
                "kg_name": "Default",
                "schemas": ["newdqnov7"],
                "use_llm": True
            },
            "should_fail": True,
            "expected_error": "kg_name is required"
        },
        {
            "name": "Null kg_name",
            "payload": {
                "kg_name": None,
                "schemas": ["newdqnov7"],
                "use_llm": True
            },
            "should_fail": True,
            "expected_error": "kg_name is required"
        },
        {
            "name": "Valid kg_name",
            "payload": {
                "kg_name": "New_KG_101",
                "schemas": ["newdqnov7"],
                "use_llm": True,
                "limit": 1000
            },
            "should_fail": False,
            "expected_error": None
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{total}: {test_case['name']}")
        
        try:
            # Test KPI execution endpoint
            response = requests.post(
                f"{BASE_URL}/kpis/{TEST_KPI_ID}/execute",
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if test_case['should_fail']:
                if response.status_code == 400:
                    response_data = response.json()
                    if test_case['expected_error'] in response_data.get('error', ''):
                        print(f"   ✅ PASS: Got expected error - {response_data['error']}")
                        passed += 1
                    else:
                        print(f"   ❌ FAIL: Got error but wrong message - {response_data.get('error', 'No error message')}")
                else:
                    print(f"   ❌ FAIL: Expected 400 error but got {response.status_code}")
            else:
                if response.status_code in [200, 201, 202]:
                    print(f"   ✅ PASS: Valid request accepted - {response.status_code}")
                    passed += 1
                else:
                    response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    print(f"   ❌ FAIL: Valid request rejected - {response.status_code}: {response_data.get('error', 'Unknown error')}")
                    
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️ SKIP: Cannot connect to server at {BASE_URL}")
            print(f"        Make sure the server is running on localhost:8000")
            continue
        except requests.exceptions.Timeout:
            print(f"   ⚠️ SKIP: Request timed out")
            continue
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! kg_name validation is working correctly.")
    else:
        print("❌ Some tests failed. Check the validation logic.")
    
    return passed == total

def test_sql_preview_validation():
    """Test kg_name validation in SQL preview endpoint."""
    print("\n🧪 Testing SQL Preview kg_name Validation")
    print("="*60)
    
    test_cases = [
        {
            "name": "SQL Preview - Missing kg_name",
            "payload": {
                "query": "get products where planner is missing",
                "select_schema": "newdqnov7"
            },
            "should_fail": True
        },
        {
            "name": "SQL Preview - Default kg_name",
            "payload": {
                "query": "get products where planner is missing",
                "kg_name": "default",
                "select_schema": "newdqnov7"
            },
            "should_fail": True
        },
        {
            "name": "SQL Preview - Valid kg_name",
            "payload": {
                "query": "get products where planner is missing",
                "kg_name": "New_KG_101",
                "select_schema": "newdqnov7"
            },
            "should_fail": False
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{total}: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/sql-preview",
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if test_case['should_fail']:
                if response.status_code == 400:
                    response_data = response.json()
                    print(f"   ✅ PASS: Got expected error - {response_data.get('error', 'No error message')}")
                    passed += 1
                else:
                    print(f"   ❌ FAIL: Expected 400 error but got {response.status_code}")
            else:
                if response.status_code in [200, 201]:
                    print(f"   ✅ PASS: Valid request accepted - {response.status_code}")
                    passed += 1
                else:
                    response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    print(f"   ❌ FAIL: Valid request rejected - {response.status_code}: {response_data.get('error', 'Unknown error')}")
                    
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️ SKIP: Cannot connect to server")
            continue
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 SQL PREVIEW RESULTS: {passed}/{total} tests passed")
    return passed == total

def main():
    """Run all validation tests."""
    print("🚀 Testing kg_name Validation Implementation")
    print("="*80)
    
    # Test KPI execution validation
    kpi_result = test_kg_name_validation()
    
    # Test SQL preview validation
    preview_result = test_sql_preview_validation()
    
    print("\n" + "="*80)
    print("📊 OVERALL RESULTS:")
    print(f"   KPI Execution Validation: {'✅ PASS' if kpi_result else '❌ FAIL'}")
    print(f"   SQL Preview Validation: {'✅ PASS' if preview_result else '❌ FAIL'}")
    
    if kpi_result and preview_result:
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        print("   kg_name validation is working correctly across all endpoints.")
        print("\n📋 What was tested:")
        print("   ✅ Empty request body")
        print("   ✅ Missing kg_name parameter")
        print("   ✅ Empty string kg_name")
        print("   ✅ Whitespace-only kg_name")
        print("   ✅ 'default' kg_name (all cases)")
        print("   ✅ null kg_name")
        print("   ✅ Valid kg_name acceptance")
        print("\n🎯 All scenarios now properly reject invalid kg_name values!")
    else:
        print("\n❌ Some validation tests failed.")
        print("   Please check the implementation and try again.")
    
    return kpi_result and preview_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
