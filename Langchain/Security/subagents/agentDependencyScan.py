import os

def scan_dependencies():
    print("[SUBAGENT DEP] Scanning requirements and project configuration files...")
    findings = []
    
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        try:
            with open(req_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "==" not in line and ">=" not in line:
                            findings.append({
                                "category": "DEPENDENCY_SECURITY",
                                "severity": "MEDIUM",
                                "file": req_file,
                                "issue": f"Unpinned dependency package: '{line}'"
                            })
        except Exception as e:
            print(f"[SUBAGENT DEP] Error reading {req_file}: {e}")
            
    print(f"[SUBAGENT DEP] Dependency scan complete. Found {len(findings)} recommendations.")
    return findings
