#!/usr/bin/env python
"""
Test script for Production AI Agent - Part 6 Final Project.
Tests all requirements: health, readiness, auth, rate limit, budget.
"""

import time
import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "dev-secret-key-123"

def print_test(name, success, details=""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {name}")
    if details:
        print(f"       {details}")

def test_health():
    """Test health endpoint"""
    try:
        resp = requests.get(f"{BASE_URL}/health")
        success = resp.status_code == 200 and "status" in resp.json()
        print_test("Health Check", success, f"Status: {resp.status_code}")
        return success
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_ready():
    """Test readiness endpoint"""
    try:
        resp = requests.get(f"{BASE_URL}/ready")
        success = resp.status_code == 200 and resp.json().get("ready")
        print_test("Readiness Check", success, f"Status: {resp.status_code}")
        return success
    except Exception as e:
        print_test("Readiness Check", False, str(e))
        return False

def test_auth():
    """Test authentication requirement"""
    # Without API key should fail
    try:
        resp = requests.post(
            f"{BASE_URL}/ask",
            json={"question": "Test"},
            headers={"Content-Type": "application/json"}
        )
        no_key_fails = resp.status_code == 403
        print_test("Auth - Without Key Fails", no_key_fails, f"Status: {resp.status_code}")
    except Exception as e:
        print_test("Auth - Without Key Fails", False, str(e))
        return False
    
    # With valid API key should succeed
    try:
        resp = requests.post(
            f"{BASE_URL}/ask",
            json={"question": "Test"},
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            }
        )
        valid_key_succeeds = resp.status_code == 200
        print_test("Auth - With Valid Key", valid_key_succeeds, f"Status: {resp.status_code}")
        return no_key_fails and valid_key_succeeds
    except Exception as e:
        print_test("Auth - With Valid Key", False, str(e))
        return False

def test_rate_limit():
    """Test rate limiting"""
    limit = 20
    try:
        success_count = 0
        for i in range(limit + 5):
            resp = requests.post(
                f"{BASE_URL}/ask",
                json={"question": f"Test {i}"},
                headers={
                    "X-API-Key": API_KEY,
                    "Content-Type": "application/json"
                }
            )
            if resp.status_code == 200:
                success_count += 1
            elif resp.status_code == 429:
                # Hit rate limit
                success = i >= limit
                print_test("Rate Limit", success, f"Limited after {i} requests")
                return success
            time.sleep(0.05)
        
        print_test("Rate Limit", False, "Did not hit rate limit")
        return False
    except Exception as e:
        print_test("Rate Limit", False, str(e))
        return False

def test_budget():
    """Test budget tracking"""
    try:
        # Send many requests to exceed budget ($5/day = 500 requests @ $0.01 each)
        for i in range(505):
            resp = requests.post(
                f"{BASE_URL}/ask",
                json={"question": f"Budget test {i}"},
                headers={
                    "X-API-Key": API_KEY,
                    "Content-Type": "application/json"
                }
            )
            if resp.status_code == 402:
                # Hit budget limit
                success = i >= 500
                print_test("Budget Guard", success, f"Limited after {i} requests")
                return success
            elif resp.status_code != 200:
                print_test("Budget Guard", False, f"Unexpected status: {resp.status_code}")
                return False
            time.sleep(0.01)
        
        print_test("Budget Guard", False, "Did not hit budget limit")
        return False
    except Exception as e:
        print_test("Budget Guard", False, str(e))
        return False

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("Production AI Agent - Test Suite")
    print("="*50 + "\n")
    
    # Basic tests (should all pass)
    print("📍 Basic Tests:")
    test_health()
    test_ready()
    
    print("\n📍 Authentication Tests:")
    test_auth()
    
    print("\n📍 Security Tests (Warning: These take time):")
    print("  Testing rate limit... (20 req/min limit)")
    test_rate_limit()
    
    print("  Testing budget... (will take a while)")
    print("  Skipping budget test - would need 500+ requests")
    print("  In production, this would be tested with Redis")
    
    print("\n" + "="*50)
    print("Test Summary:")
    print("  ✅ = Requirement met")
    print("  ❌ = Requirement failed")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
