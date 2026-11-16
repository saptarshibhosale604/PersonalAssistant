#!/usr/bin/env python3
"""
TACTICAL MODULE: push_ip.py (HARDENED)
Pushes current public IP to paste.rs (primary) with fallback endpoints.
Returns clean retrieval URL for mobile access.
Validates response is a URL, not HTML/error.
"""
import sys
import socket
import urllib.request
import urllib.parse

# ─── CONFIG ───
ENDPOINTS = {
    "paste.rs": "https://paste.rs",
    "0x0.st":   "https://0x0.st",
    "ix.io":    "https://ix.io",
}
PRIMARY = "paste.rs"
TIMEOUT = 10

# ─── TACTICAL FUNCTIONS ───
def get_public_ip() -> str:
    """Resolve public IP via DNS (fast, no HTTP)."""
    try:
        return socket.gethostbyname("myip.opendns.com")
    except socket.gaierror:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as r:
            return r.read().decode().strip()

def push_to_pastebin(content: str, endpoint: str) -> str:
    """POST content to endpoint, return retrieval URL."""
    url = ENDPOINTS[endpoint]
    data = urllib.parse.urlencode({"file": content}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("User-Agent", "curl/7.68.0")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        response = resp.read().decode().strip()
    
    # Validate: must be a URL, not HTML
    if response.lower().startswith("<") or "html" in response.lower()[:50]:
        raise ValueError(f"Endpoint returned HTML/error: {response[:100]}")
    if not response.startswith("http"):
        raise ValueError(f"Unexpected response format: {response[:100]}")
    
    return response

def retrieve_ip(url: str) -> str:
    """Fetch and parse IP from retrieval URL (handles paste.rs format)."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "text/plain")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        content = resp.read().decode().strip()
    
    # paste.rs returns "file=<content>" - strip prefix
    if content.startswith("file="):
        return content[5:]
    return content

def main():
    ip = get_public_ip()
    print(f"[INTEL] Public IP acquired: {ip}")

    for ep in [PRIMARY] + [e for e in ENDPOINTS if e != PRIMARY]:
        try:
            retrieve_url = push_to_pastebin(ip, ep)
            print(f"[SUCCESS] Pushed to {ep}: {retrieve_url}")
            
            # Verify retrieval works
            try:
                verified_ip = retrieve_ip(retrieve_url)
                print(f"[VERIFIED] Retrieval OK: {verified_ip}")
            except Exception as e:
                print(f"[WARN] Retrieval test failed: {e}", file=sys.stderr)
            
            print(f"[MOBILE ACCESS] Open this URL on Android: {retrieve_url}")
            return 0
        except Exception as e:
            print(f"[WARN] {ep} failed: {e}", file=sys.stderr)
    
    print("[ERROR] All endpoints failed.", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main())