"""
Personal Assistant CLI entry point.

Handles mode configuration, user input/output, and dispatches
processed input to the configured LLM framework (LangChain or Fabric).
"""

# ---- Standard library imports ----
import json
import os
import sys
from typing import Any, Iterable, Optional

# ---- Local imports ----
import Fabric.manager as Fabric
import Langchain.agent as Agent
import Langchain.Tools.toolsManager as toolsManager
import UI.modesManager as modesManager
import UserContext.userContext as UserContext
from Log.custom_logger import logger
from Log.log_utils import PrintFunctionName

# Optional / alternate I/O backends (kept for reference, not currently wired in):
# import readline
# import TextToSpeech.textToSpeechOnline02 as TTS
# import SpeechToText.speechToTextOnline as STT
# import LLM.llm as LLM
# import userInputToScriptInvocation as UITSI

# logger.debug("Initialized assistant.py")

# ---- Constants / Global State ----
LIST_WAKE_UP_CALLS = ["hey there", "hi there", "hey rpi"]
LIST_SLEEP_CALLS = ["sleep now", "go to sleep", "we are done", "got it"]

THREAD_ID = 0          # Memory Id for the agent graph
USER_INPUT_COUNT = 0   # Tracks number of loops through Main()

MODE_CONFIG_FILE_PATH = "./UI/modesConfig.json"
MODE_CONFIG_SANDBOX_FILE_PATH = "./UI/modesConfigSandbox.json"
USER_INPUT_FILE = "./Log/userInput.txt"
MODE_SANDBOX = "false"

COMMANDS = [
    "mode", "input", "text", "speech", "output", "context", "yes", "no",
    "llm", "local", "global", "globalgemini", "framework", "langchain",
    "fabric", "True", "False", "multiline",
]

FORMAT_MESSAGE_WIDTH = 60  # Total width used when printing section separators

# ---- Mode Configuration Helpers ----
@PrintFunctionName
def _ResolveModeConfigPath() -> str:
    """Return the active mode-config file path, honoring sandbox mode."""
    if MODE_SANDBOX == "true":
        return MODE_CONFIG_SANDBOX_FILE_PATH
    return MODE_CONFIG_FILE_PATH


@PrintFunctionName
def LoadModes() -> Optional[dict]:
    """
    Load the mode configuration from disk.

    If the config file does not exist yet, trigger initialization via
    modesTUI and return None (caller should reload afterward if needed).
    """
    # PrintFunctionNames("cli LoadModes...")
    configPath = _ResolveModeConfigPath()

    if os.path.exists(configPath):
        logger.debug("[Debug] LoadModes: getting current mode config file")
        with open(configPath, "r") as configFile:
            return json.load(configFile)

    logger.debug("[Debug] LoadModes: initializing the mode config file")
    modesManager.LoadConfigurationFromFile(modeSandbox=MODE_SANDBOX)
    return None


@PrintFunctionName
def UpdateModeValue(modeName: str, modeValue: str) -> None:
    """Update a single mode's value in the config file and persist it."""
    # PrintFunctionNames("cli UpdateModeValue...")
    modeConfig = LoadModes()
    modeConfig[modeName] = modeValue

    configPath = _ResolveModeConfigPath()
    with open(configPath, "w") as configFile:
        json.dump(modeConfig, configFile, indent=2)

    print()


@PrintFunctionName
def GetAllModeValues() -> None:
    """Print every mode name and its current value."""
    # PrintFunctionNames("cli GetAllModeValues...")
    modeConfig = LoadModes()
    counter = 1
    for key, value in modeConfig.items():
        key = key.replace('-', ' ')
        # print(f"  {key:<27} → {value}")
        print(f"{counter}.  {key:<20} [{value}]")
        counter += 1


@PrintFunctionName
def GetModeValue(modeName: str) -> Any:
    """Return the current value for the given mode name."""
    # PrintFunctionNames("cli GetModeValue...")
    modeConfig = LoadModes()
    return modeConfig[modeName]


