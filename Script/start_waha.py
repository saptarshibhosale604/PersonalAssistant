"""
README / Overview:
--------------------------------------------------
PersonalAssistant Startup Script (start_waha.py)

This script automates the full startup sequence for WAHA and the PersonalAssistant WhatsApp bridge:
1. Loads environment variables from the root .env file using python-dotenv.
2. STEP 01: Starts Docker Desktop and waits until the Docker daemon is responsive.
3. STEP 02: Starts the WAHA container and waits 20 seconds for initialization.
4. STEP 03: Configures the WAHA session webhook (pointing to the Python bridge).
5. STEP 04: Checks session status and polls until status becomes 'WORKING'.
6. STEP 05: Starts the Python WAHA bridge (`python -m UI.WhatsApp.waha_bridge`).

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

def run_step(step_num, description, action_func, wait_after=0, wait_for_working=False, api_config=None):
    print(f"\n----------------------------------------")
    print(f"STEP {step_num:02d}: {description}")
    print("Waiting for 3 seconds...")
    time.sleep(3)
    
    print("Running command...")
    try:
        action_func()
        
        if wait_after > 0:
            print(f"Waiting for {wait_after} seconds for service/container initialization...")
            time.sleep(wait_after)
            
        if wait_for_working and api_config:
            print("Waiting for WAHA session status to become 'WORKING'...")
            max_attempts = 40
            attempt = 0
            is_working = False
            
            while attempt < max_attempts:
                attempt += 1
                try:
                    res = requests.get(
                        f"{api_config['base_url']}/api/sessions/{api_config['session_name']}",
                        headers={"x-api-key": api_config['api_key']}
                    )
                    if res.status_code == 200:
                        data = res.json()
                        status = data.get("status")
                        if status == "WORKING":
                            print("WAHA session status is WORKING!")
                            print(data)
                            is_working = True
                            break
                        else:
                            print(f"Current session status: {status}. Waiting... (Attempt {attempt}/{max_attempts})")
                    else:
                        print(f"Connecting to session API... Status code {res.status_code} (Attempt {attempt}/{max_attempts})")
                except Exception as e:
                    print(f"Connecting to session API... (Attempt {attempt}/{max_attempts})")
                
                time.sleep(3)
                
            if not is_working:
                raise Exception("WAHA session did not reach 'WORKING' status within the expected time.")
                
        print("[SUCCESS] Step completed.")
    except Exception as e:
        print(f"[ERROR/WARNING] {e}")
        raise e

def main():
    # 0. Load Configuration from root .env file using load_dotenv
    env_path = Path(r"E:\WORK\PROJECT\git\PersonalAssistant\.env")
    if not env_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {env_path}")
        
    print(f"Loading environment variables from {env_path} using load_dotenv...")
    load_dotenv(dotenv_path=env_path)
    
    required_keys = ["WAHA_API_KEY", "WAHA_API_URL", "WAHA_SESSION"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print(f"There are no env vars for: {', '.join(missing_keys)}")
        
    api_key = os.getenv("WAHA_API_KEY")
    base_url = os.getenv("WAHA_API_URL")
    session_name = os.getenv("WAHA_SESSION")
    bridge_port = os.getenv("WAHA_BRIDGE_PORT", "5002")
    webhook_url = f"http://host.docker.internal:{bridge_port}/webhook"
    
    api_config = {
        "base_url": base_url,
        "session_name": session_name,
        "api_key": api_key
    }

    # 1. Start Docker Desktop and wait until it is running
    def start_docker():
        print("Command: Start-Process 'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe'")
        subprocess.Popen(["C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"])
        
        print("Checking Docker engine status...")
        max_attempts = 60
        attempt = 0
        docker_running = False
        
        while attempt < max_attempts:
            attempt += 1
            try:
                res = subprocess.run(["docker", "info"], capture_output=True, text=True)
                if res.returncode == 0:
                    docker_running = True
                    break
            except Exception:
                pass
            print(f"Waiting for Docker daemon to start... (Attempt {attempt}/{max_attempts})")
            time.sleep(3)
            
        if not docker_running:
            raise Exception("Docker Desktop failed to start within the expected time.")
        print("Docker Desktop is fully up and running!")

    run_step(1, "Starting Docker Desktop & Waiting for Engine", start_docker)

    # 2. Start the WAHA container
    whatsapp_dir = Path(r"E:\WORK\PROJECT\git\PersonalAssistant\UI\WhatsApp")
    def start_waha():
        os.chdir(whatsapp_dir)
        cmd = f'docker run -d -it --env-file "{whatsapp_dir}/.env" -v "{whatsapp_dir}/sessions:/app/.sessions" --rm -p 3000:3000 --name waha devlikeapro/waha'
        print(f"Command: {cmd}")
        time.sleep(2)
        subprocess.run(cmd, shell=True, check=True)

    run_step(2, "Starting WAHA docker container", start_waha, wait_after=20)

    # 3. Configure the webhook
    def configure_webhook():
        print(f"Command: PUT /api/sessions/{session_name}")
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
        print("Webhook Configuration Result:")
        print(res.json())

    run_step(3, "Configuring WAHA session webhook", configure_webhook)

    # 4. Check the webhook status and wait until status is WORKING
    def check_webhook_status():
        print(f"Command: GET /api/sessions/{session_name}")
        res = requests.get(
            f"{base_url}/api/sessions/{session_name}",
            headers={"x-api-key": api_key}
        )
        res.raise_for_status()
        print("Initial Session Status Result:")
        print(res.json())

    run_step(4, "Checking WAHA session webhook status", check_webhook_status, wait_for_working=True, api_config=api_config)

    # 5. Start the waha bridge
    def start_bridge():
        root_dir = Path(r"E:\WORK\PROJECT\git\PersonalAssistant")
        os.chdir(root_dir)
        cmd = "python -m UI.WhatsApp.waha_bridge"
        print(f"Command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    run_step(5, "Starting Python WAHA bridge", start_bridge)

    print("\n=========================================")
    print("All startup steps executed!")

if __name__ == "__main__":
    main()
