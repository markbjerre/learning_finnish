"""
Speed test script for Finnish Learning API
Measures timing at word entry
"""

import requests
import time
import json
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:5003"

def test_word_speed(word):
    """Test word lookup speed with detailed timing"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}Testing word: '{word}'")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    # Measure total request time (includes network + processing)
    request_start = time.time()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/word/{word}",
            params={"source_lang": "fi", "target_lang": "da"}
        )
        
        request_end = time.time()
        total_request_time = (request_end - request_start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract timing info from response
            timing = data.get('_timing', {})
            
            print(f"{Fore.GREEN}✅ Request successful\n")
            
            print(f"{Fore.YELLOW}⏱️  TIMING BREAKDOWN:")
            print(f"{Fore.WHITE}{'─'*80}")
            print(f"{Fore.CYAN}1. Client Request Time:      {Fore.WHITE}{total_request_time:>8.2f} ms {Fore.BLUE}(Network + Server)")
            
            if timing:
                print(f"\n{Fore.MAGENTA}Server-side breakdown:")
                print(f"{Fore.WHITE}{'─'*80}")
                print(f"{Fore.CYAN}   - Prompt Building:        {Fore.WHITE}{timing.get('prompt_build_ms', 0):>8.2f} ms")
                print(f"{Fore.CYAN}   - OpenAI API Call:        {Fore.WHITE}{timing.get('openai_api_ms', 0):>8.2f} ms {Fore.RED}← Main bottleneck")
                print(f"{Fore.CYAN}   - JSON Parsing:           {Fore.WHITE}{timing.get('parse_ms', 0):>8.2f} ms")
                print(f"{Fore.WHITE}{'─'*80}")
                print(f"{Fore.CYAN}   Total Server Time:        {Fore.WHITE}{timing.get('total_ms', 0):>8.2f} ms")
                
                network_overhead = total_request_time - timing.get('total_ms', 0)
                print(f"{Fore.CYAN}   Network Overhead:         {Fore.WHITE}{network_overhead:>8.2f} ms")
            
            print(f"\n{Fore.GREEN}{'─'*80}")
            print(f"{Fore.GREEN}TOTAL TIME (End-to-End):     {Fore.WHITE}{total_request_time:>8.2f} ms")
            print(f"{Fore.GREEN}{'─'*80}")
            
            # Show word data
            print(f"\n{Fore.YELLOW}📚 RESULT:")
            print(f"{Fore.WHITE}Word:        {data.get('word')}")
            print(f"{Fore.WHITE}Translation: {data.get('translation')}")
            print(f"{Fore.WHITE}Pronunciation: {data.get('pronunciation')}")
            
            # Performance assessment
            print(f"\n{Fore.YELLOW}📊 ASSESSMENT:")
            if total_request_time < 1000:
                print(f"{Fore.GREEN}⚡ Excellent - Very fast response!")
            elif total_request_time < 2000:
                print(f"{Fore.CYAN}👍 Good - Acceptable response time")
            elif total_request_time < 3000:
                print(f"{Fore.YELLOW}⚠️  Moderate - Slightly slow")
            else:
                print(f"{Fore.RED}🐌 Slow - Consider optimization")
            
            print(f"\n{Fore.BLUE}💡 NOTE: OpenAI API call typically takes 1-3 seconds")
            print(f"{Fore.BLUE}   This is the expected behavior for AI-generated content.")
            
        else:
            print(f"{Fore.RED}❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"{Fore.RED}❌ ERROR: {str(e)}")

def test_multiple_words():
    """Test multiple words and show average timing"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*80}")
    print(f"MULTIPLE WORD SPEED TEST")
    print(f"{'='*80}\n")
    
    words = ["talo", "kissa", "kirja", "vesi", "auto"]
    times = []
    
    for word in words:
        start = time.time()
        try:
            response = requests.get(f"{BASE_URL}/api/word/{word}")
            end = time.time()
            elapsed = (end - start) * 1000
            times.append(elapsed)
            
            if response.status_code == 200:
                data = response.json()
                server_time = data.get('_timing', {}).get('total_ms', 0)
                print(f"{Fore.GREEN}✅ {word:10} - {elapsed:7.2f} ms (Server: {server_time:7.2f} ms)")
            else:
                print(f"{Fore.RED}❌ {word:10} - Failed")
        except Exception as e:
            print(f"{Fore.RED}❌ {word:10} - Error: {str(e)}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n{Fore.YELLOW}{'─'*80}")
        print(f"{Fore.CYAN}STATISTICS:")
        print(f"{Fore.WHITE}Average: {avg_time:7.2f} ms")
        print(f"{Fore.WHITE}Fastest: {min_time:7.2f} ms")
        print(f"{Fore.WHITE}Slowest: {max_time:7.2f} ms")

