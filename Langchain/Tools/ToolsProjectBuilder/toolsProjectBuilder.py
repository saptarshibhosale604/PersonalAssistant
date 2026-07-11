import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.tools import tool
from langchain_ollama.chat_models import ChatOllama

# ------------------------------------------------------------------ #
# Global configuration
# ------------------------------------------------------------------ #
# NOTE on the qwen3.5:4b fixes below:
#
# 1. `max_tokens` is NOT a real ChatOllama/Ollama option -- Ollama's native
#    API only understands `num_predict`. Passing `max_tokens=...` to
#    ChatOllama is silently ignored, which meant every call in the original
#    file was actually running with Ollama's *default* num_predict of 128
#    tokens. That's far too short for a JSON architecture spec or a full
#    Python function, so generations were getting truncated mid-output --
#    which then failed JSON parsing / Python compilation and burned through
#    the fix-retry loops for the wrong reason. Fixed by using `num_predict`
#    and raising it well above 128.
# 2. `num_ctx` was never set, so Ollama used its default 2048-token context
#    window. Several prompts here (architecture generation, function
#    generation with the full contract + dependency graph inlined) can
#    exceed that easily, and Ollama truncates from the *start* of the
#    prompt when it overflows -- silently dropping instructions. Fixed by
#    setting an explicit, generous num_ctx.
# 3. Small quantized models are more prone to repetition loops and to
#    leaking `<think>...</think>` traces even with reasoning disabled.
#    Added `repeat_penalty` tuning and a defensive think-tag stripper.
# 4. Added a JSON retry-and-fix loop (mirroring the existing Python
#    compile-and-fix loop) since a 4B model fails to produce valid JSON on
#    the first try more often than larger models, especially for the big
#    architecture spec.
DEFAULT_MAX_TOKENS = 4096      # was 500 -- see note (1) above
DEFAULT_TEMPERATURE = 0
DEFAULT_MAX_RETRIES = 1
DEFAULT_NUM_CTX = 32768        # was unset (defaulted to 2048) -- see note (2)
DEFAULT_REPEAT_PENALTY = 1.3   # was unset (Ollama default 1.1) -- see note (3)
DEFAULT_TOP_K = 20             # Qwen-recommended sampling settings
DEFAULT_TOP_P = 0.95
BANNER_WIDTH = 60

MAX_COMPILE_FIX_ATTEMPTS = 2      # (#9)  per-function compile-and-fix retries
MAX_EXECUTION_FIX_ATTEMPTS = 2    # (#10) whole-project run-and-fix retries
MAX_VALIDATION_FIX_ATTEMPTS = 1   # (#6)  interface-validation regeneration passes
MAX_JSON_FIX_ATTEMPTS = 2         # (#new) JSON retry-and-fix, mirrors CompileWithFixLoop
EXECUTION_TIMEOUT_SECONDS = 5     # generated projects are often interactive loops;
                                   # a timeout without a traceback is treated as "ran ok"

# Global output file/dir names -- one per artifact, as in the original design.
PROJECT_IDEA_FILE = "Langchain/Tools/ToolsProjectBuilder/Project/project_idea.json"
PROJECT_GOAL_FILE = "Langchain/Tools/ToolsProjectBuilder/Project/project_goal.json"
PROJECT_ARCHITECTURES_FILE = "Langchain/Tools/ToolsProjectBuilder/Project/project_architectures.json"
PROJECT_DATA_MODEL_FILE = "Langchain/Tools/ToolsProjectBuilder/Project/ProjectScripts/data_model.py"
PROJECT_VALIDATION_FILE = "Langchain/Tools/ToolsProjectBuilder/Project/project_validation.json"
PROJECT_SCRIPTS = "Langchain/Tools/ToolsProjectBuilder/Project/ProjectScripts"

LLM = ChatOllama(
    model="qwen3.5:4b",
    streaming=True,
    num_predict=DEFAULT_MAX_TOKENS,
    temperature=DEFAULT_TEMPERATURE,
    max_retries=DEFAULT_MAX_RETRIES,
    # reasoning=False,
    reasoning=True,
    num_ctx=DEFAULT_NUM_CTX,
    repeat_penalty=DEFAULT_REPEAT_PENALTY,
    top_k=DEFAULT_TOP_K,
    top_p=DEFAULT_TOP_P,
)


# ------------------------------------------------------------------ #
# Shared helpers
# ------------------------------------------------------------------ #
def StreamLlmResponse(promptText):
    """
    Streams the LLM response chunk-by-chunk to stdout and returns the
    fully concatenated AIMessage-like object (last chunk carries the
    aggregated usage/response metadata once streaming completes).
    """
    fullChunk = None
    try:
        for chunk in LLM.stream(promptText):
            fullChunk = chunk if fullChunk is None else fullChunk + chunk
        print()
    except Exception as streamError:
        print(f"\n[StreamLlmResponse] Error while streaming LLM output: {streamError}")
        raise
    return fullChunk


def ExtractLlmMetrics(aiMessage):
    """
    Pulls token usage and timing metrics out of an AIMessage returned by
    ChatOllama. Ollama reports durations in nanoseconds, so they are
    converted to seconds here.
    """
    metrics = {}
    try:
        usage = getattr(aiMessage, "usage_metadata", None) or {}
        meta = getattr(aiMessage, "response_metadata", None) or {}

        inputTokens = usage.get("input_tokens", meta.get("prompt_eval_count", 0))
        outputTokens = usage.get("output_tokens", meta.get("eval_count", 0))
        totalTokens = usage.get("total_tokens", inputTokens + outputTokens)

        def NsToSeconds(nsValue):
            try:
                return round(int(nsValue) / 1e9, 2)
            except (TypeError, ValueError):
                return 0.0

        metrics = {
            "inputTokens": inputTokens,
            "outputTokens": outputTokens,
            "totalTokens": totalTokens,
            "createdAt": meta.get("created_at", datetime.now(timezone.utc).isoformat()),
            "loadDuration": NsToSeconds(meta.get("load_duration", 0)),
            "promptEvalDuration": NsToSeconds(meta.get("prompt_eval_duration", 0)),
            "generationDuration": NsToSeconds(meta.get("eval_duration", 0)),
            "totalDuration": NsToSeconds(meta.get("total_duration", 0)),
        }
    except Exception as metricsError:
        print(f"[ExtractLlmMetrics] Error extracting metrics: {metricsError}")
    return metrics


def PrintLlmMetrics(metrics):
    try:
        print("LLM Metrics Extraction:")
        print(f"Input Tokens       : {metrics.get('inputTokens', 0)}")
        print(f"Output Tokens      : {metrics.get('outputTokens', 0)}")
        print(f"Total Tokens       : {metrics.get('totalTokens', 0)}")
        print(f"Created At         : {metrics.get('createdAt', '')}")
        print(f"Load Duration      : {metrics.get('loadDuration', 0)}s")
        print(f"Prompt Eval Time   : {metrics.get('promptEvalDuration', 0)}s")
        print(f"Generation Time    : {metrics.get('generationDuration', 0)}s")
        print(f"Total Duration     : {metrics.get('totalDuration', 0)}s")
        print("-" * BANNER_WIDTH)
    except Exception as printError:
        print(f"[PrintLlmMetrics] Error printing metrics: {printError}")


