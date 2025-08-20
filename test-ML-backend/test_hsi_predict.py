#!/usr/bin/env python3
"""
HSI Predict API 테스트 스크립트
"""

import requests
import json
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 기본 URL
BASE_URL = "http://localhost:8000"

def test_hsi_predict():
    """HSI Predict API를 테스트합니다."""
    
    # 테스트 데이터
    test_data = {
        "id": "test_meat_001",
        "seqno": 1,
        "isRefrigerated": False
    }
    
    print(f"Testing HSI Predict API with data: {test_data}")
    
    try:
        # POST 요청
        response = requests.post(
            f"{BASE_URL}/hsipredict/",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Message: {result.get('message')}")
            print(f"Predictions: {result.get('predictions')}")
            print(f"XAI Image URLs: {result.get('xai_image_urls')}")
            print(f"Created At: {result.get('created_at')}")
        else:
            print("❌ Failed!")
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_health_check():
    """서버 상태를 확인합니다."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print("❌ Server is not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False

if __name__ == "__main__":
    print("=== HSI Predict API Test ===")
    
    # 서버 상태 확인
    if test_health_check():
        print("\n--- Testing HSI Predict API ---")
        test_hsi_predict()
    else:
        print("Please start the server first:")
        print("cd test-ML-backend")
        print("python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
