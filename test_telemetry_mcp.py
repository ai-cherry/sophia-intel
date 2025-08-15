#!/usr/bin/env python3
"""
Test script for Telemetry MCP Server
Tests all three tools: get_usage, get_billing_status, get_integration_health
"""

import requests
import json
import time
from datetime import datetime

def test_telemetry_mcp(base_url="http://localhost:5004"):
    """Test all Telemetry MCP endpoints"""
    print("🧪 TESTING TELEMETRY MCP SERVER")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data['status']}")
            print(f"   Services monitored: {health_data['services_monitored']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False
    
    # Get list of services
    print("\n2. Getting list of services...")
    try:
        response = requests.get(f"{base_url}/services", timeout=10)
        if response.status_code == 200:
            services_data = response.json()
            services = services_data['data']['services']
            print(f"✅ Found {len(services)} services: {', '.join(services)}")
        else:
            print(f"❌ Services endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Services endpoint error: {str(e)}")
        return False
    
    # Test each tool for each service
    test_services = services[:3]  # Test first 3 services for demo
    results = {}
    
    for service in test_services:
        print(f"\n3. Testing service: {service}")
        results[service] = {}
        
        # Test get_usage
        print(f"   Testing get_usage for {service}...")
        try:
            response = requests.get(f"{base_url}/get_usage/{service}", timeout=10)
            if response.status_code == 200:
                usage_data = response.json()
                if usage_data['success']:
                    usage = usage_data['data']
                    print(f"   ✅ Usage: {usage['current_usage']} {usage['unit']} (${usage['cost_estimate']})")
                    results[service]['usage'] = 'success'
                else:
                    print(f"   ❌ Usage failed: {usage_data.get('error', 'Unknown error')}")
                    results[service]['usage'] = 'failed'
            else:
                print(f"   ❌ Usage endpoint failed: {response.status_code}")
                results[service]['usage'] = 'failed'
        except Exception as e:
            print(f"   ❌ Usage error: {str(e)}")
            results[service]['usage'] = 'error'
        
        # Test get_billing_status
        print(f"   Testing get_billing_status for {service}...")
        try:
            response = requests.get(f"{base_url}/get_billing_status/{service}", timeout=10)
            if response.status_code == 200:
                billing_data = response.json()
                if billing_data['success']:
                    billing = billing_data['data']
                    print(f"   ✅ Billing: ${billing['monthly_spend']}/month, ${billing['daily_spend']}/day")
                    results[service]['billing'] = 'success'
                else:
                    print(f"   ❌ Billing failed: {billing_data.get('error', 'Unknown error')}")
                    results[service]['billing'] = 'failed'
            else:
                print(f"   ❌ Billing endpoint failed: {response.status_code}")
                results[service]['billing'] = 'failed'
        except Exception as e:
            print(f"   ❌ Billing error: {str(e)}")
            results[service]['billing'] = 'error'
        
        # Test get_integration_health
        print(f"   Testing get_integration_health for {service}...")
        try:
            response = requests.get(f"{base_url}/get_integration_health/{service}", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                if health_data['success']:
                    health = health_data['data']
                    print(f"   ✅ Health: {health['status']} ({health['uptime_percentage']:.1f}% uptime)")
                    results[service]['health'] = 'success'
                else:
                    print(f"   ❌ Health failed: {health_data.get('error', 'Unknown error')}")
                    results[service]['health'] = 'failed'
            else:
                print(f"   ❌ Health endpoint failed: {response.status_code}")
                results[service]['health'] = 'failed'
        except Exception as e:
            print(f"   ❌ Health error: {str(e)}")
            results[service]['health'] = 'error'
    
    # Test comprehensive endpoint
    print(f"\n4. Testing comprehensive test endpoint...")
    try:
        response = requests.get(f"{base_url}/test_all_services", timeout=30)
        if response.status_code == 200:
            test_data = response.json()
            if test_data['success']:
                summary = test_data['data']['summary']
                print(f"✅ Comprehensive test completed:")
                print(f"   Total services: {summary['total_services']}")
                print(f"   Successful tests: {summary['successful_tests']}")
                print(f"   Success rate: {summary['success_rate']:.1%}")
            else:
                print(f"❌ Comprehensive test failed: {test_data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Comprehensive test endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Comprehensive test error: {str(e)}")
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = 0
    successful_tests = 0
    
    for service, service_results in results.items():
        print(f"{service}:")
        for test_type, result in service_results.items():
            total_tests += 1
            if result == 'success':
                successful_tests += 1
                print(f"  ✅ {test_type}: {result}")
            else:
                print(f"  ❌ {test_type}: {result}")
    
    success_rate = (successful_tests / total_tests) if total_tests > 0 else 0
    print(f"\nOverall Success Rate: {successful_tests}/{total_tests} ({success_rate:.1%})")
    
    if success_rate >= 0.8:
        print("🎉 TELEMETRY MCP SERVER TEST PASSED!")
        return True
    else:
        print("⚠️  TELEMETRY MCP SERVER TEST NEEDS ATTENTION")
        return False

if __name__ == "__main__":
    success = test_telemetry_mcp()
    exit(0 if success else 1)