@PrintFunctionName
def DropModeConfigFile() -> None:
    # PrintFunctionNames("cli DropModeConfigFile...")
    """Delete the current mode config file, if it exists."""
    configPath = _ResolveModeConfigPath()
    if os.path.exists(configPath):
        os.remove(configPath)
        print(f"File '{configPath}' has been deleted successfully.")
    else:
        print(f"File '{configPath}' does not exist.")


# ---- Tool / Command Helpers ----

@PrintFunctionName
def FormatToolsPrinting(tools: Iterable[Any]) -> None:
    """
    Print tools in the format: <toolName>: <toolDescription>

    Supports LangChain StructuredTool/BaseTool instances, dicts, and
    callables with name/description attributes.
    """
    # PrintFunctionNames("cli FormatToolsPrinting...")
    for index, tool in enumerate(tools, start=1):
        name = None
        description = None

        if hasattr(tool, "name") and hasattr(tool, "description"):
            name = getattr(tool, "name", None)
            description = getattr(tool, "description", None)
        elif isinstance(tool, dict):
            name = tool.get("name")
            description = tool.get("description")
        elif callable(tool) and hasattr(tool, "__name__"):
            name = getattr(tool, "__name__", None)
            description = getattr(tool, "description", None) or getattr(tool, "__doc__", None)

        name = name or f"tool_{index}"
        description = description or "(no description available)"
        description = description.split("\n")[0].rstrip()  # first line only, no trailing whitespace

        print(f"{name}: {description:20}")


@PrintFunctionName
def BasicCmds(userInput: str) -> bool:
    """
    Handle basic CLI commands (help, mode changes).

    Returns True if the input was recognized and handled as a basic
    command, False if it should be passed on for further processing.
    """
    # PrintFunctionNames("cli BasicCmds...")
    global MODE_SANDBOX

    parts = userInput.lower().split()

    if parts[0] == "help":
        FormatMessageTypes("SystemMessage")
        logger.info("Help:")
        logger.info("Type 'help' for list of commands")
        logger.info("Type 'mode update' for update the modes")
        GetAllModeValues()

    elif len(parts) <= 3 and parts[0] == "mode":
        modeName = "mode-" + parts[1]
        modeValue = parts[2] if len(parts) > 2 and parts[2] else None

        print(f"BasicCmds {modeName} ==> {modeValue}")

        if modeName in ("mode-input", "mode-llm", "mode-stream"):
            UpdateModeValue(modeName, modeValue)
            return True

        elif modeName == "mode-get":
            GetAllModeValues()
            return True

        elif modeName == "mode-update":
            if MODE_SANDBOX == "true":
                modesManager.Main(MODE_SANDBOX)
            else:
                modesManager.Main()
            return True

        elif modeName == "mode-sandbox":
            MODE_SANDBOX = modeValue
            modesManager.LoadConfigurationFromFile(modeSandbox=MODE_SANDBOX)
            GetAllModeValues()
            return True

        elif modeName == "mode-tools":
            # modeValue is either "update" or "get"
            tools = toolsManager.Main(modeValue)
            print("toolsManager: Goodbye!")
            # FormatToolsPrinting(tools)
            return True

        elif modeName == "mode-reset":
            DropModeConfigFile()
            return True
    else:
        return False

    FormatMessageTypes("")
    print()
    return True


@PrintFunctionName
def Completer(text: str, state: int) -> Optional[str]:
    """Auto-completion callback for readline-style tab completion."""
    # PrintFunctionNames("cli Completer...")
    options = [command for command in COMMANDS if command.startswith(text)]
    if state < len(options):
        return options[state]
    return None


# readline.set_completer(Completer)
# readline.parse_and_bind("tab: complete")


@PrintFunctionName
def FormatMessageTypes(text: str) -> None:
    """Print a section separator line with the given label centered in it."""
    # PrintFunctionNames("cli FormatMessageTypes...")
    padding = (FORMAT_MESSAGE_WIDTH - len(text) - 4) // 2
    print("=" * padding + " " + text + " " + "=" * padding)


