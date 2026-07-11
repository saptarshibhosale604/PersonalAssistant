"""
Agent module.

Builds and manages a LangChain agent that can run against different LLM
backends (local Ollama models or OpenAI) and routes tool calls through a
human-in-the-loop (HITL) approval middleware.
"""

import os

from Log.log_utils import PrintFunctionName

@PrintFunctionName
def RemoveSpaces(inputString: str) -> str:
    """Remove all whitespace characters from a string.

    Used to sanitize API keys that were pasted with accidental line-wrap
    spaces.
    """
    return inputString.replace(" ", "")


# --------------------------------------------------------------------------- #
# API keys
# --------------------------------------------------------------------------- #
# SECURITY NOTE: these are live credentials committed directly in source.
# Rotate/revoke them and load from a secrets manager or .env file instead
# (see "Optional Suggestions" in the accompanying review).
OPENAI_KEY = (
    "sk-proj-zP6XLa1m5gtlBcXJCaHZGmAvXEvUrP 5ATJSPBfLRdEuF-vSroLAG4V0zBdpwPz9PTXe9rM0-CgT3BlbkFJ83"
    " AZyS7Zds5OT4G7S7MJslTok1O8P7ftX6Zz_IvdtMsy_CnjJeBoOv-o-G5t13-1Yw20ei_BwA"
)  # myTestKey08, saptarshibhosale604@gmail.com
TAVILY_KEY = "tvly-kX76LCz C36oih0u9COcf6oa 53A47MX0g"

os.environ["OPENAI_API_KEY"] = RemoveSpaces(OPENAI_KEY)
os.environ["TAVILY_API_KEY"] = RemoveSpaces(TAVILY_KEY)

# Imported after the API-key env vars are set above, since some provider
# SDKs read credentials from the environment at import time.
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_ollama.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from Log.custom_logger import logger
import Langchain.Tools.toolsManager as toolsManager


# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0
DEFAULT_MAX_RETRIES = 1
BANNER_WIDTH = 60

JARVIS_SYSTEM_PROMPT = (
    "You are an assistance like a JARVIS from Iron Man. "
    "Your name is RPI. Your master name is SSB"
)
BUDDY_SYSTEM_PROMPT = (
    "You are a chearful, intelligent, naughty, best friend, sarcastic character. "
    "Your name is RPI. The user name is SSB, who is your best buddy"
)

# Tools that require explicit human approval before execution.
TOOL_INTERRUPT_POLICY = {
    # toolsTest
    "toolTestGetWeather": True,
    "toolTestCalculateExpression": True,
    "toolTestCreatePoem": True,
    # toolsPii
    "toolMyName": True,
    "toolMyPetsName": True,
    # toolsGeneral
    "toolShell": True,
    "toolSetCronRemainder": True,
    "toolWebSearch": True,
    # toolsDataAnalysis
    "execute_pyspark_code": True,
    "analyze_csv_data": True,
    # toolsFinanceAssist V01
    "ToolReadFinanceData": True,
    "ToolWriteFinanceData": True,
    # toolsFinanceAssist V02
    "sql_db_query": True,
    "sql_db_schema": True,
    "sql_db_list_tables": True,
    "sql_db_query_checker": True,
}


# --------------------------------------------------------------------------- #
# Global mutable state
# --------------------------------------------------------------------------- #
REQUESTED_TOOLS_NUMBER_PER_USER_INPUT = 0
REQUESTED_TOOLS_NUMBER_PER_AGENT_INTERRUPT = 0
MODE_CURRENT_LLM = "na"  # tracks the active LLM mode, to detect mode changes
TOOLS = []  # default: no tools

LLM = ChatOllama(
    model="qwen3.5:4b",
    streaming=True,
    max_tokens=DEFAULT_MAX_TOKENS,
    temperature=DEFAULT_TEMPERATURE,
    max_retries=DEFAULT_MAX_RETRIES,
    reasoning=False,
)

# --------------------------------------------------------------------------- #
# Functions
# --------------------------------------------------------------------------- #

@PrintFunctionName
def FormatMessageTypes(text: str) -> None:
    """Print a centered '=== text ===' banner used to separate message blocks."""
    padding = (BANNER_WIDTH - len(text) - 4) // 2
    print("=" * padding + " " + text + " " + "=" * padding)


