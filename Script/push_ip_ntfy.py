#!/usr/bin/env python3
"""
TACTICAL MODULE: push_ip_ntfy.py
Pushes current public IP to ntfy.sh with a PREDICTABLE TOPIC NAME.
No output parsing needed — URL is known in advance.
Mobile: Install ntfy app, subscribe to topic → INSTANT NOTIFICATION.
"""
import sys
import socket
import urllib.request
import urllib.parse
import platform

# ─── CONFIG ───
# CHOOSE YOUR TOPIC NAME ONCE — THIS IS YOUR PREDICTABLE URL
# Format suggestion: pi-ip-<hostname>-<short-unique>
HOSTNAME = platform.node().lower().replace(".", "-")
TOPIC_NAME = f"pi-ip-{HOSTNAME}-{abs(hash(HOSTNAME)) % 10000:04d}"  # e.g., pi-ip-mypi-1234
NTFY_URL = f"https://ntfy.sh/{TOPIC_NAME}"

# Optional: Add title/tags for ntfy app
TITLE = f"Pi IP Update: {HOSTNAME}"
TAGS = "raspberry_pi,ip,auto"
PRIORITY = "default"  # default, low, high, urgent

TIMEOUT = 10

# ─── TACTICAL FUNCTIONS ───
def get_public_ip() -> str:
    """Resolve public IP via DNS (fast, no HTTP)."""
    try:
        return socket.gethostbyname("myip.opendns.com")
    except socket.gaierror:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as r:
            return r.read().decode().strip()

def push_to_ntfy(ip: str) -> bool:
    """POST IP to ntfy.sh topic with headers."""
    data = ip.encode()
    req = urllib.request.Request(NTFY_URL, data=data, method="POST")
    req.add_header("Title", TITLE)
    req.add_header("Tags", TAGS)
    req.add_header("Priority", PRIORITY)
    req.add_header("User-Agent", "curl/7.68.0")
    
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[ERROR] ntfy.sh push failed: {e}", file=sys.stderr)
        return False

def retrieve_from_ntfy() -> str:
    """Fetch latest message from topic (for verification)."""
    req = urllib.request.Request(NTFY_URL)
    req.add_header("Accept", "text/plain")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read().decode().strip()
    except Exception as e:
        print(f"[ERROR] ntfy.sh retrieval failed: {e}", file=sys.stderr)
        return ""

def main():
    ip = get_public_ip()
    print(f"[INTEL] Public IP acquired: {ip}")
    print(f"[TOPIC] {TOPIC_NAME}")
    print(f"[URL]   {NTFY_URL}")
    print(f"[MOBILE] Install 'ntfy' app -> Subscribe to '{TOPIC_NAME}' -> INSTANT NOTIFICATION")
    
    if push_to_ntfy(ip):
        print(f"[SUCCESS] Pushed to ntfy.sh")
        
        # Verify
        retrieved = retrieve_from_ntfy()
        if retrieved == ip:
            print(f"[VERIFIED] Retrieval OK: {retrieved}")
        else:
            print(f"[WARN] Retrieval mismatch: got '{retrieved}'", file=sys.stderr)
        
        print(f"\n[TACTICAL] YOUR PREDICTABLE URLS:")
        print(f"  View latest:     {NTFY_URL}")
        print(f"  Raw (curl):      curl {NTFY_URL}")
        print(f"  JSON (latest):   {NTFY_URL}/json")
        print(f"  Subscribe (app): ntfy://{TOPIC_NAME}")
        return 0
    else:
        print("[ERROR] Push failed.", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())