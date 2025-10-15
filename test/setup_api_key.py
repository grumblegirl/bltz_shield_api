#!/usr/bin/env python3
"""
Setup script to create an API key record for testing.

This script inserts a record into the api_key table to map the hardcoded API key
to an organization_id for testing purposes.
"""

import sys
import os
from datetime import datetime

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def setup_test_api_key():
    """Create a test API key record in the database."""
    print("🔧 Setting up test API key record...")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from backend.supabase_metadata import create_metadata_client
        
        # Test data
        api_key_record = {
            "organization_id": 1,
            "created_by": "system",
            "deleted": False,
            "api_key": "bltz_shield_2025_secure_key"
        }
        
        with create_metadata_client(use_service_role=True) as client:
            if not client.is_connected:
                print("❌ Failed to connect to Supabase")
                return False
            
            # Check if API key already exists
            existing = (
                client.client
                .table("api_key")
                .select("*")
                .eq("api_key", api_key_record["api_key"])
                .execute()
            )
            
            if existing.data:
                print(f"✅ API key record already exists: {existing.data[0]}")
                return True
            
            # Insert new API key record
            response = (
                client.client
                .table("api_key")
                .insert(api_key_record)
                .execute()
            )
            
            if response.data:
                print(f"✅ Successfully created API key record: {response.data[0]}")
                return True
            else:
                print("❌ Failed to create API key record")
                return False
                
    except Exception as e:
        print(f"❌ Error setting up API key: {e}")
        return False

def test_api_key_lookup():
    """Test the API key lookup functionality."""
    print("\n🔍 Testing API key lookup...")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from backend.supabase_metadata import create_metadata_client
        
        with create_metadata_client(use_service_role=True) as client:
            org_id = client.get_organization_id_from_api_key("bltz_shield_2025_secure_key")
            
            if org_id:
                print(f"✅ Successfully looked up organization_id: {org_id}")
                return True
            else:
                print("❌ Failed to lookup organization_id")
                return False
                
    except Exception as e:
        print(f"❌ Error testing API key lookup: {e}")
        return False

def main():
    """Run setup and tests."""
    print("🚀 BLTZ Shield API - API Key Setup")
    print("=" * 50)
    
    success1 = setup_test_api_key()
    success2 = test_api_key_lookup()
    
    if success1 and success2:
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Test curl command:")
        print('curl -X POST \'https://bltz-shield-api.vercel.app/metadata\' \\')
        print('  -H \'Content-Type: application/json\' \\')
        print('  -H \'X-API-Key: bltz_shield_2025_secure_key\' \\')
        print('  -d \'{')
        print('    "provider": "openai",')
        print('    "timestamp": "2025-10-14T22:30:15.123Z",')
        print('    "meta_data": {"test": "data"},')
        print('    "user": "user@example.com",')
        print('    "license": "plus"')
        print('  }\'')
    else:
        print("\n⚠️ Setup failed. Check configuration.")
    
    return success1 and success2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)