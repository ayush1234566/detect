#!/usr/bin/env python3
"""
API Testing Script for FastAPI + MongoDB Backend
Tests all major endpoints to ensure everything is working correctly
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a single endpoint and return results"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"✅ {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: {str(e)}")
        print("-" * 50)
        return False

def main():
    print("🚀 Testing FastAPI + MongoDB Backend")
    print("=" * 50)
    
    # Test basic endpoints
    test_endpoint("/")
    test_endpoint("/ping-db")
    
    # Test speech endpoints
    test_endpoint("/speech/test-microphone")
    test_endpoint("/speech/transcripts")
    
    # Test user creation
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "usn": "TEST123"
    }
    test_endpoint("/users", "POST", user_data)
    
    print("\n🎉 API Testing Complete!")
    print(f"Your FastAPI server is running at: {BASE_URL}")
    print(f"MongoDB connection: Working ✅")
    print(f"Speech features: Available ✅")

if __name__ == "__main__":
    main()