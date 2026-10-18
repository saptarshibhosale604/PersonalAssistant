
import pathlib
path = pathlib.Path("Langchain/agent.py")
code = path.read_text(encoding="utf-8")
target = "    for streamMode, chunk in AGENT.stream("
replacement = """    print("--- DEBUG: EXACT LLM PAYLOAD --- ")
    for m in messages:
        print(f"[{type(m).__name__}]: {m.content}")
    print("---------------------------------")
    for streamMode, chunk in AGENT.stream("""

if target in code:
    code = code.replace(target, replacement, 1)
    path.write_text(code, encoding="utf-8")
    print("SUCCESS")
else:
    print("NOT FOUND")

