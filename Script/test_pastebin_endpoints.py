#!/usr/bin/env python3
"""
TACTICAL RECON: Test no-auth pastebin endpoints for IP push
"""
import urllib.request
import urllib.parse
import sys

ENDPOINTS = {
    "0x0.st": "https://0x0.st",
    "ix.io": "https://ix.io",
    "sprunge.us": "http://sprunge.us",
    "paste.rs": "https://paste.rs",
    "clbin.com": "https://clbin.com",
    "0x0.at": "https://0x0.at",  # alternative domain
    "ttm.sh": "https://ttm.sh",  # timed paste
    "paste.century.link": "https://paste.century.link",
    "pastebin.pl": "https://pastebin.pl/api/api_post.php",  # different API
}

TEST_CONTENT = "103.31.40.65"  # Your IP

def test_endpoint(name: str, url: str) -> dict:
    """Test a single endpoint, return result dict."""
    try:
        data = urllib.parse.urlencode({"file": TEST_CONTENT}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("User-Agent", "curl/7.68.0")  # Some block default UA
        with urllib.request.urlopen(req, timeout=10) as resp:
            response = resp.read().decode().strip()
            status = resp.status
            
        # Validate: should be a short URL, not HTML
        is_html = response.lower().startswith("<") or "html" in response.lower()[:50]
        is_url = response.startswith("http") and len(response) < 100
        
        return {
            "name": name,
            "url": url,
            "status": status,
            "response": response[:200],
            "is_html": is_html,
            "is_url": is_url,
            "success": is_url and not is_html,
        }
    except Exception as e:
        return {
            "name": name,
            "url": url,
            "status": "ERROR",
            "response": str(e)[:200],
            "is_html": False,
            "is_url": False,
            "success": False,
        }

def main():
    print("[RECON] Testing no-auth pastebin endpoints...\n")
    results = []
    
    for name, url in ENDPOINTS.items():
        print(f"[SCAN] {name} ({url})...", end=" ", flush=True)
        result = test_endpoint(name, url)
        results.append(result)
        
        if result["success"]:
            print(f"[OK] SUCCESS -> {result['response']}")
        elif result["is_html"]:
            print(f"[FAIL] HTML ERROR -> {result['response'][:80]}...")
        else:
            print(f"[FAIL] FAILED ({result['status']}) -> {result['response'][:80]}...")
    
    print("\n" + "="*60)
    print("TACTICAL SUMMARY:")
    working = [r for r in results if r["success"]]
    if working:
        for r in working:
            print(f"  [OK] {r['name']}: {r['response']}")
    else:
        print("  [WARN] NO WORKING ENDPOINTS FOUND")
    
    print("\nFULL INTEL:")
    for r in results:
        print(f"  {r['name']:15} | {str(r['status']):6} | URL:{r['is_url']} HTML:{r['is_html']} | {r['response'][:100]}")

if __name__ == "__main__":
    main()