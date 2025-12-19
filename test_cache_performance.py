"""
Test script for enhanced extraction caching system
"""
import time
import requests
import json

def test_caching_performance():
    """Test that caching improves performance"""
    base_url = "http://localhost:5000"
    company = "kredily"
    
    print("\n" + "="*80)
    print("ENHANCED EXTRACTION CACHING TEST")
    print("="*80 + "\n")
    
    # Test 1: First request (cache miss - slow)
    print("Test 1: First request (expected: cache miss, slow)")
    print("-" * 80)
    start = time.time()
    
    response = requests.get(f"{base_url}/api/companies/{company}/enhanced")
    
    duration_first = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Status: {response.status_code}")
        print(f"⏱️  Duration: {duration_first:.2f}s")
        print(f"📊 Fields returned: {len(data)} fields")
        print(f"🏢 Company: {data.get('company_name', 'N/A')}")
        print(f"🏭 Sector: {data.get('sector', 'N/A')}")
        print(f"📧 Email: {data.get('email', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    print("\n" + "-" * 80)
    print("Waiting 2 seconds before next request...")
    time.sleep(2)
    
    # Test 2: Second request (cache hit - fast)
    print("\nTest 2: Second request (expected: cache hit, FAST)")
    print("-" * 80)
    start = time.time()
    
    response = requests.get(f"{base_url}/api/companies/{company}/enhanced")
    
    duration_second = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Status: {response.status_code}")
        print(f"⏱️  Duration: {duration_second:.2f}s")
        print(f"📊 Fields returned: {len(data)} fields")
        print(f"🏢 Company: {data.get('company_name', 'N/A')}")
        print(f"🏭 Sector: {data.get('sector', 'N/A')}")
        print(f"📧 Email: {data.get('email', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    # Test 3: Third request (cache hit - should be same speed)
    print("\n" + "-" * 80)
    print("Waiting 1 second before next request...")
    time.sleep(1)
    
    print("\nTest 3: Third request (expected: cache hit, FAST)")
    print("-" * 80)
    start = time.time()
    
    response = requests.get(f"{base_url}/api/companies/{company}/enhanced")
    
    duration_third = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Status: {response.status_code}")
        print(f"⏱️  Duration: {duration_third:.2f}s")
        print(f"📊 Fields returned: {len(data)} fields")
    else:
        print(f"❌ Error: {response.status_code}")
        return
    
    # Performance comparison
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON")
    print("="*80)
    print(f"First request (cache miss):  {duration_first:.2f}s")
    print(f"Second request (cache hit):  {duration_second:.2f}s")
    print(f"Third request (cache hit):   {duration_third:.2f}s")
    
    speedup_2 = duration_first / duration_second if duration_second > 0 else 0
    speedup_3 = duration_first / duration_third if duration_third > 0 else 0
    
    print(f"\n🚀 Speedup (2nd request): {speedup_2:.1f}x faster")
    print(f"🚀 Speedup (3rd request): {speedup_3:.1f}x faster")
    
    # Cache stats
    print("\n" + "="*80)
    print("CACHE STATISTICS")
    print("="*80)
    
    response = requests.get(f"{base_url}/api/cache/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"Total cached companies: {stats.get('total_cached', 0)}")
        print(f"Oldest entry: {stats.get('oldest_entry', 'N/A')}")
        print(f"Newest entry: {stats.get('newest_entry', 'N/A')}")
        print(f"Database path: {stats.get('db_path', 'N/A')}")
    
    print("\n" + "="*80)
    print("✅ CACHING TEST COMPLETE!")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n⚠️  Make sure the API server is running on http://localhost:5000")
    print("   Run: python api_server.py\n")
    
    input("Press Enter to start the test...")
    
    try:
        test_caching_performance()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("   Make sure it's running: python api_server.py\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