def StripThinkTags(rawText):
    """
    Defensive cleanup for small/quantized Qwen models: even with
    reasoning=False requested, some Ollama builds still leak
    <think>...</think> reasoning traces into the main content. Strip them
    before any JSON/Python extraction so a stray reasoning block never
    gets parsed as if it were the actual output.
    """
    try:
        return re.sub(r"<think>.*?</think>", "", rawText, flags=re.DOTALL).strip()
    except Exception as stripError:
        print(f"[StripThinkTags] Error stripping think tags: {stripError}")
        return rawText


def ExtractJsonBlock(rawText):
    """
    Best-effort extraction of a JSON object/array from raw LLM text,
    in case the model wraps it in markdown code fences or extra prose.
    """
    try:
        rawText = StripThinkTags(rawText)
        fencedMatch = re.search(r"```(?:json)?\s*(.*?)```", rawText, re.DOTALL)
        candidateText = fencedMatch.group(1).strip() if fencedMatch else rawText.strip()
        return candidateText
    except Exception as extractError:
        print(f"[ExtractJsonBlock] Error extracting JSON block: {extractError}")
        return rawText


def ExtractPythonCode(rawText):
    """
    Best-effort extraction of raw Python source from LLM text, stripping
    markdown code fences if the model added them despite instructions
    not to.
    """
    try:
        rawText = StripThinkTags(rawText)
        fencedMatch = re.search(r"```(?:python)?\s*(.*?)```", rawText, re.DOTALL)
        return (fencedMatch.group(1).strip() if fencedMatch else rawText.strip())
    except Exception as extractError:
        print(f"[ExtractPythonCode] Error extracting Python block: {extractError}")
        return rawText.strip()


def ValidateJson(candidateText):
    try:
        return json.loads(candidateText)
    except json.JSONDecodeError as validationError:
        print(f"[ValidateJson] Invalid JSON produced by LLM: {validationError}")
        raise


def SaveJsonToFile(parsedObject, fileName):
    try:
        filePath = Path(fileName)
        filePath.parent.mkdir(parents=True, exist_ok=True)
        with open(filePath, "w", encoding="utf-8") as outFile:
            json.dump(parsedObject, outFile, indent=2, ensure_ascii=False)
        print(f"[SaveJsonToFile] Saved output to '{fileName}'")
    except Exception as saveError:
        print(f"[SaveJsonToFile] Error saving JSON to '{fileName}': {saveError}")
        raise


def BuildResultPayload(parsedContent, metrics):
    return {"result": parsedContent}


# ------------------------------------------------------------------ #
# (#new) JSON retry-and-fix loop, mirrors CompileWithFixLoop for Python.
# Small/quantized models are more likely to emit malformed or truncated
# JSON on the first pass (especially for the large architecture spec), so
# this feeds the parse error back to the model and asks it to fix ONLY
# the JSON, instead of failing the whole tool call outright.
# ------------------------------------------------------------------ #
def ValidateJsonWithFixLoop(initialPromptText, maxAttempts=MAX_JSON_FIX_ATTEMPTS):
    promptText = initialPromptText
    lastMetrics = {}
    lastError = None

    for attempt in range(1, maxAttempts + 2):  # first try + maxAttempts fix rounds
        aiMessage = StreamLlmResponse(promptText)
        lastMetrics = ExtractLlmMetrics(aiMessage)
        PrintLlmMetrics(lastMetrics)

        candidateText = ExtractJsonBlock(aiMessage.content)

        try:
            parsedContent = ValidateJson(candidateText)
            return parsedContent, lastMetrics, None
        except json.JSONDecodeError as jsonError:
            lastError = str(jsonError)
            print(f"[ValidateJsonWithFixLoop] Attempt {attempt} produced invalid JSON: {lastError}")
            if attempt > maxAttempts:
                return None, lastMetrics, lastError
            promptText = (
                "The following text was supposed to be a single valid JSON "
                "object/array but failed to parse.\n\n"
                f"Text:\n{candidateText}\n\n"
                f"JSON parse error:\n{lastError}\n\n"
                "Fix ONLY what is necessary so it becomes valid JSON. Preserve "
                "all field names and values as closely as possible to the "
                "original intent -- do not drop content just to make it parse.\n\n"
                "Output Rules:\n"
                "- Return ONLY the corrected JSON.\n"
                "- No markdown, no ```json fences, no explanations.\n"
                "- The first character of your response must be '{' or '['."
            )

    return None, lastMetrics, lastError


def RunJsonToolPipeline(promptText, fileName):
    """
    Shared pipeline used by JSON-producing tools:
      1. Stream the LLM response (printed live), retrying+fixing on
         invalid JSON (#new).
      2. Extract + print metrics.
      3. Wrap the JSON content.
      4. Save to the given file name.
    """
    try:
        parsedContent, metrics, jsonError = ValidateJsonWithFixLoop(promptText)
        if jsonError:
            print(f"[RunJsonToolPipeline] Giving up after fix attempts: {jsonError}")
            return {"error": jsonError}

        payload = BuildResultPayload(parsedContent, metrics)
        SaveJsonToFile(payload, fileName)
        return payload
    except Exception as pipelineError:
        print(f"[RunJsonToolPipeline] Pipeline failed: {pipelineError}")
        return {"error": str(pipelineError)}


def LoadJsonField(fileName, *keyPath, fallback=None):
    """
    DRY helper for the repeated 'load a nested field out of a saved JSON
    artifact, falling back gracefully' pattern used throughout this file.
    keyPath is walked under the top-level "result" key, e.g.
    LoadJsonField(PROJECT_GOAL_FILE, "projectGoal", fallback="...")
    """
    try:
        with open(fileName, "r", encoding="utf-8") as f:
            data = json.load(f)
        node = data.get("result", {})
        for key in keyPath:
            node = node.get(key)
            if node is None:
                raise ValueError(f"Could not find '{'.'.join(keyPath)}' in {fileName}.")
        return node
    except FileNotFoundError:
        print(f"[LoadJsonField] File {fileName} not found. Using fallback.")
        return fallback
    except json.JSONDecodeError as e:
        print(f"[LoadJsonField] Failed to parse {fileName}: {e}")
        return fallback
    except Exception as e:
        print(f"[LoadJsonField] {e}")
        return fallback


# -- Python validation / saving --

def ValidatePython(candidateText):
    """Raises SyntaxError if candidateText is not valid Python."""
    compile(candidateText, "<generated>", "exec")
    return candidateText


