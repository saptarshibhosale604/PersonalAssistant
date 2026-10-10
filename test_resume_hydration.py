"""
Test script for /resume: session log parsing and agent memory seeding.
Run from the repo root: python test_resume_hydration.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import Langchain.agent as Agent
from Langchain.sessionResume import ParseSessionLog

SAMPLE_LOG_PATH = "./Log/SessionLog/session_0003_2026-10-09_21-10-06.log"
TEST_MODE_LLM = "local-1b"  # no API key / network needed to build the agent


def test_parse_session_log():
    """Parse session_0003 and check its first turn."""
    turns = ParseSessionLog(SAMPLE_LOG_PATH)
    print(f"Parsed {len(turns)} turns from {SAMPLE_LOG_PATH}")
    for idx, (user, ai) in enumerate(turns, start=1):
        print(f"  Turn {idx}:")
        print(f"    User: {user[:60]!r}")
        print(f"    AI:   {ai[:60]!r}")

    assert len(turns) >= 1, "Expected at least one turn"
    firstUser, firstAi = turns[0]
    assert firstUser.startswith("You are using POWERSHELL CMD."), firstUser
    assert "just say hiiii and then use 3 tools" in firstUser, firstUser
    assert "Hiiiiii" in firstAi, firstAi
    assert "[tools used: ReadProjectContext, toolExecuteBash, toolSearchWikipedia]" in firstAi, firstAi
    print("✓ ParseSessionLog test passed\n")
    return turns


def test_seed_thread_history(turns):
    """Seed the turns into a thread, then force an agent rebuild and check they survive."""
    threadId = 99
    loaded = Agent.SeedThreadHistory(threadId, TEST_MODE_LLM, turns)
    assert loaded == len(turns)

    # Switching LLM mode rebuilds AGENT; memory must survive via the shared checkpointer
    Agent.UpdateAgent("local-3b")

    config = {"configurable": {"thread_id": f"thread-{threadId}"}}
    messages = Agent.AGENT.get_state(config).values.get("messages", [])
    assert len(messages) == 2 * len(turns), f"Expected {2 * len(turns)} messages, got {len(messages)}"
    assert "just say hiiii" in messages[0].content
    print(f"✓ SeedThreadHistory test passed ({len(messages)} messages in thread-{threadId})\n")


if __name__ == "__main__":
    parsedTurns = test_parse_session_log()
    test_seed_thread_history(parsedTurns)
    print("All resume tests passed successfully! ✓")
