# Plan: Add OpenRouter Modes

## Request
Add 2 OpenRouter models like `globalGemini02`, named:
- `globalOpenRouter01`
- `globalOpenRouter02`

Reference:
- https://openrouter.ai/docs/quickstart#using-the-openai-sdk

## Scope
Plan only. Do not implement.

---

## Project areas involved
Based on current project structure, the following files/areas are relevant:

1. `Langchain/agent.py`
   - Main LLM mode switch logic for LangChain framework.
   - Best existing reference: `globalGroq01` / `globalGroq02` blocks using `ChatOpenAI` with custom `base_url`.

3. `UI/config.py`
   - Defines allowed values and descriptions for `mode-llm`.

4. `UI/cli.py`
   - Contains `COMMANDS` list with known mode names.

5. `UI/modesManager.py`
   - Uses `UI/config.py` for menu rendering.
   - Likely no structural change needed if config is updated.

6. `README.md`
   - Should document required environment variable and the new mode aliases.

---

## Integration strategy
OpenRouter should be added using the same OpenAI-compatible pattern already used for Groq.

### Planned client pattern
Use LangChain `ChatOpenAI` configured with:
- `base_url="https://openrouter.ai/api/v1"`
- `api_key=os.environ.get("OPENROUTER_API_KEY")`
- `model="<openrouter-provider/model-id>"`

This matches the OpenRouter quickstart approach for OpenAI-compatible SDK usage.

---

## Decisions needed before implementation
The alias names are clear, but the actual routed models must be chosen.

Need to decide:
- `globalOpenRouter01` -> which real OpenRouter model?
- `globalOpenRouter02` -> which real OpenRouter model?

Answer:
nvidia/nemotron-3-ultra:free, nvidia/nemotron-3.5-lightning:free

### Recommended mapping intent
- `globalOpenRouter01`: stronger planning / reasoning / tool-use model
- `globalOpenRouter02`: faster / cheaper / fallback general-purpose model

---

## Planned file-by-file changes

### 1) `UI/config.py`
Add two entries under:
- `modeConfigInitializationJson['mode-llm']['allowed']`

Planned new options:
- `globalOpenRouter01`
- `globalOpenRouter02`

Planned description style:
- `globalOpenRouter01`: cloud / OpenRouter model 01, stronger planning + tool use
- `globalOpenRouter02`: cloud / OpenRouter model 02, faster fallback / general tasks

Notes:
- Keep current default `mode-llm` unchanged unless explicitly requested.
- No preset changes required unless user wants OpenRouter included in presets.

### 2) `UI/cli.py`
Update the `COMMANDS` list to include:
- `globalOpenRouter01`
- `globalOpenRouter02`

Reason:
- Keeps CLI-recognized mode names aligned with config options.

### 3) `Langchain/agent.py`
Add two new `elif` branches inside `UpdateAgent(modeLLM)`.

Planned behavior:
- Both modes use `ChatOpenAI`
- Both point to OpenRouter endpoint
- Both read `OPENROUTER_API_KEY` from environment
- Both enable tools via `toolsManager.Main("get")`
- Both follow current cloud model conventions for:
  - `streaming=True`
  - `max_tokens=DEFAULT_MAX_TOKENS`
  - `temperature=DEFAULT_TEMPERATURE`
  - `max_retries=DEFAULT_MAX_RETRIES`

Suggested structure:
- `globalOpenRouter01` -> stronger OpenRouter model alias
- `globalOpenRouter02` -> faster OpenRouter model alias

### 5) `README.md`
Add documentation for:
- `OPENROUTER_API_KEY`
- new `mode-llm` values
- which actual models `globalOpenRouter01` and `globalOpenRouter02` map to
- note that OpenRouter uses OpenAI-compatible API base URL

---

## Configuration approach options

### Option A: Hardcode OpenRouter model IDs in code
Example idea:
- `globalOpenRouter01` -> fixed provider/model string
- `globalOpenRouter02` -> fixed provider/model string

Pros:
- simplest
- fastest to add

Cons:
- requires code changes when model IDs change
- duplicates mapping in more than one file

### Option B: Centralized constants, USER DECIDED to Go with this option
Define shared constants such as:
- `OPENROUTER_MODEL_01`
- `OPENROUTER_MODEL_02`

Pros:
- cleaner than fully inline strings

Cons:
- still code-based, not runtime configurable

### Option C: Environment-variable-driven mapping (recommended)
Use:
- `OPENROUTER_MODEL_01`
- `OPENROUTER_MODEL_02`

with fallback defaults if desired.

Pros:
- easier future model swapping
- better for testing and maintenance
- avoids repeated code edits when OpenRouter catalog changes

Recommended for this project:
- Use `OPENROUTER_API_KEY` for auth
- Prefer env-configurable alias mapping if you expect model changes

---

## Planned validation checklist
After implementation, verify:

### Mode/UI
- `globalOpenRouter01` appears in mode selection UI
- `globalOpenRouter02` appears in mode selection UI
- mode value saves correctly to config file
- CLI accepts the new mode names

### LangChain framework
- switching to `globalOpenRouter01` initializes without error
- switching to `globalOpenRouter02` initializes without error
- tool-enabled flow remains available
- streaming works acceptably

### Environment handling
- missing `OPENROUTER_API_KEY` gives understandable failure
- no OpenRouter secrets are hardcoded into source

### Documentation
- README clearly describes setup and alias mapping

---

## Risks / notes

1. Not every OpenRouter-backed model behaves identically with all OpenAI-style params.
   - tool calling, streaming, and token handling can vary by actual model.

2. Model choice matters.
   - some routed models may be weaker for tool calling or planning.

3. Current project duplicates mode logic in multiple places.
   - `Langchain/agent.py` and `Fabric/manager.py` must stay synchronized.

4. Existing repo contains hardcoded credentials in some files.
   - OpenRouter addition should avoid that pattern and use env vars only.

---

## Recommended implementation order
1. Choose real OpenRouter model IDs for both aliases.
2. Add the 2 new mode names to `UI/config.py`.
3. Add the 2 new mode names to `UI/cli.py`.
4. Add OpenRouter branches in `Langchain/agent.py`.
6. Document `OPENROUTER_API_KEY` and alias mapping in `README.md`.
7. Run validation checks in both frameworks.

---