def SavePythonToFile(codeText, fileName):
    try:
        filePath = Path(fileName)
        filePath.parent.mkdir(parents=True, exist_ok=True)
        with open(filePath, "w", encoding="utf-8") as f:
            f.write(codeText)
        print(f"[SavePythonToFile] Saved output to '{fileName}'")
    except Exception as e:
        print(f"[SavePythonToFile] Error saving Python: {e}")
        raise


def BuildPythonPayload(codeText, metrics):
    return {"code": codeText, "metrics": metrics}


# ------------------------------------------------------------------ #
# (#9) Compile-and-fix loop
# ------------------------------------------------------------------ #
def CompileWithFixLoop(initialPromptText, maxAttempts=MAX_COMPILE_FIX_ATTEMPTS):
    """
    Streams an initial LLM completion expected to be Python source,
    validates it compiles, and if it doesn't, feeds the traceback back
    to the model asking it to fix ONLY the failing code. Repeats up to
    maxAttempts times. Returns (codeText, metrics, lastError).
    """
    promptText = initialPromptText
    lastMetrics = {}
    lastError = None

    for attempt in range(1, maxAttempts + 2):  # first try + maxAttempts fix rounds
        aiMessage = StreamLlmResponse(promptText)
        lastMetrics = ExtractLlmMetrics(aiMessage)
        PrintLlmMetrics(lastMetrics)

        codeText = ExtractPythonCode(aiMessage.content)

        try:
            ValidatePython(codeText)
            return codeText, lastMetrics, None
        except SyntaxError as syntaxError:
            lastError = str(syntaxError)
            print(f"[CompileWithFixLoop] Attempt {attempt} failed to compile: {lastError}")
            if attempt > maxAttempts:
                return codeText, lastMetrics, lastError
            promptText = (
                "The following Python code failed to compile.\n\n"
                f"Code:\n{codeText}\n\n"
                f"Compile error:\n{lastError}\n\n"
                "Fix ONLY what is necessary so the code compiles. Preserve the "
                "original function name, parameters, and behavior.\n\n"
                "Output Rules:\n"
                "- Return ONLY the corrected Python code.\n"
                "- No markdown, no ```python fences, no explanations.\n"
                "- The first character of your response must be 'd' from the word 'def' "
                "(or an import line if imports are required, prefixed before it)."
            )

    return codeText, lastMetrics, lastError


def RunPyToolPipeline(promptText, fileName, useFixLoop=True):
    """
    Pipeline for Python generation. When useFixLoop is True (default),
    runs CompileWithFixLoop so syntax errors are self-corrected before
    saving (#9).
    """
    try:
        if useFixLoop:
            codeText, metrics, compileError = CompileWithFixLoop(promptText)
            if compileError:
                print(f"[RunPyToolPipeline] Giving up after fix attempts: {compileError}")
                return {"error": compileError, "code": codeText}
        else:
            aiMessage = StreamLlmResponse(promptText)
            metrics = ExtractLlmMetrics(aiMessage)
            PrintLlmMetrics(metrics)
            codeText = ExtractPythonCode(aiMessage.content)
            ValidatePython(codeText)

        payload = BuildPythonPayload(codeText, metrics)
        SavePythonToFile(codeText, fileName)
        return payload
    except Exception as e:
        print(f"[RunPyToolPipeline] Pipeline failed: {e}")
        return {"error": str(e)}


# ------------------------------------------------------------------ #
# (#8) Caller/callee context derived from the dependency graph
# ------------------------------------------------------------------ #
def BuildCallerContext(functionName, dependencies):
    """
    Given the richer dependency graph (list of {"caller","callee","passes",
    "expects"} edges), returns a human-readable block describing who calls
    this function (and what it receives) and what this function calls (and
    what it must return to satisfy them).
    """
    calls = dependencies.get("calls", []) if isinstance(dependencies, dict) else []

    calledBy = [edge for edge in calls if edge.get("callee") == functionName]
    callsOut = [edge for edge in calls if edge.get("caller") == functionName]

    lines = []
    if calledBy:
        lines.append("Called by:")
        for edge in calledBy:
            lines.append(
                f"  - {edge.get('caller')}() passes {edge.get('passes')} "
                f"and expects this function to return: {edge.get('expects')}"
            )
    else:
        lines.append("Called by: (no recorded callers)")

    if callsOut:
        lines.append("Calls out to:")
        for edge in callsOut:
            lines.append(
                f"  - {edge.get('callee')}() — pass {edge.get('passes')}, "
                f"which returns: {edge.get('expects')}"
            )

    return "\n".join(lines)


# ------------------------------------------------------------------ #
# (#10) Execution validator
# ------------------------------------------------------------------ #
def RunAndCaptureExecution(filePath, timeoutSeconds=EXECUTION_TIMEOUT_SECONDS):
    """
    Executes the assembled project with `python filePath`, feeding empty
    stdin (so any input() calls fail fast with EOFError rather than
    hanging). Returns (success, output) where output is the combined
    stdout/stderr. A timeout with no traceback is treated as a benign
    "the program is running / waiting" case, since interactive loops
    (games, CLIs) legitimately block.
    """
    try:
        result = subprocess.run(
            [sys.executable, str(filePath)],
            input="",
            capture_output=True,
            text=True,
            timeout=timeoutSeconds,
        )
        combinedOutput = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            return True, combinedOutput
        if "Traceback (most recent call last)" in combinedOutput:
            return False, combinedOutput
        # Non-zero exit without a traceback (e.g. EOFError from empty stdin
        # on an interactive prompt) is not a code defect we can fix here.
        return True, combinedOutput
    except subprocess.TimeoutExpired as timeoutError:
        combinedOutput = (timeoutError.stdout or "") + (timeoutError.stderr or "")
        if "Traceback (most recent call last)" in combinedOutput:
            return False, combinedOutput
        return True, combinedOutput
    except Exception as e:
        return False, f"Traceback (most recent call last):\n{e}"


# ------------------------------------------------------------------ #
# Tools
# ------------------------------------------------------------------ #

def toolCreateProjectIdea(userInput: str) -> dict:
    '''create a project idea'''
    # '''If input asks to "create a project idea" or "come up with a project" from a rough user input.'''
    promptText = (
    "Your task is to convert the user's request into a software project idea.\n\n"

    f"User input:\n{userInput}\n\n"

    "Rules:\n"
    "1. Return ONLY valid JSON.\n"
    "2. The JSON must contain EXACTLY ONE key.\n"
    '3. The key MUST be named "projectIdea".\n'
    "4. Do NOT change the key name.\n"
    "5. Do NOT add spaces before or after the key.\n"
    "6. Do NOT add any other keys.\n"
    "7. The value should be a 3-6 sentence description explaining:\n"
    "   - the problem it solves\n"
    "   - the target users\n"
    "   - the main features\n\n"

    "Correct output example:\n"
    '{"projectIdea":"A simple project description."}\n\n'

    "Return ONLY the JSON object."
    )
    # promptText = (
    #     "You are a software project consultant. Based on the user's input below, "
    #     "write a single descriptive software project idea (3-6 sentences covering "
    #     "the problem it solves, target users, and core features).\n\n"
    #     f"User input: '{userInput}'\n\n"
    #     "Respond ONLY with valid JSON in exactly this shape, no extra text:\n"
    #     '{"projectIdea": "<the descriptive project idea>"}'
    # )
    if RunJsonToolPipeline(promptText, PROJECT_IDEA_FILE):
        return f"""
Project idea successfully generated.

IMPORTANT:
The requested project idea has already been completely generated and saved.
Do NOT regenerate, summarize, expand, or rewrite the project idea.
Simply tell the user where it was saved.
Saved to:
{PROJECT_IDEA_FILE}
        """
    return "Failed to create the project idea"



