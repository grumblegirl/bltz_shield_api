#!/usr/bin/env python3
"""
Test script for BLTZ Shield API Supabase integration.

This script tests:
1. Supabase connection
2. Metadata validation
3. Database insertion
4. API endpoint with new schema
"""

import json
import sys
import os
from datetime import datetime

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_supabase_connection():
    """Test Supabase database connection."""
    print("🔍 Testing Supabase connection...")
    
    try:
        from backend.supabase_metadata import create_metadata_client
        
        # Test connection
        with create_metadata_client(use_service_role=True) as client:
            if client.is_connected:
                print("✅ Supabase connection successful")
                
                # Test retrieving recent metadata
                recent = client.get_recent_metadata(limit=5)
                if recent is not None:
                    print(f"✅ Retrieved {len(recent)} recent metadata records")
                else:
                    print("ℹ️ No metadata records found (this is normal for new setup)")
                
                return True
            else:
                print("❌ Supabase connection failed")
                return False
                
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False

def test_metadata_insertion():
    """Test metadata insertion functionality."""
    print("\n📝 Testing metadata insertion...")
    
    try:
        from backend.supabase_metadata import insert_metadata
        
        # Create sample metadata following the new schema
        sample_data = {
            "model": "gpt",
            "timestamp": datetime.now().isoformat(),
            "metadata_data": {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "screen_width": 1920,
                "screen_height": 1080,
                "timezone": "America/New_York",
                "language": "en-US",
                "platform": "MacIntel",
                "cookie_enabled": True,
                "online": True,
                "touch_support": False,
                "browser_name": "Chrome",
                "browser_version": "120.0.0.0"
            }
        }
        
        # Test insertion
        success = insert_metadata(sample_data, use_service_role=True)
        
        if success:
            print("✅ Metadata insertion successful")
            return True
        else:
            print("❌ Metadata insertion failed")
            return False
            
    except Exception as e:
        print(f"❌ Metadata insertion error: {e}")
        return False

def test_api_logic():
    """Test API logic with new schema."""
    print("\n🔧 Testing API logic...")
    
    try:
        from backend.api_logic import APILogic
        
        api = APILogic()
        
        # Test with new schema
        test_data = {
            "model": "gpt",
            "timestamp": "2025-01-27T12:00:00Z",
            "metadata_data": {
                "user_agent": "Mozilla/5.0 (Test Browser)",
                "screen_resolution": "1920x1080",
                "language": "en-US",
                "test_field": "test_value"
            }
        }
        
        # Test metadata endpoint
        response = api.handle_metadata_endpoint(test_data)
        
        if response.get("result") == "success":
            print("✅ API logic test successful")
            print(f"   Database stored: {response.get('metadata_summary', {}).get('database_stored', False)}")
            return True
        else:
            print(f"❌ API logic test failed: {response.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ API logic test error: {e}")
        return False

def test_schema_validation():
    """Test schema validation with various inputs."""
    print("\n✅ Testing schema validation...")
    
    try:
        from backend.api_logic import APILogic
        
        api = APILogic()
        
        test_cases = [
            # Valid case
            {
                "name": "Valid request",
                "data": {
                    "model": "gpt",
                    "timestamp": "2025-01-27T12:00:00Z",
                    "metadata_data": {"test": "value"}
                },
                "should_pass": True
            },
            # Missing field
            {
                "name": "Missing model field",
                "data": {
                    "timestamp": "2025-01-27T12:00:00Z",
                    "metadata_data": {"test": "value"}
                },
                "should_pass": False
            },
            # Invalid model
            {
                "name": "Invalid model type",
                "data": {
                    "model": "invalid_model",
                    "timestamp": "2025-01-27T12:00:00Z", 
                    "metadata_data": {"test": "value"}
                },
                "should_pass": False
            },
            # Invalid metadata_data type
            {
                "name": "Invalid metadata_data type",
                "data": {
                    "model": "gpt",
                    "timestamp": "2025-01-27T12:00:00Z",
                    "metadata_data": "not_a_dict"
                },
                "should_pass": False
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = api.handle_metadata_endpoint(test_case["data"])
            success = response.get("result") == "success"
            
            if success == test_case["should_pass"]:
                print(f"   ✅ {test_case['name']}: PASS")
            else:
                print(f"   ❌ {test_case['name']}: FAIL")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Schema validation test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 BLTZ Shield API Supabase Integration Tests")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Supabase Connection", test_supabase_connection),
        ("Schema Validation", test_schema_validation),
        ("API Logic", test_api_logic),
        ("Metadata Insertion", test_metadata_insertion)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("-" * 40)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
    else:
        print("⚠️ Some tests failed. Check configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)