@PrintFunctionName
def BuildAgent():
    """Create a new LangChain agent from the current global LLM/tools + HITL middleware."""
    # print("Agent BuildAgent new instance")
    # print(f"Agent BuildAgent llm: {LLM}")

    middleware = [
        HumanInTheLoopMiddleware(
            interrupt_on=TOOL_INTERRUPT_POLICY,
            description_prefix="Tool execution pending approval",
        )
    ]
    return create_agent(model=LLM, tools=TOOLS, middleware=middleware, checkpointer=InMemorySaver())


AGENT = BuildAgent()


@PrintFunctionName
def UpdateAgent(modeLLM: str) -> None:
    """Rebuild the global agent whenever the requested LLM mode changes."""
    global LLM, MODE_CURRENT_LLM, AGENT, TOOLS

    # print(f"Agent UpdateAgent: modeLLM: {modeLLM}, modeCurrentLLM: {MODE_CURRENT_LLM}")
    if modeLLM == MODE_CURRENT_LLM:
        return

    # logger.debug(f"Agent UpdateAgent Changing LLM: modeLLM: {modeLLM}, modeCurrentLLM: {MODE_CURRENT_LLM}")
    MODE_CURRENT_LLM = modeLLM

    if modeLLM == "local-1b":
        LLM = ChatOllama(
            model="llama3.2:1b", streaming=True, max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE, max_retries=DEFAULT_MAX_RETRIES,
        )
        TOOLS = []

    elif modeLLM == "local-3b":
        LLM = ChatOllama(
            model="llama3.2", streaming=True, max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE, max_retries=DEFAULT_MAX_RETRIES,
        )

    elif modeLLM == "local-4b-no-tools":
        LLM = ChatOllama(
            model="qwen3.5:4b", streaming=True, max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE, max_retries=DEFAULT_MAX_RETRIES, reasoning=False,
        )
        TOOLS = []

    elif modeLLM == "local-4b":
        LLM = ChatOllama(
            model="qwen3.5:4b", streaming=True, max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE, max_retries=DEFAULT_MAX_RETRIES, reasoning=False,
        )
        TOOLS = toolsManager.Main("get")  # "get": fetch tools list

    elif modeLLM == "local-7b-raw":
        LLM = ChatOllama(
            model="llama2-uncensored:7b", streaming=True, max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE, max_retries=DEFAULT_MAX_RETRIES,
        )

    elif modeLLM == "local-7b-vision":
        LLM = ChatOllama(
            model="llava:7b", streaming=True, max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE, max_retries=DEFAULT_MAX_RETRIES,
        )

    elif modeLLM == "global":
        LLM = ChatOpenAI(
            model="gpt-3.5-turbo", streaming=True, max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE, max_retries=DEFAULT_MAX_RETRIES,
        )
        TOOLS = toolsManager.Main("get")  # "get": fetch tools list

    elif modeLLM == "globalGemini":
        # NOTE: ChatGoogleGenerativeAI is not imported in this module; this
        # branch raises NameError if selected. Preserved as-is from the
        # original implementation (see "Issues Found" in the review).
        LLM = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key="AIzaSyBPH-0Dd5e2Heu8lFs1rCci8ZdGxnr_ZvE",
        )

    AGENT = BuildAgent()

