import os

def scan_secrets_and_pii():
    print("[SUBAGENT SECRETS] Scanning environment and configuration files for exposed secrets...")
    findings = []
    
    env_files = [".env", ".envTemplate", "credentials.json"]
    for ef in env_files:
        if os.path.exists(ef):
            findings.append({
                "category": "SECRET_EXPOSURE",
                "severity": "HIGH",
                "file": ef,
                "issue": f"Sensitive configuration file '{ef}' present in workspace root. Ensure it is excluded in .gitignore."
            })
            
    print(f"[SUBAGENT SECRETS] Secret scan complete. Found {len(findings)} configuration alerts.")
    return findings
