# Implementation Plan: Military Personality / Drill Sergeant Persona (Operation "General RPI")

## 🎯 Objective
Add a **military / drill sergeant personality** (e.g., Sergeant / General persona) as a new configurable LLM mode (`local-military` or `military`) in the RPI assistant suite. Master **SSB** will be addressed as "General", "Sir", or "Commander", and RPI will respond with crisp, disciplined, tactical phrasing ("Hoorah!", "Affirmative, General!", "Executing orders immediately!").

---

## 🛠️ Files to Modify & New Additions

### 1. `Langchain/agent.py`
- **Define System Prompt:** Add `MILITARY_SYSTEM_PROMPT`:
  ```python
  MILITARY_SYSTEM_PROMPT = (
      "You are RPI, a high-ranking tactical military AI assistant with a strict, disciplined, "
      "and fiercely loyal drill-sergeant and combat-AI personality. "
      "Your master is SSB, whom you address strictly as 'General SSB', 'Sir', or 'Commander'. "
      "Speak in crisp, military-grade phrasing, use tactical terminology (e.g., 'Mission parameters received', "
      "'Executing directive', 'Acknowledged, General!'), maintain absolute readiness, and remain both efficient "
      "and intimidatingly enthusiastic about accomplishing tasks."
  )
  ```
- **Update `Main()` routing:** Add branch for `local-military`:
  ```python
  elif modeLLM == "local-military":
      return StreamAndAccumulate(
          [
              {"role": "system", "content": MILITARY_SYSTEM_PROMPT},
              {"role": "user", "content": userInput},
          ],
          configMemory,
      )
  ```
- **Update `UpdateAgent(modeLLM)`:** Ensure `local-military` initializes `ChatOllama` with the default local model (e.g. `qwen3.5:4b`) and equips tools (`TOOLS = toolsManager.Main("get")`).

### 2. `UI/config.py`
- Add `local-military` to `modeConfigInitializationJson['mode-llm']['allowed']`:
  ```python
  'local-military': 'Model running locally with Military / Drill Sergeant persona (Commander SSB)',
  ```

### 3. `UI/modesTUI02.py`, `UI/modesTUI03.py` (if applicable)
- Ensure option descriptions include the new military persona so TUI menus display it properly.

---

## 📋 Step-by-Step Implementation Steps

1. **Step 1:** Define `MILITARY_SYSTEM_PROMPT` in `Langchain/agent.py`.
2. **Step 2:** Update `UpdateAgent()` in `Langchain/agent.py` so `local-military` loads `qwen3.5:4b` with tool support.
3. **Step 3:** Update `Main()` in `Langchain/agent.py` to route `local-military` with `MILITARY_SYSTEM_PROMPT`.
4. **Step 4:** Add `local-military` option in `UI/config.py` under `modeConfigInitializationJson`.
5. **Step 5:** Verify TUI and CLI execution (`python UI/cli.py` or `modesManager.py`).

---

## ⚠️ Potential Edge Cases & Considerations
- **Tool Execution Interruption:** Ensure HITL tool approvals work seamlessly with the new prompt (when tools like `toolShell` or `toolReadFile` are invoked, RPI should report execution with military precision).
- **Streaming Mode:** Check `mode-stream` compatibility with `local-military` mode.
