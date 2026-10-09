# Plan: Create 2 NVIDIA Models (`globalGemini01` style)

## 1. Objective
Create a formal plan to integrate two NVIDIA API-hosted LLMs using the OpenAI-compatible NVIDIA API client (similar to the user's provided snippet utilizing `base_url="https://integrate.api.nvidia.com/v1"` and `model="z-ai/glm-5.3"`), and introduce them as global model configurations named `globalGemini01` (or equivalent NVIDIA model references under `globalGemini01` naming structure / NVIDIA equivalents) as requested.

## 2. Reference User Snippet
```python
from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "$NVIDIA_API_KEY"
)

completion = client.chat.completions.create(
  model="z-ai/glm-5.3",
  messages=[{"role":"system","content":"You are a helpful assistant."},{"role":"user","content":"Which number is larger, 9.11 or 9.8?"}],
  temperature=0.5,
  top_p=1,
  max_tokens=1024,
  stream=False
)

print(completion.choices[0].message)
```

## 3. Selected NVIDIA Models
1. **Model 1 (`globalNvidia01`)**: `z-ai/glm-5.3` (from your snippet)
2. **Model 2 (`globalNvidia02`)**: `meta/llama-3.1-70b-instruct` (or another NVIDIA catalog model as fallback)

## 4. Plan Steps

| # | Step | Description |
|---|------|-------------|
| 1 | **Environment Setup** | Define the environment variable `NVIDIA_API_KEY` across project config templates and Docker environments. |
| 2 | **LLM Module Configuration** | Extend `LLM/llm.py` (or create a dedicated NVIDIA connector wrapper) to initialize OpenAI clients pointing to `https://integrate.api.nvidia.com/v1` with `NVIDIA_API_KEY`. |
| 3 | **Model Aliasing** | Register the two NVIDIA models under the requested naming pattern (e.g., `globalGemini01` / `globalGemini02` NVIDIA variants or specific aliases requested like `globalGemini01` pointing to `z-ai/glm-5.3` and an auxiliary NVIDIA model). |
| 4 | **Agent & LangChain Integration** | Create LangChain/OpenAI chat wrappers or update `Langchain/agent.py` so the agent can route chat completions and tool calls through the NVIDIA API endpoint. |
| 5 | **UI & CLI Updates** | Update CLI (`UI/cli.py`) and Web App (`UI/WebApp/app.py`) model selection flags/menus to include the new NVIDIA models. |
| 6 | **Testing Script** | Create a test script in `Testing/testNvidiaModels.py` to test both models with sample prompts. |
| 7 | **Documentation** | Update `README.md` and `projectInfo.md` with instructions on setting `NVIDIA_API_KEY` and using the NVIDIA-hosted models. |

## 5. Configuration Sketch (Example)

```python
# LLM/llm.py (excerpt for NVIDIA models)
from openai import OpenAI

NVIDIA_MODELS = {
    "globalNvidia01": {
        "model": "z-ai/glm-5.3",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY"
    },
    "globalNvidia02": {
        "model": "meta/llama-3.1-70b-instruct",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY"
    }
}
```

## 6. Risks & Mitigations
- **API Key Security**: Ensure `NVIDIA_API_KEY` is loaded securely from environment variables and not checked into source control.
- **OpenAI Client Compatibility**: Since NVIDIA uses the OpenAI SDK format (`base_url`), ensure timeout, streaming, and parameter handling (`temperature`, `top_p`, `max_tokens`) match OpenAI API specs.

## 7. Deliverables
- This plan document (`Plan/nvidia_models_plan.md`).
- Planned integration architecture for NVIDIA API models in `LLM/llm.py`.