def test_cache_performance():
    """Test cache performance - should be milliseconds!"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*80}")
    print(f"CACHE PERFORMANCE TEST")
    print(f"{'='*80}\n")
    
    word = "talo"
    
    # First call - cold (no cache)
    print(f"{Fore.YELLOW}1️⃣  First call (COLD - no cache):")
    start = time.time()
    response1 = requests.get(f"{BASE_URL}/api/word/{word}")
    time1 = (time.time() - start) * 1000
    
    if response1.status_code == 200:
        data1 = response1.json()
        timing1 = data1.get('_timing', {})
        print(f"{Fore.RED}   ⏱️  Time: {time1:.2f} ms (OpenAI: {timing1.get('openai_api_ms', 0):.2f} ms)")
        print(f"{Fore.RED}   🐌 SLOW - OpenAI API call required")
    
    # Second call - hot (cached)
    print(f"\n{Fore.YELLOW}2️⃣  Second call (HOT - cached):")
    start = time.time()
    response2 = requests.get(f"{BASE_URL}/api/word/{word}")
    time2 = (time.time() - start) * 1000
    
    if response2.status_code == 200:
        data2 = response2.json()
        timing2 = data2.get('_timing', {})
        is_cached = timing2.get('cached', False)
        print(f"{Fore.GREEN}   ⏱️  Time: {time2:.2f} ms (Cache: {timing2.get('cache_lookup_ms', 0):.2f} ms)")
        if is_cached:
            print(f"{Fore.GREEN}   ⚡ FAST - From cache!")
        else:
            print(f"{Fore.RED}   ❌ ERROR - Should be cached!")
    
    # Performance comparison
    speedup = time1 / time2 if time2 > 0 else 0
    print(f"\n{Fore.CYAN}{'─'*80}")
    print(f"{Fore.YELLOW}📊 COMPARISON:")
    print(f"{Fore.WHITE}   Cold (no cache):  {time1:>8.2f} ms")
    print(f"{Fore.WHITE}   Hot (cached):     {time2:>8.2f} ms")
    print(f"{Fore.GREEN}   Speedup:          {speedup:>8.1f}x faster! 🚀")
    print(f"{Fore.CYAN}{'─'*80}")
    
    if time2 < 50:
        print(f"{Fore.GREEN}✅ EXCELLENT: Cache response in milliseconds!")
    elif time2 < 100:
        print(f"{Fore.CYAN}👍 GOOD: Cache response under 100ms")
    else:
        print(f"{Fore.YELLOW}⚠️  WARNING: Cache response slower than expected")

def main():
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          Finnish Learning API - Speed Test                     ║")
    print("║          Testing: http://localhost:5003                        ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    # Test cache performance first
    test_cache_performance()
    
    # Test single word with detailed timing
    test_word_speed("kissa")
    
    # Test multiple words
    test_multiple_words()
    
    print(f"\n{Fore.GREEN}✅ Speed tests complete!\n")
    print(f"{Fore.CYAN}💡 TIP: First call to any word is slow (OpenAI API)")
    print(f"{Fore.CYAN}💡 TIP: Subsequent calls are cached and FAST (< 50ms)!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted by user.")
