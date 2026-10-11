# Implementation Plan: Adding NVIDIA Build Free Tier Models

This plan outlines the steps required to add two free-tier models from [NVIDIA Build](https://build.nvidia.com/models) into the agent and its supporting frameworks (Langchain/agent.py, Fabric/manager.py, UI/cli.py, and UI/config.py).

## 1. Selected NVIDIA Models
- **globalNvidia01**: meta/llama-3.1-70b-instruct (Optimized for complex reasoning, logic, and tool use)
- **globalNvidia02**: mistralai/mistral-large-2-instruct (Optimized for robust general-purpose tasks and generation)

---

## 2. File-by-File Changes

### A. Langchain/agent.py
Add elif modeLLM == "globalNvidia01": and elif modeLLM == "globalNvidia02": using ChatOpenAI configured with NVIDIA's OpenAI-compatible NIM endpoint (ase_url="https://integrate.api.nvidia.com/v1" and pi_key=os.environ.get("NVIDIA_API_KEY")).

### C. UI/cli.py
Register "globalNvidia01" and "globalNvidia02" in the valid CLI LLM options list.

### D. UI/config.py
Add description entries for both NVIDIA models in the TUI configuration dict.

### E. Environment Setup (.env)
Add the NVIDIA_API_KEY environment variable.
