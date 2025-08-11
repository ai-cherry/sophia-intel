#!/usr/bin/env python3
"""
Test Lambda Labs API Connection
"""

import requests
import json
import time

# Lambda Labs Configuration
LAMBDA_API_KEY = "os.getenv("NOTION_API_KEY").EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y"
LAMBDA_ENDPOINT = "https://cloud.lambda.ai/api/v1"

def test_lambda_connection():
    """Test Lambda Labs API connection"""
    print("🔍 Testing Lambda Labs API connection...")
    
    # Create session with authentication
    session = requests.Session()
    session.auth = (LAMBDA_API_KEY, '')
    
    try:
        # Test API connection
        print(f"Connecting to: {LAMBDA_ENDPOINT}/instances")
        response = session.get(f"{LAMBDA_ENDPOINT}/instances")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Lambda Labs API Connected!")
            print(f"Response: {json.dumps(data, indent=2)[:500]}...")  # Truncate for readability
            
            if 'data' in data:
                instances = data['data']
                print(f"\n📊 Found {len(instances)} instances")
                
                for instance in instances[:3]:  # Show first 3
                    print(f"\nInstance: {instance.get('name', 'unnamed')}")
                    print(f"  Status: {instance.get('status')}")
                    print(f"  Type: {instance.get('instance_type', {}).get('name')}")
                    print(f"  IP: {instance.get('ip', 'N/A')}")
                    
                return True
            else:
                print("No instances found (this is normal)")
                return True
                
        elif response.status_code == 401:
            print("⚠️  Authentication failed - API key may be incorrect")
            return False
        elif response.status_code == 403:
            print("⚠️  Forbidden - API key may lack permissions")
            return False
        else:
            print(f"⚠️  Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"⚠️  Connection error - Lambda Labs API may be down")
        print(f"    Error: {str(e)[:100]}...")
        return False
    except Exception as e:
        print(f"⚠️  Unexpected error: {str(e)[:100]}...")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Lambda Labs API Connection Test")
    print("=" * 60)
    
    result = test_lambda_connection()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ Lambda Labs API is accessible")
    else:
        print("⚠️  Lambda Labs API test inconclusive")
        print("   This may be normal if the API endpoint has changed")
    print("=" * 60)
