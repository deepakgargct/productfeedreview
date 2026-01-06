#!/usr/bin/env python
"""
Test script for the enhanced API endpoints
"""

import requests
import json

API_BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_single_validation():
    """Test single product validation"""
    print("\nTesting /api/validate endpoint...")
    
    product = {
        "product_id": "TEST001",
        "title": "Test Product - Wireless Headphones",
        "description": "High-quality wireless headphones with noise cancellation",
        "price": 99.99,
        "currency": "USD",
        "category": "electronics",
        "availability": "in_stock",
        "image_url": "https://example.com/product.jpg",
        "product_url": "https://example.com/products/headphones"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/validate",
            json=product,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Compliance Score: {result.get('compliance_percentage')}")
        print(f"Critical Issues: {result.get('summary', {}).get('total_critical', 0)}")
        print(f"Valid: {result.get('valid')}")
        print(f"Response: {json.dumps(result, indent=2)[:500]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_batch_validation():
    """Test batch product validation"""
    print("\nTesting /api/validate-feed endpoint...")
    
    products = [
        {
            "product_id": "BATCH001",
            "title": "Product 1 - Valid",
            "description": "This is a valid product with all required fields",
            "price": 49.99,
            "currency": "USD",
            "category": "electronics",
            "availability": "in_stock"
        },
        {
            "product_id": "BATCH002",
            "title": "Short",  # Too short
            "description": "Bad",  # Too short
            "price": -10,  # Invalid
            "currency": "INVALID",
            "category": "unknown",
            "availability": "maybe"
        }
    ]
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/validate-feed",
            json=products,
            timeout=15
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Total Products: {result.get('batch_summary', {}).get('total_products')}")
        print(f"Compliant: {result.get('batch_summary', {}).get('compliant_products')}")
        print(f"Compliance Rate: {result.get('batch_summary', {}).get('compliance_rate')}")
        print(f"Response: {json.dumps(result, indent=2)[:500]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_api_info():
    """Test API info endpoint"""
    print("\nTesting /api/info endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/info", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("API Testing Suite for Enhanced Product Feed Validator")
    print("=" * 60)
    
    print("\nIMPORTANT: Make sure the API server is running!")
    print("Start it with: python api_server.py\n")
    
    input("Press Enter to start tests...")
    
    results = {
        "health_check": test_health_check(),
        "single_validation": test_single_validation(),
        "batch_validation": test_batch_validation(),
        "api_info": test_api_info()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
