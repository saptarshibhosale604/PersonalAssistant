import os
import re

def scan_code_vulnerabilities():
    print("[SUBAGENT CODE] Scanning Python source files for potential code vulnerabilities...")
    findings = []
    
    # Dangerous patterns
    patterns = {
        "SQL_INJECTION": r"execute\s*\(\s*f[\"\'].*?\{.*?\}.*?[\"\']\s*\)",
        "UNSAFE_EVAL": r"\b(eval|exec)\s*\(",
        "HARDCODED_SECRET": r"(api_key|password|secret|token)\s*=\s*['\"'][a-zA-Z0-9_\-]{8,}['\"']"
    }
    
    scan_dirs = ["Langchain", "UI", "Script"]
    for d in scan_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            for vuln_type, pattern in patterns.items():
                                matches = re.findall(pattern, content, re.IGNORECASE)
                                if matches:
                                    findings.append({
                                        "category": "CODE_SECURITY",
                                        "severity": "HIGH" if vuln_type != "HARDCODED_SECRET" else "CRITICAL",
                                        "file": filepath,
                                        "issue": f"Detected potential {vuln_type} pattern."
                                    })
                    except Exception as e:
                        print(f"[SUBAGENT CODE] Error reading {filepath}: {e}")
                        
    print(f"[SUBAGENT CODE] Scan complete. Found {len(findings)} potential issues.")
    return findings
