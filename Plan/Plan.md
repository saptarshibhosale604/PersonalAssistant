# 📋 Project Plan & Recent Changes

## 📌 Current Focus & Recent Modifications

### 1. `Langchain/agent.py`
- Added `import time` and a `time.sleep(10)` delay inside `ExtractStreamContent` after printing stream chunks.
- **Goal / Status:** Added for testing stream timing/throttling and chunk inspection during tool-calling and response generation.

### 2. `UI/cli.py`
- Enhanced `BasicCmdsMode` command parsing:
  - Added support for `/` and `/help` prefixes alongside `help`.
  - Expanded and structured the help output to clearly list available slash commands (`/input`, `/llm`, `/stream`, `/get`, `/update`, `/sandbox`, `/tools`, `/resume`, `/skill`, `/reset`, `/exit`, and custom skills).
- **Goal / Status:** Improve user experience and discoverability of available CLI commands.

---

## 🚀 Next Steps / Todo List
- [ ] Review the impact of `time.sleep(10)` in `Langchain/agent.py` and decide whether to keep or remove it for production.
- [ ] Test new `/help` commands in the CLI to ensure all slash commands execute properly.
- [ ] Continue refining multi-line input handling in `UI/cli.py`.