@PrintFunctionName
def PrintPostProcessingLLMVariables(content) -> None:
    """
    Print final AIMessage metadata in a human-readable format.
    Intended for use with stream_mode='updates'.
    """

    try:
        if not isinstance(content, dict):
            return

        modelData = content.get("model")
        if not modelData:
            return

        messages = modelData.get("messages", [])
        if not messages:
            return

        message = messages[-1]

        responseMetadata = getattr(message, "response_metadata", {})
        usageMetadata = getattr(message, "usage_metadata", {})

        # print("\n" + "=" * 80)
        # print("FINAL LLM RESPONSE")
        # print("-" * BANNER_WIDTH)
        print("\nLLM Metrics Extraction:")
        # print("=" * 80)

        # print(f"Model              : {responseMetadata.get('model_name', 'Unknown')}")
        # print(f"Provider           : {responseMetadata.get('model_provider', 'Unknown')}")
        # print(f"Done               : {responseMetadata.get('done', 'Unknown')}")
        # print(f"Done Reason        : {responseMetadata.get('done_reason', 'Unknown')}")

        print()

        print(f"Input Tokens       : {usageMetadata.get('input_tokens', 0)}")
        print(f"Output Tokens      : {usageMetadata.get('output_tokens', 0)}")
        print(f"Total Tokens       : {usageMetadata.get('total_tokens', 0)}")

        print()

        print(f"Created At         : {responseMetadata.get('created_at', 'Unknown')}")

        print(
            f"Load Duration      : "
            f"{responseMetadata.get('load_duration', 0) / 1_000_000_000:.2f}s"
        )

        print(
            f"Prompt Eval Time   : "
            f"{responseMetadata.get('prompt_eval_duration', 0) / 1_000_000_000:.2f}s"
        )

        print(
            f"Generation Time    : "
            f"{responseMetadata.get('eval_duration', 0) / 1_000_000_000:.2f}s"
        )

        print(
            f"Total Duration     : "
            f"{responseMetadata.get('total_duration', 0) / 1_000_000_000:.2f}s"
        )

        if getattr(message, "tool_calls", None):
            print()
            print("Tool Calls:")
            for index, toolCall in enumerate(message.tool_calls, start=1):
                print(f"  {index}. {toolCall}")

        # print()
        # print("-" * 80)
        # print("FINAL RESPONSE")
        # print("-" * 80)
        # print(message.content)
        # print("=" * 80)

    except Exception as error:
        print(f"PrintPostProcessingLLMVariables Error: {error}")

# @PrintFunctionName
def ExtractStreamContent(streamMode: str, content) -> str:
    """Extract printable text from a streamed chunk and print it to the console.

    Handles two stream modes:
      - "messages": incremental LLM/tool message chunks, printed as they arrive.
      - "updates": state updates, used to detect and surface pending tool-call
        interrupts that require human approval.
    """
    global REQUESTED_TOOLS_NUMBER_PER_USER_INPUT, REQUESTED_TOOLS_NUMBER_PER_AGENT_INTERRUPT

    # print(f"ExtractStreamContent content: {content}")

    if streamMode == "messages":
        if not (isinstance(content, tuple) and len(content) >= 1):
            return ""

        messageChunk = content[0]
        if not hasattr(messageChunk, "content"):
            return ""

        messageType = getattr(messageChunk, "type", messageChunk.__class__.__name__)
        if messageType == "tool":
            FormatMessageTypes("ToolMessage")
            print(f"{messageChunk.content}", end="", flush=True)
            print()
            FormatMessageTypes("")
            print()
        else:
            print(f"{messageChunk.content}", end="", flush=True)

        return messageChunk.content or ""

    elif streamMode == "updates":

        PrintPostProcessingLLMVariables(content)

        interrupts = content.get("__interrupt__", [])
        if not interrupts:
            return ""

        firstInterrupt = interrupts[0]
        REQUESTED_TOOLS_NUMBER_PER_USER_INPUT += 1
        REQUESTED_TOOLS_NUMBER_PER_AGENT_INTERRUPT = len(firstInterrupt.value["action_requests"])

        for actionRequest in firstInterrupt.value["action_requests"]:
            toolName = actionRequest["name"]
            args = actionRequest.get("args", actionRequest.get("arguments", {}))
            print(f"\n{'-' * BANNER_WIDTH}")
            logger.info(
                f"tool_name: {toolName},\nargs: {args},\n"
                f"requestedToolsNumberPerUserInput: {REQUESTED_TOOLS_NUMBER_PER_USER_INPUT}\n"
                f"requestedToolsNumberPerAgentInterrupt: {REQUESTED_TOOLS_NUMBER_PER_AGENT_INTERRUPT}"
            )
            print(f"{'-' * BANNER_WIDTH}")
            input("Is this approved or rejected?(Default: approved): ")

        return ""

    else:
        print(f"else stream_mode: {streamMode}")
        return ""


@PrintFunctionName
def StreamAndAccumulate(messages: list, configMemory: dict) -> str:
    """Stream a fresh agent turn for the given messages, printing and
    accumulating the response text, wrapped in an AIMessage banner."""
    response = ""
    FormatMessageTypes("AIMessage")
    for streamMode, chunk in AGENT.stream(
        {"messages": messages}, stream_mode=["updates", "messages"], config=configMemory
    ):
        chunkText = ExtractStreamContent(streamMode, chunk)
        if chunkText:
            response += chunkText
    print()
    FormatMessageTypes("")
    print()
    return response