def toolSummarizeProjectGoal() -> dict:
    '''create a project goal'''
    # '''If input asks to "summarize the project idea" into a short project goal.'''
    raw_project_idea = LoadJsonField(
        PROJECT_IDEA_FILE, "projectIdea", fallback="There is nothing in my mind right now"
    )

    promptText = (
    "You are an API that converts a software project idea into a concise project goal.\n\n"

    f"Project idea:\n{raw_project_idea}\n\n"

    "Instructions:\n"
    "1. Read the project idea.\n"
    "2. Summarize it into ONE short, punchy project goal.\n"
    "3. The goal must be no more than TWO sentences.\n"
    "4. Keep the goal clear, specific, and implementation-focused.\n\n"

    "Output Rules:\n"
    "1. Return ONLY valid JSON.\n"
    "2. The output will be parsed using Python json.loads().\n"
    '3. The JSON must contain EXACTLY ONE key named "projectGoal".\n'
    "4. Do NOT change the key name.\n"
    "5. Do NOT add spaces before or after the key.\n"
    "6. Do NOT use different capitalization.\n"
    "7. Do NOT add any other keys.\n"
    "8. Do NOT output markdown.\n"
    "9. Do NOT output explanations.\n"
    "10. Do NOT output comments.\n\n"

    "Correct output example:\n"
    '{"projectGoal":"Create a simple command-line Rock Paper Scissors game that lets users play against the computer using clean, modular Python code."}\n\n'

    "Invalid examples:\n"
    '{"ProjectGoal":"..."}\n'
    '{"project Goal":"..."}\n'
    '{"project_goal":"..."}\n'
    '{"goal":"..."}\n\n'

    "Return ONLY the JSON object."
    )
    # promptText = (
    #     "You are a software project consultant. Summarize the descriptive project "
    #     "idea below into a single short, punchy project goal (max 2 sentences).\n\n"
    #     f"Project idea: '{raw_project_idea}'\n\n"
    #     "Respond ONLY with valid JSON in exactly this shape, no extra text:\n"
    #     '{"projectGoal": "<the short project goal>"}'
    # )
    if RunJsonToolPipeline(promptText, PROJECT_GOAL_FILE):
        return f"""
Project goal successfully generated.

IMPORTANT:
The requested project goal has already been completely generated and saved.
Do NOT regenerate, summarize, expand, or rewrite it.
Simply tell the user where it was saved.
Saved to:
{PROJECT_GOAL_FILE}
        """
    return "Failed to create the project goal"



def toolProposeArchitectures() -> dict:
    '''create a project architecture'''
    # '''If input asks to "propose architectures" or "suggest software architecture options" for a project.'''
    raw_project_idea = LoadJsonField(
        PROJECT_IDEA_FILE, "projectIdea", fallback="There is nothing in my mind right now"
    )
    project_goal_text = LoadJsonField(
        PROJECT_GOAL_FILE, "projectGoal", fallback="There is nothing specific defined yet."
    )

    # (#1) Full API contracts, not just descriptions.
    # (#4) Rich dependency graph with passes/expects per edge.
    # (#7) A frozen control-flow ("flow") spec so main() is generated from
    #      an explicit order instead of being guessed later.
    # (#5) A shared data model spec so every function agrees on one shape.
    promptText = f"""
You are an API that generates a software project architecture.

Project idea:
{raw_project_idea}

Project goal:
{project_goal_text}

Generate the complete API contract for this project.

Rules:
1. Return ONLY valid JSON.
2. The output will be parsed using Python json.loads().
3. Do NOT output markdown.
4. Do NOT output explanations.
5. Do NOT output comments.
6. Do NOT add any text before or after the JSON.
7. The JSON must contain EXACTLY these top-level keys:
   - functions
   - dependencies
   - flow
   - data_model
8. Do NOT rename any key.
9. Keep the project small (4-8 functions).
10. Every function must use the shared data model.
11. All function names must be snake_case.
12. Ensure all example_input, example_output, dependencies, and flow are internally consistent.

Required JSON schema:

{{
  "functions": [
    {{
      "name": "function_name",
      "description": "What the function does.",
      "input_params": [
        {{
          "id": "parameter_name",
          "type": "type_hint"
        }}
      ],
      "output_param": {{
        "return_type": "type_hint",
        "description": "Returned value."
      }},
      "example_input": {{
        "parameter_name": "example"
      }},
      "example_output": "example"
    }}
  ],
  "dependencies": {{
    "calls": [
      {{
        "caller": "function_name",
        "callee": "function_name",
        "passes": [
          "parameter_name"
        ],
        "expects": "return description"
      }}
    ]
  }},
  "flow": [
    "function_name"
  ],
  "data_model": {{
    "name": "ProjectState",
    "fields": {{
      "field_name": "type_hint"
    }}
  }}
}}

Return ONLY the JSON object.
"""
#     promptText = f"""
# # Role
# You are a Python API Generator. Analyze the project idea and goal below and
# output ONLY a valid JSON object representing the complete, FROZEN API
# contract for the system: every function signature, its example input/output,
# how data flows between functions, the execution order, and one shared data
# model every function will use. Do not include markdown text outside the code
# block or any conversational filler.

# # Input Data
# Project idea: '{raw_project_idea}'
# Project goal: '{project_goal_text}'

