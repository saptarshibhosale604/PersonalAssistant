import json
import os

def aggregate_reports():
    print("[SECURITY AGGREGATOR] Aggregating security audit sub-agent reports...")
    state_file = "sessions/SecurityAudit/security_state.json"
    if not os.path.exists(state_file):
        print("[SECURITY AGGREGATOR ERROR] No security state file found.")
        return None
        
    with open(state_file, "r") as f:
        state = json.load(f)
        
    findings = state.get("findings", [])
    
    report_content = "# 🛡️ Master Security Audit Report\n\n"
    report_content += f"**Status:** {state.get('status')}\n"
    report_content += f"**Last Updated:** {state.get('last_updated')}\n"
    report_content += f"**Completed Stages:** {', '.join(state.get('completed_stages', []))}\n\n"
    
    report_content += "## 📊 Executive Summary\n"
    report_content += f"Total Vulnerabilities / Findings Discovered: **{len(findings)}**\n\n"
    
    report_content += "## 🔍 Detailed Findings\n"
    if not findings:
        report_content += "No security vulnerabilities detected across completed agent sessions.\n"
    else:
        for idx, finding in enumerate(findings, 1):
            report_content += f"### {idx}. [{finding.get('severity')}] {finding.get('category')}\n"
            report_content += f"- **File/Target:** `{finding.get('file')}`\n"
            report_content += f"- **Issue:** {finding.get('issue')}\n\n"
            
    os.makedirs("Log", exist_ok=True)
    report_path = "Log/MasterSecurityReport.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"[SECURITY AGGREGATOR] Master security report successfully generated at '{report_path}'.")
    return report_path
