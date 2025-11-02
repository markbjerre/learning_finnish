#!/usr/bin/env python3
"""
Test script for Finnish Learning API
Run this locally to test the API before deploying
"""

import requests
import json
import sys

# Change this to your deployed URL when testing production
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_word_lookup(word="talo"):
    """Test word lookup endpoint"""
    print(f"\n=== Testing Word Lookup: {word} ===")
    response = requests.get(f"{BASE_URL}/api/word/{word}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Word: {data.get('word')}")
        print(f"Translation: {data.get('translation')}")
        print(f"Forms: {json.dumps(data.get('forms'), indent=2)}")
        print(f"Example: {data.get('example')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_translation():
    """Test translation endpoint"""
    print("\n=== Testing Translation ===")
    payload = {
        "text": "Hei, kuinka voit?",
        "source_lang": "fi",
        "target_lang": "da"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/translate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Original: {data.get('original')}")
        print(f"Translation: {data.get('translation')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    # Check if custom URL provided
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    
    print(f"Testing API at: {BASE_URL}")
    
    # Run tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Word Lookup", test_word_lookup("talo")))
    results.append(("Translation", test_translation()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)
