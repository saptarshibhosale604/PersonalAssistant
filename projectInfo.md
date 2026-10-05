# Project Information: Personal Assistant (RPI / JARVIS)

## 📌 Project Overview
A modular, multi-modal personal assistant designed to run on a **Raspberry Pi** and inside **Docker containers**. It supports both local LLMs (Ollama) and cloud LLMs (Google Gemini, OpenAI/ChatGPT), featuring tool-calling capabilities, human-in-the-loop (HITL) tool approval, context memory, and multiple user interfaces (CLI and Web App).

---

## 🛠️ Technology Stack
- **Hardware:** Raspberry Pi
- **Containerization:** Docker & Docker Compose
- **Languages & Frameworks:** Python, Langchain / LangGraph
- **Database:** SQLite
- **LLM Integrations:**
  - **Cloud:** Google Gemini (`gemini-3.6-flash`, `gemini-3.5-flash-lite`, etc.), OpenAI
  - **Local:** Ollama (e.g., Qwen3.5, Gemma4 via LM Studio / Docker)

---

## 📂 Project Structure & Key Directories
- `UI/`: User interfaces (`cli.py`, `WebApp/app.py`)
- `Langchain/`: Core agent logic, tools, and execution (`agent.py`, `agent02.py`)
- `LLM/`: LLM configurations and initialization (`llm.py`)
- `UserContext/`: Persistent user session and context data
- `Log/`: Application execution and error logs (`log.log`)
- `Testing/`: Experimental scripts and model tests (e.g., `testGemini.py`)
- `Bashrc/`, `CmdsScripts/`: Shell scripts, aliases, and Git authentication
- `Dockerfiles`: `Dockerfile`, `DockerfileOld`

---

## 🚀 Key Features & Capabilities
1. **Dual LLM Modes:** Switch between cloud models (with advanced tool-calling) and local offline LLMs.
2. **Tool Integration & HITL:** Agents can invoke shell commands, file tools, web searches, etc., with granular control over which tools require human confirmation before execution.
3. **Context Management:** Supports context remembering and toggling conversation history.
4. **Multiple Interfaces:** Fully interactive CLI and Flask/Python Web App.

---

## 📝 Common Commands & Workflows

### Docker Build & Run (Ollama Local + Assistant)
```bash
docker build -t personal_assistant . 
docker rm ollamaLocal -f
docker run -d --rm -v ollama:/root/.ollama -v $(pwd):/root/ProjectRpi/ -p 11434:11434 --name ollamaLocal personal_assistant
```

### Running the CLI inside Docker
```bash
docker exec -it ollamaLocal sh -c '. /root/.profile; refresh && python /App/UI/cli.py'
```
*(Or interactive shell)*:
```bash
docker exec -it ollamaLocal /bin/sh
. /root/.profile
refresh
python /App/UI/cli.py
```

### Running the Web App
```bash
docker run -d --rm -v ollama:/root/.ollama -v $(pwd):/root/Project/ -p 11434:11434 -p 5001:5001 --name ollamaLocal personal_assistant
docker exec -it ollamaLocal python /App/UI/WebApp/app.py
```

### Testing Gemini Models
```bash
python Testing/testGemini.py
```

---

## ⚠️ Active Status & TODOs (Summary)
- **Active Model Defaults:** `gemini-3.6-flash` (Cloud, primary agent) and `gemini-3.5-flash-lite` (Fast fallback).
- **Known Issues / Items in Progress:**
  - Multi-line user input mode refinement.
  - Local LLM tool calling improvements and prompt engineering (JARVIS persona).
  - Shell tool multiple command handling.
  - Multi-instance mode isolation for concurrent CLI/Web usage.
