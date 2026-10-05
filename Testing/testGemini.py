"""
Test which Gemini models work via LangChain (ChatGoogleGenerativeAI).

Run from repo root:
    source venv/bin/activate
    python Testing/testGemini.py

Requires GOOGLE_API_KEY in the environment.
"""

import os
import sys
import time

from langchain_google_genai import ChatGoogleGenerativeAI

PROMPT = "Reply with just: OK"

# Fixed candidates, tested in addition to whatever the API lists,
# so that non-existent / retired names also show up in the report.
CANDIDATE_MODELS = [
    "gemini-3.6-flash",          # current default in Langchain/agent.py
    "gemini-3.5-flash",
    "gemini-3.5-pro",
    "gemini-3-flash",
    "gemini-3-pro",
    "gemini-3-flash-preview",
    "gemini-3-pro-preview",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
]


def ListAvailableModels():
    """Return Gemini model names that the API says support generateContent."""
    try:
        from google import genai
        client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        names = []
        for model in client.models.list():
            actions = getattr(model, "supported_actions", None) or []
            name = model.name.removeprefix("models/")
            if "generateContent" in actions and name.startswith("gemini"):
                names.append(name)
        return sorted(names)
    except Exception as e:
        print(f"Could not list models from API: {FirstLine(e)}")
        return []


def FirstLine(error):
    text = str(error).strip() or type(error).__name__
    return text.splitlines()[0][:160]


def TestModel(modelName):
    """Invoke a model once. Returns (ok, latencySec, replyOrError)."""
    start = time.time()
    try:
        llm = ChatGoogleGenerativeAI(
            model=modelName, max_tokens=1024, max_retries=0, timeout=30
        )
        response = llm.invoke(PROMPT)
        reply = (response.text or "").strip().replace("\n", " ")
        if not reply:
            return False, time.time() - start, "Empty response"
        return True, time.time() - start, reply[:40]
    except Exception as e:
        return False, time.time() - start, f"{type(e).__name__}: {FirstLine(e)}"


def PrintReport(working, notWorking):
    print("\n" + "=" * 90)
    print(f"WORKING ({len(working)})")
    print("=" * 90)
    for name, latency, reply in working:
        print(f"  {name:<40} {latency:6.2f}s   {reply}")

    print("\n" + "=" * 90)
    print(f"NOT WORKING ({len(notWorking)})")
    print("=" * 90)
    for name, latency, error in notWorking:
        print(f"  {name:<40} {error}")

    print(f"\nTotal tested: {len(working) + len(notWorking)}  |  "
          f"Working: {len(working)}  |  Not working: {len(notWorking)}")


def Main():
    if not os.environ.get("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY is not set.")
        sys.exit(1)

    apiModels = ListAvailableModels()
    print(f"API lists {len(apiModels)} gemini models supporting generateContent.")

    # Candidates first (keeps order), then API-listed extras
    models = list(dict.fromkeys(CANDIDATE_MODELS + apiModels))

    working, notWorking = [], []
    for i, name in enumerate(models, 1):
        ok, latency, detail = TestModel(name)
        tag = "OK  " if ok else "FAIL"
        print(f"[{i:>2}/{len(models)}] {tag} {name}")
        (working if ok else notWorking).append((name, latency, detail))

    PrintReport(working, notWorking)


if __name__ == "__main__":
    Main()
