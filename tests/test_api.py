# tests/test_api.py
import requests
import json
import sys
import os
from typing import Dict, Any

# Base URL của API
BASE_URL = "http://localhost:7860"  # Thay đổi nếu cần

# Biến lưu trữ token
ACCESS_TOKEN = None

def log_response(response, message="Response"):
    """Log response từ API"""
    print(f"\n=== {message} ===")
    print(f"Status code: {response.status_code}")
    
    try:
        json_data = response.json()
        print(f"Response data: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response text: {response.text}")

def login(username: str, password: str) -> bool:
    """
    Đăng nhập để lấy token
    
    Args:
        username: Tên đăng nhập
        password: Mật khẩu
    
    Returns:
        bool: True nếu đăng nhập thành công, False nếu thất bại
    """
    global ACCESS_TOKEN
    
    url = f"{BASE_URL}/auth/token"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, data=data)
    log_response(response, "Login Response")
    
    if response.status_code == 200:
        token_data = response.json()
        ACCESS_TOKEN = token_data.get("access_token")
        print(f"Login successful. User role: {token_data.get('role')}")
        return True
    else:
        print(f"Login failed: {response.text}")
        return False

def get_users():
    """Lấy danh sách người dùng"""
    if not ACCESS_TOKEN:
        print("ERROR: Missing access token. Please login first.")
        return
    
    url = f"{BASE_URL}/admin/users"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    log_response(response, "Get Users Response")
    
    if response.status_code == 200:
        users = response.json()
        print(f"Successfully retrieved {len(users)} users")
        
        # Kiểm tra xem mỗi người dùng có thuộc tính 'role' là string không
        all_roles_are_strings = all(isinstance(user.get("role"), str) for user in users)
        if all_roles_are_strings:
            print("✅ All user roles are strings - Fix is working correctly")
        else:
            print("❌ Some user roles are not strings - Fix is NOT working")
    else:
        print(f"Failed to get users: {response.text}")

def get_user_by_id(user_id: int):
    """Lấy thông tin người dùng theo ID"""
    if not ACCESS_TOKEN:
        print("ERROR: Missing access token. Please login first.")
        return
    
    url = f"{BASE_URL}/admin/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    log_response(response, f"Get User {user_id} Response")
    
    if response.status_code == 200:
        user = response.json()
        print(f"Successfully retrieved user: {user.get('username')}")
        
        # Kiểm tra xem thuộc tính 'role' có phải là string không
        if isinstance(user.get("role"), str):
            print(f"✅ User role is a string ('{user.get('role')}') - Fix is working correctly")
        else:
            print(f"❌ User role is not a string - Fix is NOT working")
    else:
        print(f"Failed to get user: {response.text}")

def create_user(user_data: Dict[str, Any]):
    """Tạo người dùng mới"""
    if not ACCESS_TOKEN:
        print("ERROR: Missing access token. Please login first.")
        return
    
    url = f"{BASE_URL}/admin/users"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=user_data, headers=headers)
    log_response(response, "Create User Response")
    
    if response.status_code == 201:
        user = response.json()
        print(f"Successfully created user: {user.get('username')}")
        
        # Kiểm tra xem thuộc tính 'role' có phải là string không
        if isinstance(user.get("role"), str):
            print(f"✅ User role is a string ('{user.get('role')}') - Fix is working correctly")
        else:
            print(f"❌ User role is not a string - Fix is NOT working")
            
        return user.get("id")
    else:
        print(f"Failed to create user: {response.text}")
        return None

def update_user(user_id: int, update_data: Dict[str, Any]):
    """Cập nhật thông tin người dùng"""
    if not ACCESS_TOKEN:
        print("ERROR: Missing access token. Please login first.")
        return
    
    url = f"{BASE_URL}/admin/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(url, json=update_data, headers=headers)
    log_response(response, f"Update User {user_id} Response")
    
    if response.status_code == 200:
        user = response.json()
        print(f"Successfully updated user: {user.get('username')}")
        
        # Kiểm tra xem thuộc tính 'role' có phải là string không
        if isinstance(user.get("role"), str):
            print(f"✅ User role is a string ('{user.get('role')}') - Fix is working correctly")
        else:
            print(f"❌ User role is not a string - Fix is NOT working")
    else:
        print(f"Failed to update user: {response.text}")

def get_my_profile():
    """Lấy thông tin profile của người dùng hiện tại"""
    if not ACCESS_TOKEN:
        print("ERROR: Missing access token. Please login first.")
        return
    
    url = f"{BASE_URL}/auth/me"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    log_response(response, "My Profile Response")
    
    if response.status_code == 200:
        user = response.json()
        print(f"Successfully retrieved profile: {user.get('username')}")
        
        # Kiểm tra xem thuộc tính 'role' có phải là string không
        if isinstance(user.get("role"), str):
            print(f"✅ User role is a string ('{user.get('role')}') - Fix is working correctly")
        else:
            print(f"❌ User role is not a string - Fix is NOT working")
    else:
        print(f"Failed to get profile: {response.text}")

def run_tests():
    """Chạy tất cả các test"""
    # Đăng nhập với tài khoản admin
    if not login("admin", "password"):
        print("Cannot continue tests without admin access")
        return
    
    # Lấy danh sách người dùng
    get_users()
    
    # Lấy thông tin admin (id = 1)
    get_user_by_id(1)
    
    # Tạo người dùng mới
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "name": "Test User",
        "password": "password123",
        "confirm_password": "password123",
        "role": "user"
    }
    new_user_id = create_user(user_data)
    
    if new_user_id:
        # Cập nhật người dùng
        update_data = {
            "name": "Updated Test User",
            "role": "user"
        }
        update_user(new_user_id, update_data)
    
    # Lấy profile của mình
    get_my_profile()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    print("=== Starting API Test Script ===")
    run_tests()