# # Constraints & Rules
# 1. **Output Format ONLY**: Return exactly one JSON object wrapped in a ```json ... ``` code block. Nothing else.
# 2. **Structure**: The JSON must contain these top-level keys: `functions`, `dependencies`, `flow`, `data_model`.
# 3. **Function Object** (each item in `functions`) must have exactly:
#    - `name`: string (snake_case)
#    - `description`: short string
#    - `input_params`: list of {{"id": <param_name>, "type": <type_hint>}}
#    - `output_param`: {{"return_type": <type_hint>, "description": <string>}}
#    - `example_input`: object showing a concrete example call (param name -> example value)
#    - `example_output`: a concrete example of exactly what this function returns for that input
# 4. **dependencies.calls**: a list of edges, each exactly:
#    {{"caller": <function_name>, "callee": <function_name>, "passes": [<param names caller sends>], "expects": <what callee must return, matching its output_param>}}
#    If a function is never called by another, omit it from `calls` (it's an entry point).
# 5. **flow**: an ordered list of function names representing the exact execution order the program's main loop should follow (repeat entries if a function is called more than once, e.g. in a loop).
# 6. **data_model**: {{"name": <ClassName>, "fields": {{<field_name>: <type_hint>, ...}}}} describing ONE shared state object that every function should read from / write to instead of inventing ad-hoc dicts. Field names must be consistent with the field names implied by every function's inputs/outputs (e.g. if one function returns a score, its `output_param` type and the `data_model` field type/name must agree).
# 7. Every `example_output` of a function must exactly match what its callers' `expects` field (in dependencies.calls) says they need — no mismatched keys (e.g. "p1" vs "player1"), no mismatched types (e.g. int vs string).
# 8. Keep the whole system to a SMALL number of functions (aim for 4-8 total). This is a strict budget: a smaller, correct contract is far more valuable than a large one that gets truncated.
# """

    if RunJsonToolPipeline(promptText, PROJECT_ARCHITECTURES_FILE):
        return f"""
Architectures successfully generated.

IMPORTANT:
The requested software architecture / API contract has already been completely
generated and saved (functions, dependency graph, execution flow, and shared
data model). Do NOT regenerate or rewrite it manually.
Simply tell the user where it was saved.
Saved to:
{PROJECT_ARCHITECTURES_FILE}
        """
    return "Failed to create the architectural proposal."



def toolGenerateDataModel() -> dict:
    '''create the data model'''
    # '''If input asks to "generate the data model" or "create the shared state class" for the project, after architectures have been proposed.'''
    # (#5) Generate one shared data model class every function/main will use.
    data_model_spec = LoadJsonField(PROJECT_ARCHITECTURES_FILE, "data_model", fallback=None)
    functions = LoadJsonField(PROJECT_ARCHITECTURES_FILE, "functions", fallback=[])

    if not data_model_spec:
        return f"No 'data_model' found in {PROJECT_ARCHITECTURES_FILE}. Run toolProposeArchitectures first."

    promptText = f"""
You are an API that generates Python code.

Task:
Generate ONE shared data model class.

Data Model Specification:
{json.dumps(data_model_spec, indent=2)}

Functions using this model:
{json.dumps(functions, indent=2)}

Requirements:
1. Generate exactly ONE class.
2. Use either @dataclass or typing.TypedDict, whichever best matches the specification.
3. Include all required imports.
4. The class name MUST exactly match data_model.name.
5. The fields MUST exactly match data_model.fields.
6. Field names and types must not be changed.
7. Do NOT add extra fields.
8. Do NOT add methods.
9. Do NOT define any other classes.
10. Do NOT define any functions.
11. Do NOT include comments.
12. Do NOT include docstrings.
13. Do NOT include example code.
14. The generated code must be valid Python.

Output Rules:
- Return ONLY Python code.
- No markdown.
- No ```python fences.
- No explanations.
- No text before or after the code.
"""
#     promptText = f"""
# You are an expert Python software engineer.

# Generate ONLY a single shared data model class for this project, using
# either @dataclass or typing.TypedDict — pick whichever fits the spec best.

# Data Model Spec:
# {json.dumps(data_model_spec, indent=2)}

# For context, here are all the functions that will use this shared model
# (so field names/types must be consistent with what they produce/consume):
# {json.dumps(functions, indent=2)}

# Requirements:
# - Include necessary imports (e.g. dataclasses.dataclass or typing.TypedDict).
# - Class name must exactly match data_model.name.
# - Field names and types must exactly match data_model.fields.
# - Do NOT define any other classes or functions.
# - Do NOT include usage examples.

# Output Rules:
# - Return ONLY the Python code (imports + one class).
# - No markdown, no ```python fences, no explanations.
# """

    result = RunPyToolPipeline(promptText, PROJECT_DATA_MODEL_FILE)
    if "error" in result:
        return f"Failed to generate the shared data model: {result['error']}"

    return f"""
Shared data model successfully generated.

IMPORTANT:
The shared data model class has already been generated and saved. All
subsequent function generation will import and use this class. Do NOT
regenerate it manually.
Saved to:
{PROJECT_DATA_MODEL_FILE}
    """



def toolCreateFunctionScript() -> dict:
    '''create a function script'''
    # """
    # Generate Python function implementations for every function defined in
    # project_architectures.json -> result.functions, using the full contract
    # (all signatures, the dependency graph, this function's specific
    # callers/callees, and the shared data model) so functions are generated
    # consistently instead of in isolation.
    # """
    functions = LoadJsonField(PROJECT_ARCHITECTURES_FILE, "functions", fallback=None)
    if not functions:
        return f"Could not find 'functions' in {PROJECT_ARCHITECTURES_FILE}."

    dependencies = LoadJsonField(PROJECT_ARCHITECTURES_FILE, "dependencies", fallback={})
    project_goal_text = LoadJsonField(
        PROJECT_GOAL_FILE, "projectGoal", fallback="There is nothing specific defined yet."
    )

    # (#5) Shared data model, if it's been generated, is included verbatim
    # so every function is written against the same object.
    data_model_code = ""
    try:
        with open(PROJECT_DATA_MODEL_FILE, "r", encoding="utf-8") as f:
            data_model_code = f.read().strip()
    except FileNotFoundError:
        print(f"[toolCreateFunctionScript] No data model found at {PROJECT_DATA_MODEL_FILE} yet; proceeding without it.")

    functionCounter = 0
    generated = []
    failed = []

    dataModelClassMatch = re.search(r"class\s+(\w+)", data_model_code) if data_model_code else None
    dataModelClassName = dataModelClassMatch.group(1) if dataModelClassMatch else None

    for function in functions:
        functionCounter += 1

        # (#8) This function's specific callers/callees, derived from the graph.
        callerContext = BuildCallerContext(function["name"], dependencies)

        # (#2) + (#3) The complete, frozen function list + dependency graph
        # are sent alongside the target function, so the model can see how
        # every piece fits together instead of inventing its own shapes.
        promptText = f"""
You are an API that generates Python code.

Task:
Generate exactly ONE Python function.

Function name:
{function['name']}

Project Goal:
{project_goal_text}

Shared Data Model:
{data_model_code if data_model_code else "None"}

Project Functions (context only):
{json.dumps(functions, indent=2)}

Dependencies:
{json.dumps(dependencies, indent=2)}

Caller/Callee Information:
{callerContext}

Function Specification:
{json.dumps(function, indent=2)}

Requirements:
1. Generate ONLY the function "{function['name']}".
2. Match the specification exactly.
3. Match example_input and example_output exactly.
4. Preserve all parameter names.
5. Preserve all return types.
6. Preserve all key names.
7. Use type hints.
8. Include a docstring.
9. If a shared data model exists, import it:
   from data_model import {dataModelClassName if dataModelClassName else "ProjectState"}
10. Use the shared data model instead of redefining it.
11. Do NOT call the function.
12. Do NOT generate helper functions.
13. Do NOT generate classes.
14. The code must be valid Python.

Output Rules:
- Return ONLY Python code.
- No markdown.
- No ```python fences.
- No explanations.
- No comments outside the function.
- The response must start with def
"""
#         promptText = f"""
# You are an expert Python software engineer.