@PrintFunctionName
def StreamAndAccumulateResume(messages: list, configMemory: dict, decisions) -> str:
    """Resume a previously interrupted agent execution using the provided
    decisions, streaming and accumulating the response text while displaying
    it under an AIMessage banner."""
    response = ""
    FormatMessageTypes("AIMessageResume")
    # for streamMode, chunk in AGENT.invoke(
    for streamMode, chunk in AGENT.stream(
        Command(resume={"decisions": decisions}), stream_mode=["updates", "messages"], config=configMemory
        # Command(resume={"decisions": decisions}), config=configMemory
    ):
    # for streamMode, chunk in AGENT.stream(
    #     {"messages": messages}, stream_mode=["updates", "messages"], config=configMemory
    # ):
        chunkText = ExtractStreamContent(streamMode, chunk)
        if chunkText:
            response += chunkText
    print()
    FormatMessageTypes("")
    print()
    return response


@PrintFunctionName
def StreamResumeAndAccumulate(decisions: list, configMemory: dict) -> str:
    """Resume a previously-interrupted agent run with approval decisions,
    streaming and accumulating the response text."""
    response = ""
    FormatMessageTypes("AIMessage")
    for streamMode, chunk in AGENT.stream(
        Command(resume={"decisions": decisions}),
        stream_mode=["updates", "messages"],
        config=configMemory,
    ):
        chunkText = ExtractStreamContent(streamMode, chunk)
        if chunkText:
            response += chunkText
    print()
    FormatMessageTypes("")
    print()
    return response


@PrintFunctionName
def PrintLlmMetrics(lastMessage) -> None:
    """Print token usage and duration metrics for the most recent LLM response."""
    usage = lastMessage.usage_metadata
    responseMetadata = lastMessage.response_metadata

    print("-" * BANNER_WIDTH)
    print("\nLLM Metrics Extraction:")
    print(f"Input Tokens: {usage.get('input_tokens', 'N/A')}")
    print(f"Output Tokens: {usage.get('output_tokens', 'N/A')}")

    totalDurationMs = responseMetadata.get("total_duration", "N/A")
    if isinstance(totalDurationMs, (int, float)):
        print(f"Total Duration (ms): {totalDurationMs / 1000:.2f} seconds")
    else:
        print(f"Total Duration (ms): {totalDurationMs}")

    print(f"Prompt Eval Count (tokens): {usage.get('prompt_eval_count', 'N/A')}")
    print(f"Evaluation Count: {usage.get('eval_count', 'N/A')}")


