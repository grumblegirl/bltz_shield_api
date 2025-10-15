#!/usr/bin/env python3
"""
Sample curl commands and test data for BLTZ Shield API with Supabase integration.

This script generates curl commands for testing the new API schema:
{"model": "gpt", "timestamp": "...", "metadata_data": {...}}
"""

import json
from datetime import datetime


def generate_sample_metadata():
    """Generate sample browser metadata with realistic fields."""
    return {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "screen_width": 1920,
        "screen_height": 1080,
        "screen_color_depth": 24,
        "screen_pixel_depth": 24,
        "available_screen_width": 1920,
        "available_screen_height": 1055,
        "inner_width": 1920,
        "inner_height": 971,
        "outer_width": 1920,
        "outer_height": 1080,
        "device_pixel_ratio": 1,
        "timezone_offset": 300,
        "timezone": "America/New_York",
        "language": "en-US",
        "languages": ["en-US", "en"],
        "platform": "MacIntel",
        "cpu_class": None,
        "oscpu": None,
        "app_name": "Netscape",
        "app_version": "5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "app_code_name": "Mozilla",
        "product": "Gecko",
        "product_version": "20030107",
        "vendor": "Google Inc.",
        "vendor_version": None,
        "cookie_enabled": True,
        "online": True,
        "java_enabled": False,
        "touch_support": False,
        "max_touch_points": 0,
        "hardware_concurrency": 8,
        "device_memory": 8,
        "webgl_vendor": "Intel Inc.",
        "webgl_renderer": "Intel Iris Plus Graphics OpenGL Engine",
        "canvas_fingerprint": "a1b2c3d4e5f67890",
        "webgl_fingerprint": "x9y8z7w6v5u4t3s2",
        "audio_fingerprint": "m1n2o3p4q5r6s7t8",
        "battery_charging": True,
        "battery_level": 0.85,
        "connection_type": "wifi",
        "connection_downlink": 10,
        "connection_effective_type": "4g",
        "connection_rtt": 100,
        "permissions_notifications": "default",
        "permissions_geolocation": "denied",
        "permissions_camera": "denied",
        "permissions_microphone": "denied",
        "do_not_track": "1",
        "referrer": "https://example.com/",
        "url": "https://app.example.com/dashboard",
        "title": "Dashboard - Example App",
        "session_storage_available": True,
        "local_storage_available": True,
        "indexed_db_available": True
    }


def create_api_request(model="gpt", custom_metadata=None):
    """Create a complete API request payload."""
    metadata = custom_metadata or generate_sample_metadata()
    
    return {
        "model": model,
        "timestamp": datetime.now().isoformat() + "Z",
        "metadata_data": metadata
    }


def generate_curl_commands():
    """Generate curl commands for testing."""
    
    print("🌐 BLTZ Shield API - Supabase Integration Test Commands")
    print("=" * 70)
    
    # Test data variations
    test_cases = [
        {
            "name": "GPT Model with Full Metadata",
            "model": "gpt",
            "metadata": generate_sample_metadata()
        },
        {
            "name": "Claude Model with Minimal Metadata", 
            "model": "claude",
            "metadata": {
                "user_agent": "Mozilla/5.0 (Test Browser)",
                "screen_width": 1280,
                "screen_height": 720,
                "language": "en-US"
            }
        },
        {
            "name": "Gemini Model with Custom Fields",
            "model": "gemini", 
            "metadata": {
                "browser_name": "Chrome",
                "browser_version": "120.0.0.0",
                "os_name": "macOS",
                "os_version": "14.0",
                "device_type": "desktop",
                "session_id": "abc123def456",
                "user_id": "user_789"
            }
        }
    ]
    
    # Generate commands for each environment
    environments = [
        ("Local Development", "http://localhost:8000"),
        ("Production", "https://bltz-shield-api.vercel.app")
    ]
    
    for env_name, base_url in environments:
        print(f"\n📍 {env_name} ({base_url})")
        print("-" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            request_data = create_api_request(
                model=test_case["model"],
                custom_metadata=test_case["metadata"]
            )
            
            json_payload = json.dumps(request_data, indent=None)
            
            print(f"\n{i}. {test_case['name']}:")
            print("```bash")
            print(f"curl -X POST '{base_url}/metadata' \\")
            print(f"  -H 'Content-Type: application/json' \\")
            print(f"  -H 'X-API-Key: bltz_shield_2025_secure_key' \\")
            print(f"  -d '{json_payload}'")
            print("```")


def generate_test_data_files():
    """Generate JSON test data files."""
    print("\n📁 Generating Test Data Files")
    print("-" * 40)
    
    test_files = [
        ("gpt_metadata.json", create_api_request("gpt")),
        ("claude_metadata.json", create_api_request("claude")),
        ("gemini_metadata.json", create_api_request("gemini")),
        ("llama_metadata.json", create_api_request("llama"))
    ]
    
    for filename, data in test_files:
        filepath = f"test/data/{filename}"
        
        # Create test data directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Created {filepath}")


def show_expected_response():
    """Show expected API response format."""
    print("\n📋 Expected Response Format")
    print("-" * 40)
    
    expected = {
        "result": "success",
        "message": "Metadata request processed successfully", 
        "timestamp": "2025-01-27T17:30:00.123456",
        "metadata_summary": {
            "model": "gpt",
            "timestamp": "2025-01-27T17:30:00Z",
            "fields_count": 53,
            "database_stored": True
        }
    }
    
    print("```json")
    print(json.dumps(expected, indent=2))
    print("```")


def show_error_cases():
    """Show common error cases and responses."""
    print("\n❌ Error Cases to Test")
    print("-" * 40)
    
    error_cases = [
        {
            "name": "Missing API Key",
            "curl": "curl -X POST 'https://bltz-shield-api.vercel.app/metadata' -H 'Content-Type: application/json' -d '{\"model\":\"gpt\"}'",
            "expected": {"result": "error", "message": "Invalid or missing API key"}
        },
        {
            "name": "Invalid Model",
            "data": {"model": "invalid", "timestamp": "2025-01-27T12:00:00Z", "metadata_data": {}},
            "expected": {"result": "error", "message": "Unsupported model: invalid"}
        },
        {
            "name": "Missing Required Field",
            "data": {"model": "gpt", "metadata_data": {}},
            "expected": {"result": "error", "message": "Missing required fields: ['timestamp']"}
        }
    ]
    
    for case in error_cases:
        print(f"\n• {case['name']}:")
        if 'curl' in case:
            print(f"  Command: {case['curl']}")
        else:
            print(f"  Data: {json.dumps(case['data'])}")
        print(f"  Expected: {json.dumps(case['expected'])}")


def main():
    """Main function to generate all test content."""
    generate_curl_commands()
    generate_test_data_files()
    show_expected_response()
    show_error_cases()
    
    print("\n🎯 Quick Test Command (Production):")
    print("-" * 40)
    simple_test = create_api_request("gpt", {
        "user_agent": "Test Browser",
        "screen_width": 1920,
        "language": "en-US"
    })
    
    print("```bash")
    print("curl -X POST 'https://bltz-shield-api.vercel.app/metadata' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -H 'X-API-Key: bltz_shield_2025_secure_key' \\") 
    print(f"  -d '{json.dumps(simple_test)}'")
    print("```")
    
    print("\n✨ Ready to test! Use the commands above to validate the API.")


if __name__ == "__main__":
    main()