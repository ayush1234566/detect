#!/usr/bin/env python3
"""
Login Testing Script for FastAPI + MongoDB Backend
Tests student signup and login functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_student_signup():
    """Test student signup"""
    print("🔵 Testing Student Signup...")
    
    student_data = {
        "usn": "TEST123456",
        "name": "Test Student",
        "email": "test.student@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/signup/student", json=student_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_create_classroom():
    """Create a test classroom for login testing"""
    print("🔵 Creating Test Classroom...")
    
    # First create a faculty member
    faculty_data = {
        "teacher_code": "TCH001",
        "name": "Test Teacher",
        "email": "teacher@example.com",
        "subject": "Computer Science"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/signup/faculty", json=faculty_data)
        print(f"   Faculty Creation Status: {response.status_code}")
    except Exception as e:
        print(f"   Faculty Creation Error: {e}")
    
    # Create classroom
    classroom_data = {
        "classroom_id": "CS101",
        "teacher_code": "TCH001",
        "college_name": "Test College",
        "subject": "Computer Science",
        "max_students": 50
    }
    
    try:
        response = requests.post(f"{BASE_URL}/create_class", json=classroom_data)
        print(f"   Classroom Creation Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"   ❌ Classroom Creation Error: {e}")
        return False

def test_student_login():
    """Test student login"""
    print("🔵 Testing Student Login...")
    
    login_data = {
        "usn": "TEST123456",
        "classroom_id": "CS101"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/student", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_wrong_login():
    """Test login with wrong credentials"""
    print("🔵 Testing Wrong Login Credentials...")
    
    login_data = {
        "usn": "WRONG123",
        "classroom_id": "CS101"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/student", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 401  # Should fail with 401
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🚀 Testing Login Functionality with MongoDB")
    print("=" * 50)
    
    # Test MongoDB connection first
    try:
        response = requests.get(f"{BASE_URL}/ping-db")
        if response.status_code == 200:
            print("✅ MongoDB Connection: Working")
        else:
            print("❌ MongoDB Connection: Failed")
            return
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")
        return
    
    print("-" * 50)
    
    # Run tests
    signup_success = test_student_signup()
    classroom_success = test_create_classroom()
    login_success = test_student_login()
    wrong_login_success = test_wrong_login()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Student Signup: {'✅ Pass' if signup_success else '❌ Fail'}")
    print(f"   Classroom Creation: {'✅ Pass' if classroom_success else '❌ Fail'}")
    print(f"   Valid Login: {'✅ Pass' if login_success else '❌ Fail'}")
    print(f"   Invalid Login: {'✅ Pass' if wrong_login_success else '❌ Fail'}")
    
    if all([signup_success, classroom_success, login_success, wrong_login_success]):
        print("\n🎉 All login tests passed! System is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()