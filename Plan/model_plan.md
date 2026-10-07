# Plan: Add Two Mistral Models (Analogous to globalGemini02)

## 1. Objective
Integrate two Mistral AI models into the Personal Assistant project, providing them as global model options similar to the existing `globalGemini02` configuration. The plan covers research, configuration, testing, and documentation.

## 2. Reference
- Mistral AI API documentation: https://docs.mistral.ai/api
- List of available Mistral models can be obtained via the `/models` endpoint.

## 3. Selected Mistral Models
(To be finalized after consulting the API; placeholder names used for planning):
- **Mistral Large** – `mistral-large-latest` (high‑capability, flagship model)
- **Mistral Small** – `mistral-small-latest` (lightweight, low‑latency model)
mistral-small-latest, ministral-8b-latest

*These correspond to the "globalGemini02" role of providing a primary and a fallback/alternative model.*

## 4. Plan Steps

| # | Step | Description |
|---|------|-------------|
| 1 | **Fetch model list** | Use the Mistral `/models` endpoint (or refer to docs) to confirm exact model identifiers and capabilities. |
| 2 | **Update LLM configuration** | Add the two models to the LLM initialization file (`LLM/llm.py` or equivalent config). Include model name, alias (`globalMistral01`, `globalMistral02`), API key handling, and any default parameters (temperature, max tokens). |
| 3 | **Environment variables** | Ensure the Mistral API key is available (e.g., `MISTRAL_API_KEY`) and documented in the project's `.env` or secrets management. |
| 4 | **Agent/Tool integration** | Modify the agent code (`Langchain/agent*.py`) to allow selection of the new models via user prompt or configuration default. Add optional HITL approval if the model is used for tool‑calling. |
| 5 | **UI updates** | Update the CLI (`UI/cli.py`) and Web App (`UI/WebApp/app.py`) to expose model selection dropdowns or command‑line flags for the Mistral options. |
| 6 | **Testing** | Run a simple API call for each model (e.g., `python -c "from Mistral import Mistral; client = Mistral(); print(client.chat(...))"`) to verify connectivity and basic functionality. |
| 7 | **Documentation** | Record the new model aliases, usage examples, and any cost/latency considerations in the project's README or a dedicated `docs/` section. |
| 8 | **Review & Merge** | Conduct a code review, ensure no existing tests break, and merge the changes. |

## 5. Configuration Sketch (example)

```python
# LLM/llm.py  (excerpt)
LLM_MODELS = {
    "globalGemini02": {"model": "gemini-3.6-flash", "api_key_env": "GOOGLE_API_KEY"},
    "globalMistral01": {"model": "mistral-large-latest", "api_key_env": "MISTRAL_API_KEY"},
    "globalMistral02": {"model": "mistral-small-latest", "api_key_env": "MISTRAL_API_KEY"},
}
```

## 6. Risks & Mitigations
- **API key exposure**: Keep keys in environment variables, never hard‑code.
- **Rate limits**: Implement exponential back‑off and respect Mistral's quota.
- **Model capability mismatch**: Test both models with the assistant's typical prompts before defaulting.

## 7. Deliverables
- Updated `LLM/llm.py` with two new entries.
- Updated `.env.example` (or secrets config) mentioning `MISTRAL_API_KEY`.
- UI tweaks to expose model selection.
- `./Plan/model_plan.md` (this document) saved for reference.

---
*Plan created on [date] for the Personal Assistant project. No code has been executed beyond this planning step.*