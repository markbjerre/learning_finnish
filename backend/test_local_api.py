"""
Test script for Finnish Learning API
Tests all endpoints and shows requests/responses
"""

import requests
import json
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

BASE_URL = "http://localhost:5003"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"{Fore.CYAN}{Style.BRIGHT}{title}")
    print("="*80)

def print_request(method, endpoint, data=None):
    """Print request details"""
    print(f"\n{Fore.YELLOW}📤 REQUEST:")
    print(f"{Fore.GREEN}{method} {BASE_URL}{endpoint}")
    if data:
        print(f"{Fore.YELLOW}Body:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

def print_response(response):
    """Print response details"""
    print(f"\n{Fore.YELLOW}📥 RESPONSE:")
    print(f"{Fore.BLUE}Status Code: {response.status_code}")
    print(f"{Fore.BLUE}Headers:")
    for key, value in response.headers.items():
        if key.lower() in ['content-type', 'content-length']:
            print(f"  {key}: {value}")
    
    try:
        data = response.json()
        print(f"{Fore.YELLOW}Body:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(f"{Fore.YELLOW}Body (text):")
        print(response.text)

def test_health():
    """Test health check endpoint"""
    print_section("TEST 1: Health Check")
    
    endpoint = "/health"
    print_request("GET", endpoint)
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print_response(response)
        
        if response.status_code == 200:
            print(f"\n{Fore.GREEN}✅ Health check PASSED")
        else:
            print(f"\n{Fore.RED}❌ Health check FAILED")
    except Exception as e:
        print(f"\n{Fore.RED}❌ ERROR: {str(e)}")

def test_word_lookup(word):
    """Test word lookup endpoint"""
    print_section(f"TEST 2: Word Lookup - '{word}'")
    
    endpoint = f"/api/word/{word}"
    params = "?source_lang=fi&target_lang=da"
    print_request("GET", endpoint + params)
    
    try:
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            params={"source_lang": "fi", "target_lang": "da"}
        )
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n{Fore.GREEN}✅ Word lookup PASSED")
            print(f"\n{Fore.MAGENTA}Key Information:")
            print(f"  Word: {data.get('word')}")
            print(f"  Translation: {data.get('translation')}")
            print(f"  Part of Speech: {data.get('partOfSpeech')}")
            print(f"  Pronunciation: {data.get('pronunciation')}")
            if data.get('forms'):
                print(f"  Forms: {list(data.get('forms').keys())}")
            print(f"  Example: {data.get('example')}")
        else:
            print(f"\n{Fore.RED}❌ Word lookup FAILED")
    except Exception as e:
        print(f"\n{Fore.RED}❌ ERROR: {str(e)}")

def test_translation():
    """Test translation endpoint"""
    print_section("TEST 3: Translation")
    
    endpoint = "/api/translate"
    data = {
        "text": "Hei, kuinka voit?",
        "source_lang": "fi",
        "target_lang": "da"
    }
    
    print_request("POST", endpoint, data)
    
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=data
        )
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n{Fore.GREEN}✅ Translation PASSED")
            print(f"\n{Fore.MAGENTA}Translation Result:")
            print(f"  Original: {result.get('original')}")
            print(f"  Translation: {result.get('translation')}")
        else:
            print(f"\n{Fore.RED}❌ Translation FAILED")
    except Exception as e:
        print(f"\n{Fore.RED}❌ ERROR: {str(e)}")

def test_multiple_words():
    """Test multiple word lookups"""
    print_section("TEST 4: Multiple Word Lookups")
    
    words = ["talo", "kissa", "kirja"]
    results = []
    
    for word in words:
        print(f"\n{Fore.CYAN}Testing word: {word}")
        endpoint = f"/api/word/{word}"
        print_request("GET", endpoint)
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "word": word,
                    "translation": data.get("translation"),
                    "status": "✅"
                })
                print(f"{Fore.GREEN}✅ {word} -> {data.get('translation')}")
            else:
                results.append({
                    "word": word,
                    "translation": "Error",
                    "status": "❌"
                })
                print(f"{Fore.RED}❌ Failed")
        except Exception as e:
            print(f"{Fore.RED}❌ ERROR: {str(e)}")
    
    print(f"\n{Fore.YELLOW}Summary:")
    for result in results:
        print(f"  {result['status']} {result['word']} -> {result['translation']}")

def main():
    """Run all tests"""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║        Finnish Learning API Test Suite                         ║")
    print("║        Testing: http://localhost:5003                          ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    # Test 1: Health check
    test_health()
    
    # Test 2: Word lookup
    test_word_lookup("talo")
    
    # Test 3: Translation
    test_translation()
    
    # Test 4: Multiple words
    test_multiple_words()
    
    print_section("All Tests Complete!")
    print(f"\n{Fore.CYAN}Note: AI responses may vary slightly between runs.")
    print(f"{Fore.CYAN}Check that the structure and content are reasonable.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Tests interrupted by user.")
    except Exception as e:
        print(f"\n\n{Fore.RED}Unexpected error: {str(e)}")
