"""
Session Resume

Parses session logs written by Log/turn_logger.py (format_turn) back into
(userInput, agentOutput) turns, so /resume can seed them into agent memory.
"""

import re

from Log.log_utils import PrintFunctionName

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
MAX_RESUME_TURNS = 20  # keep only the most recent turns to bound prompt size
SUB_SEPARATOR = "-" * 60
SEPARATOR = "=" * 60
NO_OUTPUT_TEXT = "(No output or command handled)"

USER_INPUT_PREFIX = "UserInput      : "
TOOL_CALLS_PREFIX = "Tool Calls     : "
AGENT_OUTPUT_PREFIX = "AgentOutput    : "

LOG_PREFIX_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - \w+ - ")
TURN_START_PATTERN = re.compile(r"^UserInputCount : \d+\s*$")
TOOL_NAME_PATTERN = re.compile(r"^([^(]+)\(")


# --------------------------------------------------------------------------- #
# Functions
# --------------------------------------------------------------------------- #

def SplitTurnBlocks(lines: list) -> list:
    """Split log lines into blocks, one per 'UserInputCount : N' header."""
    blocks = []
    current = None
    for line in lines:
        if TURN_START_PATTERN.match(line):
            current = []
            blocks.append(current)
        elif current is not None:
            current.append(line)
    return blocks


def ReadField(block: list, prefix: str) -> str:
    """Return a (possibly multi-line) field value, ending at the next 60-dash separator."""
    for idx, line in enumerate(block):
        if line.startswith(prefix):
            valueLines = [line[len(prefix):]]
            for nextLine in block[idx + 1:]:
                if nextLine.strip() in (SUB_SEPARATOR, SEPARATOR):
                    break
                valueLines.append(nextLine)
            return "\n".join(valueLines).strip()
    return ""


def ReadToolNames(block: list) -> list:
    """Return the tool names from the 'Tool Calls' lines of a block."""
    names = []
    for line in block:
        if line.startswith(TOOL_CALLS_PREFIX):
            match = TOOL_NAME_PATTERN.match(line[len(TOOL_CALLS_PREFIX):])
            if match:
                names.append(match.group(1).strip())
    return names


@PrintFunctionName
def ParseSessionLog(logFilePath: str, maxTurns: int = MAX_RESUME_TURNS) -> list:
    """Parse a session log into a list of (userInput, agentOutput) tuples.

    Command-only turns (e.g. /resume itself) and turns with no output are skipped.
    Tool usage is folded into the agent output as a short note, since tool
    results are truncated in the log and cannot be rebuilt as ToolMessages.
    """
    with open(logFilePath, "r", encoding="utf-8", errors="ignore") as f:
        lines = [LOG_PREFIX_PATTERN.sub("", line.rstrip("\n")) for line in f]

    turns = []
    for block in SplitTurnBlocks(lines):
        userInput = ReadField(block, USER_INPUT_PREFIX)
        agentOutput = ReadField(block, AGENT_OUTPUT_PREFIX)
        if not userInput or not agentOutput or agentOutput == NO_OUTPUT_TEXT:
            continue

        toolNames = ReadToolNames(block)
        if toolNames:
            agentOutput = f"[tools used: {', '.join(toolNames)}]\n{agentOutput}"

        turns.append((userInput, agentOutput))

    if maxTurns and len(turns) > maxTurns:
        turns = turns[-maxTurns:]
    return turns
