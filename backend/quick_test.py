#!/usr/bin/env python3
"""
Quick test to verify caching is working
"""
import requests
import json

BASE_URL = "http://localhost:5003"

def test_cache():
    word = "kissa"
    
    print("=" * 80)
    print("TESTING CACHE - Checking server logs")
    print("=" * 80)
    
    # Request 1
    print(f"\n[REQUEST 1] Getting {word}...")
    r1 = requests.get(f"{BASE_URL}/api/word/{word}")
    data1 = r1.json()
    
    timing1 = data1.get("_timing", {})
    print(f"Response Status: {r1.status_code}")
    print(f"Cached: {timing1.get('cached', 'N/A')}")
    print(f"Total Time: {timing1.get('total_ms', 'N/A')} ms")
    print(f"OpenAI API Time: {timing1.get('openai_api_ms', 'N/A')} ms")
    
    # Request 2 - should be cached
    print(f"\n[REQUEST 2] Getting {word} again (should be cached)...")
    r2 = requests.get(f"{BASE_URL}/api/word/{word}")
    data2 = r2.json()
    
    timing2 = data2.get("_timing", {})
    print(f"Response Status: {r2.status_code}")
    print(f"Cached: {timing2.get('cached', 'N/A')}")
    print(f"Total Time: {timing2.get('total_ms', 'N/A')} ms")
    print(f"Cache Lookup Time: {timing2.get('cache_lookup_ms', 'N/A')} ms")
    
    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    if timing1.get('cached') == False and timing2.get('cached') == True:
        speedup = timing1.get('total_ms', 0) / timing2.get('total_ms', 1)
        print(f"SUCCESS: Caching works!")
        print(f"First request: {timing1.get('total_ms')} ms (OpenAI call)")
        print(f"Second request: {timing2.get('total_ms')} ms (from cache)")
        print(f"Speedup: {speedup:.1f}x faster")
        if timing2.get('total_ms', 100) < 100:
            print("EXCELLENT: Cached response is sub-100ms!")
    else:
        print("ISSUE: Cache may not be working properly")
        print(f"Request 1 cached: {timing1.get('cached')}")
        print(f"Request 2 cached: {timing2.get('cached')}")
        
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_cache()
