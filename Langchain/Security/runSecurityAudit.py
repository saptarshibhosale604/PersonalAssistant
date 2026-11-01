import sys
import os

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from Langchain.Security.securityOrchestrator import run_stage, load_security_state
from Langchain.Security.subagents.agentCodeAnalysis import scan_code_vulnerabilities
from Langchain.Security.subagents.agentDependencyScan import scan_dependencies
from Langchain.Security.subagents.agentSecretLeak import scan_secrets_and_pii
from Langchain.Security.securityAggregator import aggregate_reports

def run_full_security_audit():
    print("==================================================")
    print("[SECURITY] INITIATING DISTRIBUTED SECURITY AUDIT SWEEP")
    print("==================================================")
    
    # Stage 1: Code Vulnerabilities
    run_stage("CodeAnalysis", scan_code_vulnerabilities)
    
    # Stage 2: Dependency Security
    run_stage("DependencyScan", scan_dependencies)
    
    # Stage 3: Secrets & PII Exposure
    run_stage("SecretLeakScan", scan_secrets_and_pii)
    
    # Final Aggregation
    report_path = aggregate_reports()
    print("==================================================")
    print(f"[SECURITY] SECURITY SWEEP COMPLETE. REPORT READY: {report_path}")
    print("==================================================")

if __name__ == "__main__":
    run_full_security_audit()