# Generate ONLY ONE Python function: {function['name']}.

# Project Goal:
# {project_goal_text}

# Shared Data Model (import and use this; do not redefine it):
# {data_model_code if data_model_code else "(none generated yet — use plain typed parameters)"}

# Complete Function Contract List (for context only — implement ONLY {function['name']}):
# {json.dumps(functions, indent=2)}

# Full Dependency Graph:
# {json.dumps(dependencies, indent=2)}

# This Function's Callers/Callees:
# {callerContext}

# Function Specification (the one to implement):
# {json.dumps(function, indent=2)}

# Requirements:
# - Implement exactly this function, matching its example_input/example_output shape exactly.
# - Include type hints and a docstring.
# - If a shared data model was provided, import it with:
#   from data_model import {dataModelClassName if dataModelClassName else "<ClassName>"}
#   (use the exact class name shown in the Shared Data Model block above, if any)
# - Match the exact keys/types your callers expect (see "This Function's Callers/Callees" above) —
#   do not invent alternate key names or types.
# - Do NOT call the function.
# - Do NOT generate any other helper functions.

# Output Rules:
# - Return ONLY valid Python.
# - No markdown, no ```python fences, no explanations, no comments outside the function.
# - The first character of your response must be 'd' from the word 'def' (or 'f'/'i' if a
#   leading `from ...` / `import ...` line for the data model is required first).
# """

        outputFile = f"{PROJECT_SCRIPTS}/{function['name']}.py"
        result = RunPyToolPipeline(promptText, outputFile)  # (#9) compile-and-fix loop is used by default

        if "error" in result:
            failed.append(function["name"])
            print(f"Function {functionCounter} ('{function['name']}') FAILED to compile after retries.")
        else:
            generated.append(function["name"])
            print(f"Function {functionCounter} generation done")
            print(f"Function name: '{function['name']}'")
            print(f"Function file: '{outputFile}'\n")

    return f"""
Generated {len(generated)}/{len(functions)} functions.
{f"Failed to compile: {failed}" if failed else "All functions compiled successfully."}

Saved into:
{PROJECT_SCRIPTS}
"""



def toolValidateFunctionInterfaces() -> dict:
    '''validate the function'''
    # """
    # If input asks to "validate interfaces" or "check for mismatches" between
    # the generated functions before assembly. Reads every generated function,
    # asks the LLM to find interface mismatches (wrong return keys/types,
    # missing parameters, unused functions), and regenerates only the
    # functions flagged as broken.
    # """
    functions = LoadJsonField(PROJECT_ARCHITECTURES_FILE, "functions", fallback=None)
    dependencies = LoadJsonField(PROJECT_ARCHITECTURES_FILE, "dependencies", fallback={})
    if not functions:
        return f"Could not find 'functions' in {PROJECT_ARCHITECTURES_FILE}."

    allFunctionCode = {}
    for function in functions:
        filename = f"{PROJECT_SCRIPTS}/{function['name']}.py"
        try:
            with open(filename, "r", encoding="utf-8") as f:
                allFunctionCode[function["name"]] = f.read()
        except FileNotFoundError:
            allFunctionCode[function["name"]] = "# MISSING — file was not generated"

    # (#6) A dedicated validation pass over ALL functions together.
    validationPrompt = f"""
You are an API that validates generated Python code.

API Contract:
{json.dumps({"functions": functions, "dependencies": dependencies}, indent=2)}

Generated Functions:
{json.dumps(allFunctionCode, indent=2)}

Validation Rules:
1. Compare every generated function against the API contract.
2. Verify function names.
3. Verify parameters.
4. Verify return types.
5. Verify return keys.
6. Verify example_output matches the implementation.
7. Verify caller/callee compatibility.
8. Verify dependencies are satisfied.
9. Verify no required function is missing.
10. Identify unused or disconnected functions.
11. Identify obvious type inconsistencies.
12. If a function has multiple problems, report each separately.

Output Rules:
1. Return ONLY valid JSON.
2. The output will be parsed using Python json.loads().
3. Do NOT output markdown.
4. Do NOT output explanations.
5. Do NOT output comments.
6. Do NOT output any text before or after the JSON.
7. The JSON must contain EXACTLY these keys:
   - issues
   - clean_functions
8. Do NOT rename any key.

Required JSON schema:

{
  "issues": [
    {
      "function": "function_name",
      "problem": "short description"
    }
  ],
  "clean_functions": [
    "function_name"
  ]
}

If no issues are found, return:

{
  "issues": [],
  "clean_functions": [
    "function_name"
  ]
}
"""
#     validationPrompt = f"""
# You are a strict code reviewer. Here is the frozen API contract and every
# generated function for a project.

# API Contract (functions + dependency graph):
# {json.dumps({"functions": functions, "dependencies": dependencies}, indent=2)}

# Generated Functions:
# {json.dumps(allFunctionCode, indent=2)}

# Find:
# - interface mismatches (return keys/types that don't match what callers expect)
# - wrong return values (doesn't match example_output shape)
# - missing parameters
# - unused/disconnected functions
# - type inconsistencies

# Respond ONLY with valid JSON, no other text, in exactly this shape:
# {{
#   "issues": [
#     {{"function": "<function_name>", "problem": "<short description>"}}
#   ],
#   "clean_functions": ["<function_name>", ...]
# }}
# """

    validationResult = RunJsonToolPipeline(validationPrompt, PROJECT_VALIDATION_FILE)
    if "error" in validationResult:
        return f"Validation pass failed: {validationResult['error']}"

    issues = validationResult.get("result", {}).get("issues", [])
    if not issues:
        return f"""
Validation complete: no interface mismatches found across {len(functions)} functions.
Report saved to:
{PROJECT_VALIDATION_FILE}
        """

    functionsByName = {f["name"]: f for f in functions}
    project_goal_text = LoadJsonField(
        PROJECT_GOAL_FILE, "projectGoal", fallback="There is nothing specific defined yet."
    )

    fixed = []
    stillBroken = []

    for _ in range(MAX_VALIDATION_FIX_ATTEMPTS):
        remainingIssues = []
        for issue in issues:
            functionName = issue.get("function")
            function = functionsByName.get(functionName)
            if not function:
                continue

            callerContext = BuildCallerContext(functionName, dependencies)
            fixPrompt = f"""
You are an API that fixes Python code.

Task:
Fix exactly ONE Python function.

Project Goal:
{project_goal_text}

Function Specification:
{json.dumps(function, indent=2)}

Caller/Callee Information:
{callerContext}

Current Function:
{allFunctionCode.get(functionName, "")}

Problem:
{issue.get("problem")}

Requirements:
1. Fix ONLY the reported problem.
2. Do NOT change the function name.
3. Do NOT change the parameter list.
4. Do NOT change the return type.
5. Preserve the overall behavior.
6. Match the Function Specification exactly.
7. Match example_input exactly.
8. Match example_output exactly.
9. Preserve all expected key names and value types.
10. Do NOT generate helper functions.
11. Do NOT generate classes.
12. The code must be valid Python.

Output Rules:
- Return ONLY Python code.
- No markdown.
- No ```python fences.
- No explanations.
- No comments outside the function.
- The response must start with def
"""
#             fixPrompt = f"""
# You are an expert Python software engineer fixing an interface bug.

