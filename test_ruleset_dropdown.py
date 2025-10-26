#!/usr/bin/env python3
"""
Test script to diagnose ruleset dropdown issues.
Run this to verify the backend is returning rulesets correctly.
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
RULESETS_ENDPOINT = f"{BACKEND_URL}/v1/reconciliation/rulesets"
RULESETS_DIR = Path("data/reconciliation_rules")

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_section(text):
    """Print a formatted section."""
    print(f"\n📋 {text}")
    print("-" * 80)

def check_backend_running():
    """Check if backend is running."""
    print_section("1. Checking if Backend is Running")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"✅ Backend is running on {BACKEND_URL}")
        print(f"   Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Backend is NOT running on {BACKEND_URL}")
        print(f"   Start it with: python -m uvicorn kg_builder.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

def check_rulesets_folder():
    """Check if rulesets folder exists and has files."""
    print_section("2. Checking Rulesets Folder")
    
    if not RULESETS_DIR.exists():
        print(f"❌ Rulesets folder does NOT exist: {RULESETS_DIR}")
        print(f"   Create it with: mkdir -p {RULESETS_DIR}")
        return False
    
    print(f"✅ Rulesets folder exists: {RULESETS_DIR}")
    
    ruleset_files = list(RULESETS_DIR.glob("*.json"))
    print(f"   Found {len(ruleset_files)} ruleset files")
    
    if len(ruleset_files) == 0:
        print(f"⚠️  No ruleset files found in {RULESETS_DIR}")
        print(f"   Create a ruleset first using the Reconciliation page")
        return False
    
    for file in ruleset_files:
        print(f"   - {file.name}")
    
    return True

def check_api_endpoint():
    """Check the API endpoint."""
    print_section("3. Testing API Endpoint")
    
    print(f"Calling: {RULESETS_ENDPOINT}")
    
    try:
        response = requests.get(RULESETS_ENDPOINT, timeout=10)
        print(f"✅ API endpoint responded")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Expected 200, got {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'application/json' not in content_type:
            print(f"❌ Expected JSON response, got: {content_type}")
            return False
        
        print(f"✅ Response is valid JSON")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API endpoint")
        print(f"   Make sure backend is running on {BACKEND_URL}")
        return False
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        return False

def check_response_format():
    """Check the response format."""
    print_section("4. Checking Response Format")
    
    try:
        response = requests.get(RULESETS_ENDPOINT, timeout=10)
        data = response.json()
        
        print(f"Response structure:")
        print(json.dumps(data, indent=2, default=str)[:500])
        
        # Check required fields
        if 'success' not in data:
            print(f"❌ Missing 'success' field")
            return False
        
        if not data.get('success'):
            print(f"❌ 'success' is False")
            return False
        
        print(f"✅ 'success' field is True")
        
        if 'rulesets' not in data:
            print(f"❌ Missing 'rulesets' field")
            return False
        
        print(f"✅ 'rulesets' field exists")
        
        rulesets = data.get('rulesets', [])
        print(f"   Found {len(rulesets)} rulesets")
        
        if len(rulesets) == 0:
            print(f"⚠️  No rulesets in response")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing response: {e}")
        return False

def check_ruleset_fields():
    """Check if rulesets have required fields."""
    print_section("5. Checking Ruleset Fields")
    
    try:
        response = requests.get(RULESETS_ENDPOINT, timeout=10)
        data = response.json()
        rulesets = data.get('rulesets', [])
        
        if len(rulesets) == 0:
            print(f"⚠️  No rulesets to check")
            return False
        
        first_ruleset = rulesets[0]
        print(f"First ruleset:")
        print(json.dumps(first_ruleset, indent=2, default=str))
        
        # Check required fields
        required_fields = ['ruleset_id', 'ruleset_name']
        missing_fields = [f for f in required_fields if f not in first_ruleset]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print(f"✅ All required fields present")
        print(f"   - ruleset_id: {first_ruleset.get('ruleset_id')}")
        print(f"   - ruleset_name: {first_ruleset.get('ruleset_name')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking fields: {e}")
        return False

def main():
    """Run all checks."""
    print_header("RULESET DROPDOWN DIAGNOSTIC TEST")
    
    checks = [
        ("Backend Running", check_backend_running),
        ("Rulesets Folder", check_rulesets_folder),
        ("API Endpoint", check_api_endpoint),
        ("Response Format", check_response_format),
        ("Ruleset Fields", check_ruleset_fields),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            results.append((name, False))
    
    # Summary
    print_header("SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Ruleset dropdown should work.")
        return 0
    else:
        print("\n⚠️  Some checks failed. See details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