@PrintFunctionName
def Main(userInput: str, threadId, modeLLM: str, modeStream: str) -> str:
    """Route a user input to the appropriate LLM/agent execution strategy.

    `modeLLM` selects the backend/personality (e.g. "local", "local-buddy",
    "local-4b", "global"...). `modeStream` ("true"/"false") only affects the
    "local-4b" mode, choosing between an auto-approving streaming loop and an
    interactive invoke-based approval loop.
    """
    global REQUESTED_TOOLS_NUMBER_PER_USER_INPUT, REQUESTED_TOOLS_NUMBER_PER_AGENT_INTERRUPT

    UpdateAgent(modeLLM)

    # print(f"agent.py Main : userInput {userInput}, threadId: {threadId}, "
    #       f"modeLLM: {modeLLM}, modeStream: {modeStream}")
    print(f"[Info] agent.py Main : userInput, threadId: {threadId}, "
          f"modeLLM: {modeLLM}, modeStream: {modeStream}")

    threadIdStr = "thread-" + str(threadId)
    configMemory = {"configurable": {"thread_id": threadIdStr}}
    # print(f"thread_id: {threadIdStr}")

    if modeLLM == "local":
        return StreamAndAccumulate(
            [
                {"role": "system", "content": JARVIS_SYSTEM_PROMPT},
                {"role": "user", "content": userInput},
            ],
            configMemory,
        )

    elif modeLLM == "local-buddy":
        return StreamAndAccumulate(
            [
                {"role": "system", "content": BUDDY_SYSTEM_PROMPT},
                {"role": "user", "content": userInput},
            ],
            configMemory,
        )

    elif modeLLM == "local-4b" and modeStream == "false":
        # NOTE: leftover debug pause from the original implementation; blocks
        # execution waiting for Enter. Preserved to keep behavior identical.
        # input("HumanInterrupt02")

        result = AGENT.invoke({"messages": [{"role": "user", "content": userInput}]}, config=configMemory)
        print(f"01 result:{result}")

        lastMessage = result["messages"][-1]
        PrintLlmMetrics(lastMessage)

        while True:
            print("agiain in started the while loop")
            state = AGENT.get_state(configMemory)
            print(f"02 state:{state}")

            if not state.interrupts:
                return result["messages"][-1].content

            interrupt = state.interrupts[0]
            actions = interrupt.value["action_requests"]
            decisions = []
            for action in actions:
                print("-" * BANNER_WIDTH)
                print("Tool :", action["name"])
                print("Args :", action["args"])
                choice = input("Approve? [Y/n] : ")
                decisions.append({"type": "reject"} if choice.lower() == "n" else {"type": "approve"})

            result = AGENT.invoke(Command(resume={"decisions": decisions}), config=configMemory)
            print(f"03 result:{result}")


    elif modeLLM == "local-4b" and modeStream == "true":
        # NOTE: leftover debug pause from the original implementation; blocks
        # execution waiting for Enter. Preserved to keep behavior identical.
        # input("HumanInterrupt01")

        agentCallingCount = 0
        agentResponse = ""

        while True:
            agentCallingCount += 1

            if agentCallingCount == 1 and REQUESTED_TOOLS_NUMBER_PER_USER_INPUT < 1:
                # print(f"agent.py main agent: {AGENT}")
                agentResponse = StreamAndAccumulate([{"role": "user", "content": userInput}], configMemory)

            elif REQUESTED_TOOLS_NUMBER_PER_USER_INPUT >= 1:
                REQUESTED_TOOLS_NUMBER_PER_USER_INPUT -= 1
                FormatMessageTypes("AIMessage")

                decisions = [{"type": "approve"} for _ in range(REQUESTED_TOOLS_NUMBER_PER_AGENT_INTERRUPT)]
                REQUESTED_TOOLS_NUMBER_PER_AGENT_INTERRUPT = 0

                # NOTE: original resumes via invoke() here (not stream()), so
                # any tool response text is not appended to agentResponse.
                # Preserved as-is to keep behavior identical (see review).
                # AGENT.invoke(Command(resume={"decisions": decisions}), config=configMemory)
                agentResponse = StreamAndAccumulateResume([{"role": "user", "content": userInput}], configMemory, decisions)

                print()
                FormatMessageTypes("")
                print()

            else:
                return agentResponse

            logger.debug(f"[Info] agentCallingCountPerUserInput: {agentCallingCount}")
            agentResponse = ""

    elif modeLLM == "local-4b-no-tools" and modeStream == "true":
        # NOTE: leftover debug pause from the original implementation; blocks
        # execution waiting for Enter. Preserved to keep behavior identical.
        # input("HumanInterrupt01")

        agentCallingCount = 0
        agentResponse = ""

        while True:
            agentCallingCount += 1

            if agentCallingCount == 1:
                # print(f"agent.py main agent: {AGENT}")
                agentResponse = StreamAndAccumulate([{"role": "user", "content": userInput}], configMemory)

                print()
                FormatMessageTypes("")
                print()

            else:
                return agentResponse

            logger.debug(f"agentCallingCountPerUserInput: {agentCallingCount}")
            agentResponse = ""
    elif "global" in modeLLM:
        agentCallingCount = 0
        agentResponse = ""

        while True:
            agentCallingCount += 1

            if agentCallingCount == 1 and REQUESTED_TOOLS_NUMBER_PER_USER_INPUT < 1:
                agentResponse = StreamAndAccumulate([{"role": "user", "content": userInput}], configMemory)

            elif REQUESTED_TOOLS_NUMBER_PER_USER_INPUT >= 1:
                REQUESTED_TOOLS_NUMBER_PER_USER_INPUT -= 1
                decisions = [{"type": "approve"} for _ in range(REQUESTED_TOOLS_NUMBER_PER_AGENT_INTERRUPT)]
                REQUESTED_TOOLS_NUMBER_PER_AGENT_INTERRUPT = 0
                agentResponse = StreamResumeAndAccumulate(decisions, configMemory)

            else:
                return agentResponse

            logger.debug(f"agentCallingCountPerUserInput: {agentCallingCount}")
            agentResponse = ""