@PrintFunctionName
def ReadUserInputFile() -> Optional[str]:
    """Read and return the contents of the userInput.txt file, if present."""
    # PrintFunctionNames("cli ReadUserInputFile...")
    if os.path.exists(USER_INPUT_FILE):
        with open(USER_INPUT_FILE, "r") as inputFile:
            return inputFile.read()
    print("The userInput File do not exist")
    return None


# ---- Input / Output ----

# @log_call
@PrintFunctionName
def Input() -> str:
    """Read user input according to the current mode-input setting."""
    # PrintFunctionNames("cli Input...")
    if MODE_SANDBOX == "true":
        FormatMessageTypes("HumanMessage:Sandbox")
    else:
        FormatMessageTypes("HumanMessage")

    modeInput = GetModeValue("mode-input")

    if modeInput == "text":
        userInput = input("")
    elif modeInput == "multiline":
        logger.info(
            "Paste your multiline input followed by Ctrl-D (Linux/macOS) "
            "or Ctrl-Z (Windows) then Enter:"
        )
        userInput = sys.stdin.read()
    elif modeInput == "file":
        userInput = ReadUserInputFile()
        print(userInput)
        userChoice = input("Change to mode input text (N/y): ")
        if userChoice == "y":
            userInput = "mode input text"
    elif modeInput == "speech":
        userInput = STT.Main()  # Speech To Text
    else:
        logger.info(f"Error: Invalid modeInput: {modeInput}")
        userInput = None

    # logger.debug(f"userInput: {userInput}")
    FormatMessageTypes("")
    return userInput


@PrintFunctionName
def Processing(userInput: str) -> Any:
    """Route user input through basic commands or the LLM framework."""
    # PrintFunctionNames("cli Processing...")
    global THREAD_ID

    if BasicCmds(userInput):
        return None

    if GetModeValue("mode-conversation") == "wakeUp":
        modeFramework = GetModeValue("mode-framework")

        if modeFramework == "langchain":
            if GetModeValue("mode-context") == "no":
                THREAD_ID += 1  # Always changing memory variable

            # UserContext.Main(userInput)
            # return Agent.Main(userInput, THREAD_ID, GetModeValue("mode-llm"))
            return Agent.Main(userInput, THREAD_ID, GetModeValue("mode-llm"), GetModeValue("mode-stream"))

        elif modeFramework == "fabric":
            logger.info("modeFramework: fabric")
            return Fabric.Main(userInput, GetModeValue("mode-llm"))

    return None


@PrintFunctionName
def Output(assistantOutput: Any) -> None:
    """Emit the assistant's output according to the current mode-output setting."""
    # PrintFunctionNames("cli Output...")
    logger.debug(f"assistantOutput: {assistantOutput}")

    modeOutput = GetModeValue("mode-output")
    if modeOutput == "text":
        return
    elif modeOutput == "speech":
        TTS.Main(assistantOutput)  # Text to speech
    else:
        logger.info(f"Error: Invalid modeOutput: {modeOutput}")


# ---- Main Loop ----

@PrintFunctionName
def WelcomeUser() -> None:
    """Print a welcome banner and show the help command output."""
    # PrintFunctionNames("cli WelcomeUser...")
    # logger.debug("WelcomeUser()")
    logger.info("Welcome to Personal Assistant CLI")

    assistantOutput = Processing("help")
    if assistantOutput is not None:
        Output(assistantOutput)


@PrintFunctionName
def Main() -> None:
    """Run a single input -> processing -> output cycle."""
    # PrintFunctionNames("cli Main...")
    global USER_INPUT_COUNT

    USER_INPUT_COUNT += 1
    logger.debug(f"UserInputCount: {USER_INPUT_COUNT}")

    userInput = Input()
    # print(f"userInput after input: {userInput}")
    # if userInput is not None or userInput != "":
    if userInput and len(userInput.strip()) > 0: 
        # print(f"userInput before procesing: {userInput}")
        assistantOutput = Processing(userInput)
        if assistantOutput is not None:
            Output(assistantOutput)


WelcomeUser()

while True:
    Main()