# Project Goal:
# {project_goal_text}

# Function Specification (frozen contract — do not change its meaning):
# {json.dumps(function, indent=2)}

# This Function's Callers/Callees:
# {callerContext}

# Current (broken) implementation:
# {allFunctionCode.get(functionName, '')}

# Problem identified by review:
# {issue.get('problem')}

# Requirements:
# - Fix ONLY the interface problem described above.
# - Keep the function name, parameters, and overall behavior intent the same.
# - Match example_input/example_output exactly.

# Output Rules:
# - Return ONLY valid Python for this one function.
# - No markdown, no ```python fences, no explanations.
# - The first character of your response must be 'd' from the word 'def' (or an
#   import line if required first).
# """
            outputFile = f"{PROJECT_SCRIPTS}/{functionName}.py"
            result = RunPyToolPipeline(fixPrompt, outputFile)
            if "error" in result:
                remainingIssues.append(issue)
                stillBroken.append(functionName)
            else:
                allFunctionCode[functionName] = result["code"]
                fixed.append(functionName)

        issues = remainingIssues
        if not issues:
            break

    return f"""
Validation complete.
Issues found: {len(fixed) + len(set(stillBroken))}
Regenerated/fixed: {fixed if fixed else "none"}
{f"Still unresolved after {MAX_VALIDATION_FIX_ATTEMPTS} fix attempt(s): {list(set(stillBroken) - set(fixed))}" if stillBroken else ""}

Full report saved to:
{PROJECT_VALIDATION_FILE}
"""



def toolAssembleProject() -> dict:
    '''Assemble the project'''
    # """
    # Assemble the project: generate main() FROM the frozen execution 'flow'
    # spec (not by guessing), assemble every generated file plus the shared
    # data model into project.py, compile it, then run it and self-heal on
    # any traceback (#9, #10).
    # """
    PROJECT_MAIN_FILE = f"{PROJECT_SCRIPTS}/main.py"
    PROJECT_OUTPUT_FILE = f"{PROJECT_SCRIPTS}/project.py"

    functions = LoadJsonField(PROJECT_ARCHITECTURES_FILE, "functions", fallback=None)
    dependencies = LoadJsonField(PROJECT_ARCHITECTURES_FILE, "dependencies", fallback={})
    flow = LoadJsonField(PROJECT_ARCHITECTURES_FILE, "flow", fallback=[])
    if not functions:
        return f"Could not find 'functions' in {PROJECT_ARCHITECTURES_FILE}."

    project_goal = LoadJsonField(PROJECT_GOAL_FILE, "projectGoal", fallback="")

    data_model_code = ""
    try:
        with open(PROJECT_DATA_MODEL_FILE, "r", encoding="utf-8") as f:
            data_model_code = f.read().strip()
    except FileNotFoundError:
        pass

    # ------------------------------------------------------------
    # Read every generated function
    # ------------------------------------------------------------
    functionCode = ""
    for function in functions:
        filename = f"{PROJECT_SCRIPTS}/{function['name']}.py"
        try:
            with open(filename, "r", encoding="utf-8") as f:
                functionCode += f.read().rstrip() + "\n\n"
        except FileNotFoundError:
            print(f"Missing script: {filename}")

    # ------------------------------------------------------------
    # (#7) Generate main.py directly from the frozen `flow` spec,
    # instead of letting the model infer call order on its own.
    # ------------------------------------------------------------
    promptText = f"""
You are an API that generates Python code.

Task:
Generate exactly ONE function: main()

Project Goal:
{project_goal}

Shared Data Model:
{data_model_code if data_model_code else "None"}

Function Specifications:
{json.dumps(functions, indent=2)}

Dependencies:
{json.dumps(dependencies, indent=2)}

Execution Flow:
{json.dumps(flow, indent=2)}

Requirements:
1. Generate ONLY:
   def main():
2. Use the existing functions.
3. Do NOT redefine any function.
4. Follow the Execution Flow exactly.
5. Do NOT skip any function.
6. Do NOT reorder function calls.
7. Do NOT invent additional function calls.
8. Handle return values exactly as specified.
9. Use the shared data model if provided.
10. The generated code must be valid Python.

Append exactly:

if __name__ == "__main__":
    main()

Output Rules:
- Return ONLY Python code.
- No markdown.
- No ```python fences.
- No explanations.
- No comments outside the code.
- The response must start with either:
  from
  import
  def
"""
#     promptText = f"""
# You are an expert Python software engineer.

# Generate ONLY the application's main() function. The functions already
# exist — do NOT regenerate them.

# Project Goal:
# {project_goal}

# Shared Data Model (import and use this; do not redefine it):
# {data_model_code if data_model_code else "(none — use plain variables)"}

# Function Specifications (frozen contracts):
# {json.dumps(functions, indent=2)}

# Dependency Graph:
# {json.dumps(dependencies, indent=2)}

# FROZEN Execution Flow (call functions in EXACTLY this order; repeat as shown for loops):
# {json.dumps(flow, indent=2)}

# Requirements:
# - Generate ONLY: def main():
# - Follow the Execution Flow order exactly — do not reorder, skip, or invent extra calls.
# - Use the existing functions and the shared data model exactly as their contracts specify.
# - Handle return values using the exact keys/types shown in each function's example_output.
# - Do not redefine any function.
# - End with:

# if __name__ == "__main__":
#     main()

