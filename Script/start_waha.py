"""
README / Overview:
--------------------------------------------------
PersonalAssistant Startup Script (start_waha.py)

Automates the startup sequence according to SSB's streamlined plan:
1. STEP 1: Check if Docker is launched; if not, launch it.
2. STEP 2: Check if the 'waha' container is running; if not, start it.
3. STEP 3: Check session status (STARTING -> wait 3s, SCAN_QR_CODE -> display QR, etc.).
4. STEP 4: Configure webhook and wait until status becomes 'WORKING'.
5. STEP 5: Summarize progress, wait 3 seconds for user digest, and launch waha_bridge.

Usage:
    python Script/start_waha.py
--------------------------------------------------
"""

import os
import time
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Load environment variables
    env_path = Path(r"E:\WORK\PROJECT\git\PersonalAssistant\.env")
    if not env_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {env_path}")
        
    print(f"Loading environment variables from {env_path}...")
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("WAHA_API_KEY")
    base_url = os.getenv("WAHA_API_URL", "http://localhost:3000")
    session_name = os.getenv("WAHA_SESSION", "default")
    bridge_port = os.getenv("WAHA_BRIDGE_PORT", "5002")
    webhook_url = f"http://host.docker.internal:{bridge_port}/webhook"

    # ==========================================
    # STEP 1: Check & Launch Docker
    # ==========================================
    print("\n----------------------------------------")
    print("STEP 01: Checking Docker status...")
    docker_running = False
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if res.returncode == 0:
            docker_running = True
    except Exception:
        pass

    if docker_running:
        print("[INFO] Docker is already running!")
    else:
        print("[INFO] Docker is not running. Launching Docker Desktop...")
        subprocess.Popen(["C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"])
        
        print("Waiting for Docker daemon to start...")
        max_attempts = 60
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                res = subprocess.run(["docker", "info"], capture_output=True, text=True)
                if res.returncode == 0:
                    docker_running = True
                    break
            except Exception:
                pass
            print(f"Waiting for Docker engine... (Attempt {attempt}/{max_attempts})")
            time.sleep(3)
            
        if not docker_running:
            raise Exception("Docker Desktop failed to start within the expected time.")
        print("[SUCCESS] Docker Desktop is up and running!")

    # ==========================================
    # STEP 2: Check & Launch WAHA Container
    # ==========================================
    print("\n----------------------------------------")
    print("STEP 02: Checking WAHA container status...")
    container_running = False
    try:
        res = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", "waha"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip() == "true":
            container_running = True
    except Exception:
        pass

    if container_running:
        print("[INFO] WAHA container 'waha' is already running!")
    else:
        print("[INFO] WAHA container is not running. Starting container...")
        whatsapp_dir = Path(r"E:\WORK\PROJECT\git\PersonalAssistant\UI\WhatsApp")
        os.chdir(whatsapp_dir)
        
        # Remove stopped container if exists
        subprocess.run(["docker", "rm", "-f", "waha"], capture_output=True)
        
        cmd = f'docker run -d -it --env-file "{whatsapp_dir}/.env" -v "{whatsapp_dir}/sessions:/app/.sessions" --rm -p 3000:3000 --name waha devlikeapro/waha'
        print(f"Command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        print("Waiting 15 seconds for WAHA container initialization...")
        time.sleep(15)

    # ==========================================
    # STEP 3: Check Session Status & Handle QR Code / STARTING
    # ==========================================
    print("\n----------------------------------------")
    print("STEP 03: Checking WAHA session status...")
    
    status_ready = False
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts and not status_ready:
        attempt += 1
        try:
            res = requests.get(
                f"{base_url}/api/sessions/{session_name}",
                headers={"x-api-key": api_key},
                timeout=5
            )
            if res.status_code == 200:
                data = res.json()
                status = data.get("status")
                print(f"[Session Status] Attempt {attempt}: {status}")
                
                if status == "WORKING":
                    print("[INFO] Session is already WORKING!")
                    status_ready = True
                    break
                elif status == "STARTING":
                    print("[INFO] Session is starting up. Waiting 3 seconds...")
                    time.sleep(3)
                    continue
                elif status in ("SCAN_QR_CODE", "PAIRING"):
                    print("\n[!] WAHA requires WhatsApp authentication (QR Code required)!")
                    # Fetch screenshot / QR code if available
                    qr_res = requests.get(
                        f"{base_url}/api/sessions/{session_name}/auth/qr",
                        headers={"x-api-key": api_key}
                    )
                    if qr_res.status_code == 200:
                        print("[INFO] QR Code retrieved successfully. Check WAHA dashboard or terminal output.")
                    print(f"Please scan the QR code via WAHA dashboard at {base_url}")
                    
                    # Wait for user to scan
                    input("Press Enter once you have scanned the QR code and WhatsApp is connected...")
                else:
                    print(f"[INFO] Status is '{status}'. Waiting 3 seconds...")
                    time.sleep(3)
            else:
                print(f"[INFO] Waiting for session API... Status code {res.status_code}")
                time.sleep(3)
        except Exception as e:
            print(f"[INFO] Connecting to WAHA API... ({e})")
            time.sleep(3)

    # ==========================================
    # STEP 4: Configure Webhook & Wait for WORKING
    # ==========================================
    print("\n----------------------------------------")
    print("STEP 04: Configuring webhook & verifying WORKING status...")
    
    payload = {
        "config": {
            "webhooks": [{"url": webhook_url, "events": ["message.any"]}],
            "ignore": {"status": True, "groups": True, "channels": True, "broadcast": True}
        }
    }
    
    res = requests.put(
        f"{base_url}/api/sessions/{session_name}",
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
        json=payload
    )
    res.raise_for_status()
    print("[SUCCESS] Webhook configured successfully:", res.json())

    print("Waiting for session status to become 'WORKING'...")
    working_confirmed = False
    attempt = 0
    while attempt < 30:
        attempt += 1
        try:
            res = requests.get(
                f"{base_url}/api/sessions/{session_name}",
                headers={"x-api-key": api_key}
            )
            if res.status_code == 200:
                data = res.json()
                status = data.get("status")
                if status == "WORKING":
                    print("[SUCCESS] WAHA session status is WORKING!")
                    working_confirmed = True
                    break
                else:
                    print(f"Current status: {status}. Waiting... (Attempt {attempt}/30)")
            else:
                print(f"Polling session status... Code {res.status_code}")
        except Exception as e:
            print(f"Polling session status... ({e})")
        time.sleep(3)

    if not working_confirmed:
        raise Exception("WAHA session did not reach 'WORKING' status.")

    # ==========================================
    # STEP 5: Summarize & Launch Bridge
    # ==========================================
    print("\n----------------------------------------")
    print("STEP 05: Summary & Bridge Launch")
    print("----------------------------------------")
    print("SUMMARY OF ACTIONS:")
    print("1. Docker Desktop: Running & Verified")
    print("2. WAHA Container ('waha'): Active & Listening")
    print("3. WAHA Session Status: WORKING")
    print(f"4. Webhook Configured: {webhook_url}")
    print("----------------------------------------")
    
    print("Pausing for 3 seconds for you to digest this information...")
    time.sleep(3)
    
    print("\nLaunching Python WAHA Bridge (`waha_bridge.py`)...")
    root_dir = Path(r"E:\WORK\PROJECT\git\PersonalAssistant")
    os.chdir(root_dir)
    cmd = "python -m UI.WhatsApp.waha_bridge"
    print(f"Running command: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":
    main()
