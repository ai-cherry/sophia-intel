#!/usr/bin/env python3
"""
Comprehensive Test Suite for Sophia Hybrid MCP System
"""

import requests
import json
import time
import os
import subprocess
import signal
from pathlib import Path

class TestColors:
    """ANSI color codes for pretty output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{TestColors.BOLD}{TestColors.BLUE}{'=' * 60}{TestColors.END}")
    print(f"{TestColors.BOLD}{TestColors.BLUE}{text}{TestColors.END}")
    print(f"{TestColors.BOLD}{TestColors.BLUE}{'=' * 60}{TestColors.END}")

def print_test(test_name, result, details=""):
    if result:
        status = f"{TestColors.GREEN}✅ PASS{TestColors.END}"
    else:
        status = f"{TestColors.RED}❌ FAIL{TestColors.END}"
    
    print(f"{status} {test_name}")
    if details:
        print(f"    {TestColors.YELLOW}{details}{TestColors.END}")

def start_servers():
    """Start both cloud and local servers"""
    print_header("🚀 Starting Servers")
    
    # Start cloud server
    print("Starting cloud server...")
    cloud_proc = subprocess.Popen(
        ["python3", "cloud-server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)  # Wait for startup
    
    # Start local bridge
    print("Starting local bridge...")
    local_proc = subprocess.Popen(
        ["python3", "local-bridge.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)  # Wait for startup
    
    return cloud_proc, local_proc

def test_cloud_server():
    """Test cloud server endpoints"""
    print_header("☁️  Testing Cloud Server")
    
    base_url = "http://localhost:8080"
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health check
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/", timeout=2)
        test_pass = response.status_code == 200
        data = response.json()
        print_test("Health Check", test_pass, f"Status: {data.get('status')}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)[:50]}")
    
    # Test 2: Compute embedding
    tests_total += 1
    try:
        response = requests.post(
            f"{base_url}/compute/embedding",
            json={"text": "Test content for embedding"}
        )
        test_pass = response.status_code == 200
        data = response.json()
        print_test("Compute Embedding", test_pass, 
                  f"Cached: {data.get('cached')}, Hash: {data.get('hash')}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Compute Embedding", False, f"Error: {str(e)[:50]}")
    
    # Test 3: Deduplication check
    tests_total += 1
    try:
        response = requests.post(
            f"{base_url}/dedup/check",
            json={"content": "Test content for deduplication", "threshold": 0.8}
        )
        test_pass = response.status_code == 200
        data = response.json()
        print_test("Deduplication Check", test_pass,
                  f"Duplicate: {data.get('is_duplicate')}, Similarity: {data.get('similarity', 0):.2f}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Deduplication Check", False, f"Error: {str(e)[:50]}")
    
    # Test 4: Statistics
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/stats")
        test_pass = response.status_code == 200
        data = response.json()
        print_test("Statistics Endpoint", test_pass,
                  f"Efficiency: {data.get('efficiency', 'N/A')}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Statistics Endpoint", False, f"Error: {str(e)[:50]}")
    
    return tests_passed, tests_total

def test_local_bridge():
    """Test local bridge endpoints"""
    print_header("🌉 Testing Local Bridge")
    
    base_url = "http://localhost:8000"
    tests_passed = 0
    tests_total = 0
    
    # Create test file
    test_file = Path.home() / "Projects" / "test-mcp.txt"
    test_file.write_text("This is test content for MCP system")
    
    # Test 1: Health check
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/", timeout=2)
        test_pass = response.status_code == 200
        data = response.json()
        print_test("Health Check", test_pass, f"Mode: {data.get('mode')}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)[:50]}")
    
    # Test 2: Read file
    tests_total += 1
    try:
        response = requests.post(
            f"{base_url}/mcp/tool/read_file",
            json={"path": str(test_file)}
        )
        test_pass = response.status_code == 200
        data = response.json()
        print_test("Read File", test_pass,
                  f"Size: {data.get('size')} bytes, Duplicate: {data.get('is_duplicate')}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Read File", False, f"Error: {str(e)[:50]}")
    
    # Test 3: List files
    tests_total += 1
    try:
        response = requests.post(
            f"{base_url}/mcp/tool/list_files",
            json={"directory": "~/Projects"}
        )
        test_pass = response.status_code == 200
        data = response.json()
        print_test("List Files", test_pass,
                  f"Found {data.get('count', 0)} files")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("List Files", False, f"Error: {str(e)[:50]}")
    
    # Test 4: Check duplication
    tests_total += 1
    try:
        response = requests.post(
            f"{base_url}/mcp/tool/check_duplication",
            json={"content": "Test content for dedup"}
        )
        test_pass = response.status_code == 200
        data = response.json()
        print_test("Check Duplication", test_pass,
                  f"Cache size: {data.get('cache_size')}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Check Duplication", False, f"Error: {str(e)[:50]}")
    
    # Test 5: Statistics
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/stats")
        test_pass = response.status_code == 200
        data = response.json()
        stats = data.get('stats', {})
        print_test("Statistics", test_pass,
                  f"Files read: {stats.get('files_read')}, Duplicates: {stats.get('duplicates_found')}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Statistics", False, f"Error: {str(e)[:50]}")
    
    # Cleanup
    if test_file.exists():
        test_file.unlink()
    
    return tests_passed, tests_total

def test_deduplication():
    """Test deduplication functionality"""
    print_header("🔍 Testing Deduplication Logic")
    
    base_url = "http://localhost:8000"
    tests_passed = 0
    tests_total = 0
    
    # Create test files with duplicate content
    test_dir = Path.home() / "Projects"
    file1 = test_dir / "dup-test-1.txt"
    file2 = test_dir / "dup-test-2.txt"
    file3 = test_dir / "unique-test.txt"
    
    duplicate_content = "This is duplicate content for testing deduplication"
    unique_content = "This is unique content that should not be flagged as duplicate"
    
    file1.write_text(duplicate_content)
    file2.write_text(duplicate_content)
    file3.write_text(unique_content)
    
    # Test reading duplicate files
    tests_total += 1
    try:
        # Read first file
        response1 = requests.post(
            f"{base_url}/mcp/tool/read_file",
            json={"path": str(file1)}
        )
        data1 = response1.json()
        
        # Read duplicate file
        response2 = requests.post(
            f"{base_url}/mcp/tool/read_file",
            json={"path": str(file2)}
        )
        data2 = response2.json()
        
        test_pass = data1.get('is_duplicate') == False and data2.get('is_duplicate') == True
        print_test("Duplicate Detection", test_pass,
                  f"First: {data1.get('is_duplicate')}, Second: {data2.get('is_duplicate')}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Duplicate Detection", False, f"Error: {str(e)[:50]}")
    
    # Test unique content
    tests_total += 1
    try:
        response3 = requests.post(
            f"{base_url}/mcp/tool/read_file",
            json={"path": str(file3)}
        )
        data3 = response3.json()
        test_pass = data3.get('is_duplicate') == False
        print_test("Unique Content Detection", test_pass,
                  f"Is duplicate: {data3.get('is_duplicate')}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Unique Content Detection", False, f"Error: {str(e)[:50]}")
    
    # Get final stats
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/stats")
        data = response.json()
        stats = data.get('stats', {})
        dedup_percentage = data.get('dedup_percentage', '0%')
        
        test_pass = stats.get('duplicates_found', 0) > 0
        print_test("Deduplication Statistics", test_pass,
                  f"Dedup rate: {dedup_percentage}, Total duplicates: {stats.get('duplicates_found')}")
        if test_pass:
            tests_passed += 1
    except Exception as e:
        print_test("Deduplication Statistics", False, f"Error: {str(e)[:50]}")
    
    # Cleanup
    for f in [file1, file2, file3]:
        if f.exists():
            f.unlink()
    
    return tests_passed, tests_total

def main():
    """Run all tests"""
    print_header("🧪 Sophia Intel Hybrid MCP System Test Suite")
    
    # Track overall results
    total_passed = 0
    total_tests = 0
    
    # Start servers
    cloud_proc = None
    local_proc = None
    
    try:
        cloud_proc, local_proc = start_servers()
        print(f"{TestColors.GREEN}✅ Servers started{TestColors.END}")
        
        # Run test suites
        passed, total = test_cloud_server()
        total_passed += passed
        total_tests += total
        
        passed, total = test_local_bridge()
        total_passed += passed
        total_tests += total
        
        passed, total = test_deduplication()
        total_passed += passed
        total_tests += total
        
        # Final summary
        print_header("📊 Test Summary")
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        if success_rate == 100:
            color = TestColors.GREEN
            status = "ALL TESTS PASSED! 🎉"
        elif success_rate >= 70:
            color = TestColors.YELLOW
            status = "MOSTLY PASSING"
        else:
            color = TestColors.RED
            status = "NEEDS ATTENTION"
        
        print(f"{color}{TestColors.BOLD}")
        print(f"Tests Passed: {total_passed}/{total_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Status: {status}")
        print(f"{TestColors.END}")
        
        if success_rate == 100:
            print(f"\n{TestColors.GREEN}✅ Your Sophia Intel Hybrid MCP System is fully operational!{TestColors.END}")
            print("The deduplication system is preventing information bloat successfully.")
        
    except KeyboardInterrupt:
        print(f"\n{TestColors.YELLOW}Test interrupted by user{TestColors.END}")
    
    finally:
        # Cleanup: terminate servers
        if cloud_proc:
            cloud_proc.terminate()
            cloud_proc.wait(timeout=2)
        if local_proc:
            local_proc.terminate()
            local_proc.wait(timeout=2)
        print(f"\n{TestColors.BLUE}Servers stopped{TestColors.END}")

if __name__ == "__main__":
    main()
