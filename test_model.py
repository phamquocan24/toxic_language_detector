"""
Test script for the Vietnamese Toxic Language Detector API
"""
import requests
import json

def test_api():
    url = "http://localhost:7860/api/v1/detect"
    
    # Test with offensive text
    offensive_text = "Đồ khốn kiếp, tao ghét mày lắm"
    
    # Test with normal text
    normal_text = "Hôm nay là một ngày đẹp trời"
    
    # Test with spam text
    spam_text = "GIẢM GIÁ 50% MUA NGAY!!! KHUYẾN MÃI LỚN NHẤT NĂM!!!"
    
    # Prepare the request
    headers = {
        "Content-Type": "application/json"
    }
    
    # Test each type of text
    for text, text_type in [
        (offensive_text, "offensive"), 
        (normal_text, "normal"),
        (spam_text, "spam")
    ]:
        print(f"\nTesting {text_type} text: {text}")
        
        payload = {
            "text": text
        }
        
        # Make the request
        response = requests.post(url, headers=headers, json=payload)
        
        # Print the status code
        print(f"Status code: {response.status_code}")
        
        # Print the response
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    test_api() 