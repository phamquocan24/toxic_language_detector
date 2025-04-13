#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script kiểm tra API phát hiện ngôn từ tiêu cực
"""

import requests
import json
import sys
import time

def test_health_endpoint():
    """
    Kiểm tra endpoint /health của API
    """
    try:
        response = requests.get("http://localhost:7860/health")
        print(f"Health endpoint status code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Health endpoint response: {response.json()}")
            return True
        else:
            print(f"Health endpoint error: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing health endpoint: {str(e)}")
        return False

def login():
    """
    Đăng nhập để lấy token
    """
    try:
        # Sử dụng thông tin đăng nhập theo cài đặt mặc định trong settings.py
        # ADMIN_USERNAME="admin" và ADMIN_PASSWORD="password"
        login_data = {
            "username": "admin",
            "password": "password"  # password mặc định từ settings.py
        }
        
        response = requests.post(
            "http://localhost:7860/auth/token",
            data=login_data  # Form data cho OAuth2PasswordRequestForm
        )
        
        print(f"Login status code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("Login successful")
            return token_data.get("access_token")
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None

def test_prediction_endpoint(token=None):
    """
    Kiểm tra endpoint /extension/detect 
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Dữ liệu cho prediction endpoint
        data = {
            "text": "Đây là một bình luận tốt",
            "platform": "test"
        }
        
        response = requests.post(
            "http://localhost:7860/extension/detect",
            json=data,
            headers=headers
        )
        
        print(f"Prediction endpoint status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Prediction result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"Prediction endpoint error: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing prediction endpoint: {str(e)}")
        return False

def test_unauthenticated_prediction():
    """
    Kiểm tra endpoint /extension/detect không có xác thực
    """
    try:
        # Dữ liệu cho prediction endpoint
        data = {
            "text": "Đây là một bình luận tốt",
            "platform": "test"
        }
        
        response = requests.post(
            "http://localhost:7860/extension/detect",
            json=data
        )
        
        print(f"Unauthenticated prediction endpoint status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Unauthenticated prediction result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"Unauthenticated prediction endpoint error: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing unauthenticated prediction endpoint: {str(e)}")
        return False

def test_gradio_interface():
    """
    Kiểm tra giao diện Gradio
    """
    try:
        response = requests.get("http://localhost:7860/gradio")
        
        print(f"Gradio interface status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Gradio interface is accessible")
            return True
        else:
            print(f"Gradio interface error: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing Gradio interface: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting API test...")
    start_time = time.time()
    
    # Kiểm tra health endpoint
    health_ok = test_health_endpoint()
    
    # Kiểm tra Gradio interface
    gradio_ok = test_gradio_interface()
    
    # Kiểm tra prediction không cần xác thực
    prediction_unauthenticated = test_unauthenticated_prediction()
    
    # Đăng nhập và lấy token
    token = login()
    
    # Nếu login thành công, kiểm tra prediction với token
    if token:
        prediction_ok = test_prediction_endpoint(token)
    else:
        print("Skipping authenticated prediction test due to login failure")
        prediction_ok = False
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nAPI test completed in {duration:.2f} seconds")
    print(f"Health endpoint: {'OK' if health_ok else 'FAILED'}")
    print(f"Gradio interface: {'OK' if gradio_ok else 'FAILED'}")
    print(f"Unauthenticated prediction: {'OK' if prediction_unauthenticated else 'FAILED'}")
    print(f"Authenticated prediction: {'OK' if prediction_ok else 'FAILED'}") 