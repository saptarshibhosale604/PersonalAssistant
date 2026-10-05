# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A personal "JARVIS-like" assistant (persona "RPI", user "SSB") that runs on a Raspberry Pi, either natively in a venv or inside a Docker container alongside Ollama. The main interface is a REPL CLI that forwards input to a LangChain agent backed by a local Ollama model or OpenAI. Tool calls go through human-in-the-loop approval.

## Running

All paths in the code are relative to the repo root (`./UI/modesConfig.json`, `./Langchain/Tools/toolsConfig.json`, `./Log/`). Always run from the repo root as a module:

```bash
source venv/bin/activate
python -m UI.cli               # main CLI (works on Linux and Windows)
python UI/WebApp/app.py        # Flask web UI on port 5001
```

`OPENAI_API_KEY` must be set in the environment for the `global` LLM mode. Local modes need an Ollama server reachable on port 11434 with the relevant models pulled (e.g. `qwen3.5:4b`, `llama3.2:1b`).

Docker flow (the image sets `WORKDIR /App` and `PYTHONPATH=/App`; it is built on a custom base image `alpine-ollama-python3-02` from `DockerCustomImage/Layer01` → `Layer02`):

```bash
docker build -t personal_assistant .
docker rm ollamaLocal -f
docker run -d --rm -v ollama:/root/.ollama -v /home/ssbrpi/ProjectRpi:/root/ProjectRpi/ -p 11434:11434 --name ollamaLocal personal_assistant
docker exec -it ollamaLocal python /App/UI/cli.py
```

Inside the container, `. /root/.profile` adds the `refreshDir` / `cli` aliases, which recopy the mounted source into `/App` and then start the CLI.

There is no test suite, linter, or build step. `Testing/` holds standalone experiment scripts that you run directly.

## Architecture

**Request flow:** `UI/cli.py` (an infinite `Main()` loop) → `Input()` → `Processing()` → `Langchain/agent.py:Main(userInput, threadId, modeLLM, modeStream)` → `Output()`.

**Modes:** All runtime behaviour is set by a flat JSON file, `UI/modesConfig.json` (gitignored; recreated from defaults by `UI/modesManager.py` when missing). Keys are `mode-llm`, `mode-stream`, `mode-input` (text/multi/file/speech), `mode-output`, `mode-context`, `mode-framework` (langchain/fabric), `mode-conversation`, and others. `cli.py` re-reads this file on every access, so edits made on disk apply right away. `UI/config.py` holds the defaults, the allowed values with descriptions (used by the `modesManager` TUI), and presets. If you add a mode value, update both `config.py` and the branches that consume it.
- `/sandbox true` switches to `UI/modesConfigSandbox.json`. That lets one CLI instance use different modes from others, since all instances otherwise share one file.
- CLI commands come in two parallel styles, both handled in `cli.py`: the legacy `mode <name> <value>` / `help` (`BasicCmds`) and the newer slash commands `/llm`, `/input`, `/stream`, `/get`, `/update`, `/tools`, `/sandbox`, `/new`, `/reset` (`BasicCmds02`).

**Agent (`Langchain/agent.py`):**
- Uses module-level globals `LLM`, `TOOLS` and `AGENT`. `UpdateAgent(modeLLM)` rebuilds the agent only when `mode-llm` changes. Each mode name (`local-1b`, `local-4b`, `local-4b-no-tools`, `local-buddy`, `global`, …) maps to a `ChatOllama`/`ChatOpenAI` instance plus a tool set. Some local modes deliberately get no tools.
- `Main` branches on both `modeLLM` and `modeStream`. Each branch has its own invoke/stream loop for handling interrupts, so a behaviour change usually has to be made in several branches.
- Conversation memory is LangGraph's `InMemorySaver`, keyed by `thread-<THREAD_ID>`. `cli.py` owns `THREAD_ID`: it increments on `/new`, and on every turn when `mode-context` is `no`.
- HITL: `TOOL_INTERRUPT_POLICY` in `agent.py` lists, by tool name, which tools pause for approval. Resuming uses `Command(resume={"decisions": [...]})`, with one decision per pending tool call (a mismatch raises a ValueError). Streaming uses `stream_mode=["updates", "messages"]`, parsed in `ExtractStreamContent`.

**Tools (`Langchain/Tools/`):**
- `toolsManager.py` holds a `TOOLS_MODULES` map from a group name to a module path. Each module has to expose `ToolsList()`, which returns LangChain tools. `toolsConfig.json` stores the enabled/disabled flag for each group and is toggled interactively with `/tools update`. `toolsManager.Main("get")` returns the combined list of enabled tools.
- To add a tool group: create the module with `ToolsList()`, register it in `TOOLS_MODULES`, add a key to `toolsConfig.json`, and add any tools that need approval to `TOOL_INTERRUPT_POLICY` in `agent.py`.

**Other components:**
- `Fabric/` is an alternate framework path (`mode-framework fabric`) that wraps the Fabric CLI. Its import is currently commented out in `cli.py`.
- `UserContext/` handles persisted user-context JSON.
- `TextToSpeech/` and `SpeechToText/` are optional I/O backends; their imports are commented out in `cli.py`.
- `News/` and `LLM/` are standalone utilities.
- `*.bak` files and `Langchain/Backup/` are manual backups, not live code.

**Logging:** `from Log.custom_logger import logger` writes to `./Log/<date>_log.log` and also echoes `info` to the console. Most functions carry the `@PrintFunctionName` decorator from `Log/log_utils.py`, which prints call traces only when `ENABLE_LOGGING = True` in that file.

## Conventions

- Functions and module-level helpers use PascalCase names (`LoadModes`, `GetToolsList`), and locals use camelCase. Globals and constants are UPPER_SNAKE.
- `README.md` keeps the owner's running TODO/DONE list in the form `<priority A/B/C>, <bug|improve>, <description>`.
