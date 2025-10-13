#!/usr/bin/env python3
"""
Test script for BLTZ Shield API
Tests the /metadata endpoint with various scenarios
"""

import json
import requests
import sys

# Configuration
BASE_URL = "http://localhost:8080"
API_KEY = "bltz_shield_2025_secure_key"

def test_metadata_endpoint():
    """Test the /metadata endpoint"""
    
    print("Testing BLTZ Shield API /metadata endpoint")
    print("=" * 50)
    
    # Test 1: Valid request
    print("\n1. Testing valid request with correct API key:")
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    data = {"test": "metadata", "user": "test_user", "timestamp": "2025-10-12"}
    
    try:
        response = requests.post(f"{BASE_URL}/metadata", 
                               headers=headers, 
                               json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server. Make sure server.py is running.")
        return
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Test 2: Invalid API key
    print("\n2. Testing with invalid API key:")
    headers = {"X-API-Key": "invalid_key", "Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{BASE_URL}/metadata", 
                               headers=headers, 
                               json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Missing API key
    print("\n3. Testing with missing API key:")
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{BASE_URL}/metadata", 
                               headers=headers, 
                               json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Invalid JSON
    print("\n4. Testing with invalid JSON:")
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{BASE_URL}/metadata", 
                               headers=headers, 
                               data="{invalid json}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Unknown endpoint
    print("\n5. Testing unknown endpoint:")
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{BASE_URL}/unknown", 
                               headers=headers, 
                               json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_metadata_endpoint()