# Output Rules:
# - Return ONLY Python.
# - No markdown, no explanations, no comments outside the code.
# - The first character must be 'd' (or an import line if required first).
# """

    mainResult = RunPyToolPipeline(promptText, PROJECT_MAIN_FILE)
    if "error" in mainResult:
        return f"Failed to generate main.py: {mainResult['error']}"
    print(f"Generated {PROJECT_MAIN_FILE}")

    # ------------------------------------------------------------
    # Assemble project.py: data model + functions + main
    # ------------------------------------------------------------
    def AssembleFullProject():
        projectCode = ""
        if data_model_code:
            projectCode += data_model_code.rstrip() + "\n\n"
        for function in functions:
            filename = f"{PROJECT_SCRIPTS}/{function['name']}.py"
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    code = f.read()
                # strip a redundant "from data_model import ..." line since
                # everything now lives in one assembled file
                code = re.sub(r"^from data_model import.*$\n?", "", code, flags=re.MULTILINE)
                projectCode += code.rstrip() + "\n\n"
            except FileNotFoundError:
                print(f"Skipping missing file: {filename}")
        try:
            with open(PROJECT_MAIN_FILE, "r", encoding="utf-8") as f:
                mainCode = re.sub(r"^from data_model import.*$\n?", "", f.read(), flags=re.MULTILINE)
                projectCode += mainCode
        except FileNotFoundError:
            return None
        return projectCode

    projectCode = AssembleFullProject()
    if projectCode is None:
        return "main.py was not generated."

    try:
        ValidatePython(projectCode)
    except SyntaxError as e:
        return f"Assembled project.py failed to compile: {e}"

    try:
        SavePythonToFile(projectCode, PROJECT_OUTPUT_FILE)
        print(f"Saving the file: {PROJECT_OUTPUT_FILE}")
    except Exception as e:
        return f"Failed assembling project.py: {e}"

    # ------------------------------------------------------------
    # (#10) Execution validator / self-healing run loop
    # ------------------------------------------------------------
    functionsByName = {f["name"]: f for f in functions}
    executionLog = []

    for attempt in range(1, MAX_EXECUTION_FIX_ATTEMPTS + 2):
        success, output = RunAndCaptureExecution(PROJECT_OUTPUT_FILE)
        executionLog.append(f"Attempt {attempt}: {'OK' if success else 'FAILED'}")

        if success:
            return f"""
Project assembled and executed successfully.

Generated:
- {PROJECT_MAIN_FILE}

Assembled:
- {PROJECT_OUTPUT_FILE}

Execution log:
{chr(10).join(executionLog)}
"""

        print(f"[toolAssembleProject] Execution attempt {attempt} failed:\n{output}")
        if attempt > MAX_EXECUTION_FIX_ATTEMPTS:
            break

        # Try to identify which function the traceback points at, by
        # matching function names appearing in the traceback text.
        suspectName = None
        for name in functionsByName:
            if re.search(rf"\b{re.escape(name)}\b", output):
                suspectName = name
                break

        if suspectName is None:
            # Can't localize the bug to one function — try fixing main().
            fixPrompt = f"""
You are an API that fixes Python code.

Task:
Fix exactly ONE function: main()

Python Traceback:
{output}

Project Goal:
{project_goal}

Function Specifications:
{json.dumps(functions, indent=2)}

Execution Flow:
{json.dumps(flow, indent=2)}

Current main():
{open(PROJECT_MAIN_FILE, encoding="utf-8").read()}

Requirements:
1. Fix ONLY the error shown in the traceback.
2. Modify ONLY main().
3. Do NOT modify any other function.
4. Do NOT invent new functions.
5. Do NOT change any function signature.
6. Follow the Execution Flow exactly.
7. Use the existing functions exactly as specified.
8. Preserve the intended behavior.
9. The generated code must be valid Python.

Append exactly:

if __name__ == "__main__":
    main()

Output Rules:
- Return ONLY Python code.
- No markdown.
- No ```python fences.
- No explanations.
- No comments outside the code.
- The response must begin with:
  def
"""
#             fixPrompt = f"""
# The assembled project below raised this traceback when run:

# {output}

# Project Goal:
# {project_goal}

# Function Specifications:
# {json.dumps(functions, indent=2)}

# Execution Flow:
# {json.dumps(flow, indent=2)}

# Current main():
# {open(PROJECT_MAIN_FILE, encoding="utf-8").read()}

# Fix ONLY main() so the traceback above no longer occurs, while still
# following the Execution Flow and using the existing functions correctly.

# Output Rules:
# - Return ONLY Python for main() (ending with the if __name__ == "__main__": block).
# - No markdown, no explanations.
# - The first character must be 'd'.
# """
            fixResult = RunPyToolPipeline(fixPrompt, PROJECT_MAIN_FILE)
        else:
            function = functionsByName[suspectName]
            callerContext = BuildCallerContext(suspectName, dependencies)
            currentCode = ""
            try:
                with open(f"{PROJECT_SCRIPTS}/{suspectName}.py", encoding="utf-8") as f:
                    currentCode = f.read()
            except FileNotFoundError:
                pass

            fixPrompt = f"""
The assembled project raised this traceback when run:

{output}

The function most likely responsible is: {suspectName}

Function Specification (frozen contract):
{json.dumps(function, indent=2)}

This Function's Callers/Callees:
{callerContext}

Current implementation:
{currentCode}

Fix ONLY this function so the traceback above no longer occurs, while
still matching its example_input/example_output contract.

Output Rules:
- Return ONLY valid Python for this one function.
- No markdown, no explanations.
- The first character must be 'd' (or an import line if required first).
"""
            fixResult = RunPyToolPipeline(fixPrompt, f"{PROJECT_SCRIPTS}/{suspectName}.py")

        if "error" in fixResult:
            print(f"[toolAssembleProject] Fix attempt {attempt} itself failed to compile: {fixResult['error']}")
            break

        # Re-assemble with the fix applied and try again next loop iteration.
        projectCode = AssembleFullProject()
        if projectCode is None:
            break
        try:
            ValidatePython(projectCode)
            SavePythonToFile(projectCode, PROJECT_OUTPUT_FILE)
        except SyntaxError as e:
            print(f"[toolAssembleProject] Re-assembled project failed to compile: {e}")
            break

    return f"""
Project assembled, but execution self-healing did not fully succeed.

Generated:
- {PROJECT_MAIN_FILE}

Assembled:
- {PROJECT_OUTPUT_FILE}

Execution log:
{chr(10).join(executionLog)}

Last output:
{output}
"""

import time

@tool
def toolBuildProject(userInput: str) -> dict:
    """Run the entire project generation pipeline."""

    # toolCreateProjectIdea(userInput)
    # time.sleep(5)
    # input("HumanInterrupt01")
    # toolSummarizeProjectGoal()
    # time.sleep(5)
    input("HumanInterrupt02")
    toolProposeArchitectures()
    time.sleep(5)
    input("HumanInterrupt03")
    toolGenerateDataModel()
    time.sleep(5)
    input("HumanInterrupt04")
    toolCreateFunctionScript()
    time.sleep(5)
    input("HumanInterrupt05")
    toolValidateFunctionInterfaces()
    time.sleep(5)
    input("HumanInterrupt06")
    toolAssembleProject()
    time.sleep(5)
    input("HumanInterrupt07")

    return {
        "status": "success",
        "message": "Project generated successfully."
    }
# ------------------------------------------------------------------ #
# Tool registry
# ------------------------------------------------------------------ #
toolsAdvance = [
    # toolCreateProjectIdea,
    # toolSummarizeProjectGoal,
    # toolProposeArchitectures,
    # toolGenerateDataModel,
    # toolCreateFunctionScript,
    # toolValidateFunctionInterfaces,
    # toolAssembleProject,
    toolBuildProject
]
tools = toolsAdvance


def ToolsList():
    global tools
    return tools