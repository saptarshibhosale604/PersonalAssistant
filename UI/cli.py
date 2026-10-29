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

# ---- Environment Configuration ----
from dotenv import load_dotenv
load_dotenv()

# ---- Local imports ----
# import Fabric.manager as Fabric
import Langchain.agent as Agent
import Langchain.sessionResume as sessionResume
import Langchain.Tools.toolsManager as toolsManager
import UI.modesManager as modesManager
import UserContext.userContext as UserContext
from Log.custom_logger import logger, log_path
from Log.log_utils import PrintFunctionName
from Log.turn_logger import begin_turn, end_turn, set_agent_output, add_usage

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
is_terminal_active = False # Tracks whether interactive terminal command mode is active

MODE_CONFIG_FILE_PATH = "./UI/modesConfig.json"
MODE_CONFIG_SANDBOX_FILE_PATH = "./UI/modesConfigSandbox.json"
USER_INPUT_FILE = "./Log/userInput.txt"
MODE_SANDBOX = "false"

COMMANDS = [
    "mode", "input", "text", "speech", "output", "context", "yes", "no",
    "llm", "local", "globalChatgpt01", "globalChatgpt02", "globalGemini01", "globalGemini02", "globalMistral01", "globalMistral02", "globalGroq01", "globalGroq02", "globalOpenRouter01", "globalOpenRouter02", "globalNvidia01", "globalNvidia02", "globalHuggingFace01", "globalHuggingFace02", "framework", "langchain",
    "fabric", "True", "False", "multi", "os", "windows", "linux",
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
        # logger.debug("[Debug] LoadModes: getting current mode config file")
        with open(configPath, "r") as configFile:
            return json.load(configFile)

    # logger.debug("[Debug] LoadModes: initializing the mode config file")
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
def BasicCmdsSkill(userInput: str) -> bool:
    """
    Handle skill execution via slash commands:
        /<skillName> <userInput (Optional)>

    <skillName> is the file name in the './Skill' directory.
    Combines: <content in the skillName file> \n <userInput if provided>
    and passes the combined text to Agent (via Processing).

    Returns True if a matching skill file was found and processed, otherwise False.
    """
    userInput = userInput.strip()

    if not userInput.startswith("/"):
        return False

    # Remove leading slash and split into parts
    cmd_body = userInput[1:].strip()
    if not cmd_body:
        return False

    parts = cmd_body.split(maxsplit=1)
    skill_name = parts[0].lower()
    optional_user_input = parts[1] if len(parts) > 1 else ""

    skill_dir = "./Skill"
    if not os.path.exists(skill_dir):
        return False

    # Scan files in Skill/ directory case-insensitively or exact match
    skill_files = [f for f in os.listdir(skill_dir) if os.path.isfile(os.path.join(skill_dir, f))]
    
    # Find matching skill file (case-insensitive check for skill_name)
    matched_file = next((f for f in skill_files if f.lower() == skill_name), None)
    if not matched_file:
        return False

    skill_path = os.path.join(skill_dir, matched_file)
    try:
        with open(skill_path, "r", encoding="utf-8", errors="ignore") as sf:
            skill_content = sf.read().strip()

        # Combine skill content and optional user input
        if optional_user_input:
            combined_input = f"{skill_content}\n{optional_user_input}"
        else:
            combined_input = skill_content

        print(f"\n[Executing Skill: {matched_file}]")
        if optional_user_input:
            print(f"[User Input Provided]: {optional_user_input}")
        print("-" * 40)
        print(combined_input)
        print("-" * 40)

        # Pass combined input to Processing (which invokes Agent)
        # Processing(combined_input)
        # return True
        return combined_input
    except Exception as e:
        print(f"Error reading skill file '{matched_file}': {e}")
        return False


@PrintFunctionName
def BasicCmdsSlash(userInput: str) -> bool:
    """
    Handle basic CLI commands.

    Supported commands:

        /
        /help

        /input <value>
        /llm <value>
        /stream <value>

        /get
        /update
        /sandbox <true|false>
        /tools <update|get>
        /reset
        /exit

    Returns True if handled, otherwise False.
    """
    global MODE_SANDBOX
    global THREAD_ID
    global _os_prefix_added

    userInput = userInput.strip()

    if not userInput.startswith("/"):
        return False

    parts = userInput.split()

    command = parts[0].lower()
    value = parts[1].lower() if len(parts) > 1 else None

    print(f"BasicCmdsSlash {command} ==> {value}")

    # --------------------------------------------------
    # Help
    # --------------------------------------------------

    if command in ("/", "/help"):
        FormatMessageTypes("SystemMessage")
        print("Help:")
        print("Available commands:")
        print("  /help or /               : Displays the complete list of available project CLI control commands and current logs.")
        print("  /input <value>           : Sets the primary user input mechanism (e.g., text, speech) in the configuration.")
        print("  /llm <value>             : Switches the active Large Language Model provider or model in real-time.")
        print("  /stream <value>          : Enables or disables streaming token output directly in the console.")
        print("  /os <value>              : Specifies target operating system behavior (Windows/Linux) for system execution tools.")
        print("  /get                     : Prints all active assistant modes and configuration values.")
        print("  /update                  : Launches the interactive TUI configuration manager to edit system modes.")
        print("  /sandbox <true|false>    : Switches between production and sandbox mode configuration files.")
        print("  /tools <update|get>      : Inspects or updates registered agent tools via the tools manager.")
        print("  /new                     : Clears conversation memory thread IDs and resets session state for a fresh start.")
        print("  /resume <log file name>  : Rehydrates conversation history and context memory from a previous session log.")
        print("  /skill                   : Scans and displays available procedural skill routines stored in the './Skill' directory.")
        print("  /<skillName> <userInput> : Executes a specific pre-defined skill prompt combined with your optional input.")
        print("  /terminal start          : Enters interactive terminal command mode.")
        print("  /terminal stop           : Exits interactive terminal command mode.")
        print("  /reset                   : Deletes and re-initializes the active mode configuration file.")
        print("  /exit                    : Safely shuts down the Personal Assistant CLI application and flushes logs.")
        print()
        print(f"Log file: {os.path.abspath(log_path)}")
        print()
        GetAllModeValues()
        return True

    # --------------------------------------------------
    # Update mode values
    # --------------------------------------------------

    if command in ("/input", "/llm", "/stream", "/os"):
        UpdateModeValue(f"mode-{command[1:]}", value)
        return True

    # --------------------------------------------------
    # Terminal Mode Command
    # --------------------------------------------------

    elif command == "/terminal":
        global is_terminal_active
        if value == "start":
            is_terminal_active = True
            FormatMessageTypes("SystemMessage")
            print("Terminal mode started.")
            print("All subsequent inputs will be executed directly as system shell commands.")
            print("Type '/terminal stop' to exit terminal mode.")
            print()
            return True
        elif value == "stop":
            is_terminal_active = False
            FormatMessageTypes("SystemMessage")
            print("Terminal mode stopped. Returning to standard assistant mode.")
            print()
            return True
        else:
            print("Usage: /terminal start  OR  /terminal stop")
            return True

    # --------------------------------------------------
    # Show current modes
    # --------------------------------------------------

    elif command == "/get":
        GetAllModeValues()
        return True

    # --------------------------------------------------
    # Interactive mode update
    # --------------------------------------------------

    elif command == "/update":
        if MODE_SANDBOX == "true":
            modesManager.Main(MODE_SANDBOX)
        else:
            modesManager.Main()
        return True

    # --------------------------------------------------
    # Sandbox
    # --------------------------------------------------

    elif command == "/sandbox":
        MODE_SANDBOX = value
        modesManager.LoadConfigurationFromFile(modeSandbox=MODE_SANDBOX)
        GetAllModeValues()
        return True

    # --------------------------------------------------
    # Tools
    # --------------------------------------------------

    elif command == "/tools":
        tools = toolsManager.Main(value)
        print("toolsManager: Goodbye!")
        # FormatToolsPrinting(tools)
        return True

    # --------------------------------------------------
    # New Session - Reset OS prefix flag
    # --------------------------------------------------

    elif command == "/new":
        # tools = toolsManager.Main(value)
        print("toolsManager: New session")
        global THREAD_ID, _os_prefix_added
        THREAD_ID += 1
        _os_prefix_added = False  # Reset OS prefix flag for new session
        # FormatToolsPrinting(tools)
        return True

    # --------------------------------------------------
    # Resume Session
    # --------------------------------------------------

    elif command == "/resume":
        session_log_dir = "./Log/SessionLog"
        if not os.path.exists(session_log_dir):
            print(f"SessionLog directory not found: {session_log_dir}")
            return True

        # Get all log files sorted by modification time (newest first)
        log_files = sorted(
            [f for f in os.listdir(session_log_dir) if f.endswith((".log", ".json"))],
            key=lambda x: os.path.getmtime(os.path.join(session_log_dir, x)),
            reverse=True
        )

        if not value:
            print("Usage: /resume <log file name>")
            print("\nAvailable recent session logs:")
            for idx, log_file in enumerate(log_files[:10], start=1):
                print(f"  {idx}. {log_file}")
            print("\nTip: You can pass part of the filename or exact name.")
            return True

        # Search for matching log file: prefer the session id prefix, then any substring
        matched_log = next((f for f in log_files if f.lower().startswith(f"session_{value}_")), None)
        if not matched_log:
            matched_log = next((f for f in log_files if value in f.lower()), None)

        if not matched_log:
            print(f"Error: No session log found matching '{value}'.")
            print("Available recent session logs:")
            for idx, log_file in enumerate(log_files[:5], start=1):
                print(f"  {idx}. {log_file}")
            return True

        log_file_path = os.path.join(session_log_dir, matched_log)
        print(f"Loading session from log: {matched_log}...")
        
        try:
            with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
                log_content = f.read()
            
            # Increment THREAD_ID to start a fresh thread context referencing this session
            THREAD_ID += 1
            _os_prefix_added = False
            
            # Seed the past turns into agent memory for the new thread ID
            new_thread_id_str = "thread-" + str(THREAD_ID)
            turns = sessionResume.ParseSessionLog(log_file_path)
            turns_loaded = Agent.SeedThreadHistory(THREAD_ID, GetModeValue("mode-llm"), turns)
            print(f"[Resume] Loaded {turns_loaded} turns into {new_thread_id_str}")
            if GetModeValue("mode-context") == "no":
                print("[Resume] Warning: mode-context is 'no', so the next input starts a new thread "
                      "and will not see the resumed history. Set mode-context to 'yes'.")

            FormatMessageTypes("SystemMessage")
            print(f"Successfully resumed session from: {matched_log}")
            print(f"New Thread ID: {THREAD_ID} ({new_thread_id_str})")
            print(f"Log path: {os.path.abspath(log_file_path)}")
            
            # Display last 1000 characters or preview of log content
            preview = log_content[-1000:] if len(log_content) > 1000 else log_content
            print("\n--- Session Preview / Tail ---")
            print(preview)
            print("------------------------------\n")
            
        except Exception as e:
            print(f"Error reading log file {matched_log}: {e}")

        return True

    # --------------------------------------------------
    # Skill Manager
    # --------------------------------------------------

    elif command == "/skill":
        skill_dir = "./Skill"
        if not os.path.exists(skill_dir):
            os.makedirs(skill_dir, exist_ok=True)
            print(f"Created missing skill directory: {skill_dir}")

        while True:
            # Scan skills in Skill/ directory
            skill_files = sorted([f for f in os.listdir(skill_dir) if os.path.isfile(os.path.join(skill_dir, f))])
            
            print("\nskillManager: select the mode:")
            print("'q' to quit from the skillManager\n")
            
            if not skill_files:
                print("  (No skill files found in Skill/ directory)")
            else:
                for idx, skill_file in enumerate(skill_files, start=1):
                    print(f"{idx}. skill {skill_file}")
            
            print()
            choice = input("Enter skill number or 'q': ").strip()
            
            if choice.lower() == 'q':
                print("skillManager: Goodbye!")
                return True
            
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(skill_files):
                    selected_skill_name = skill_files[choice_idx]
                    skill_path = os.path.join(skill_dir, selected_skill_name)
                    try:
                        with open(skill_path, "r", encoding="utf-8", errors="ignore") as sf:
                            skill_content = sf.read()
                        
                        print(f"\n[Skill Selected: {selected_skill_name}]")
                        print("-" * 40)
                        print(skill_content)
                        print("-" * 40)
                        
                        # Pass skill content directly into Processing
                        Processing(skill_content)
                        return True
                    except Exception as e:
                        print(f"Error reading skill file '{selected_skill_name}': {e}")
                else:
                    print(f"Invalid selection: {choice}. Please enter a number between 1 and {len(skill_files)}.")
            else:
                print("Invalid input. Please enter a valid number or 'q'.")

        return True

    # --------------------------------------------------
    # Reset
    # --------------------------------------------------

    elif command == "/reset":
        DropModeConfigFile()
        return True

    # --------------------------------------------------
    # Exit
    # --------------------------------------------------

    elif command == "/exit":
        print("Exiting Personal Assistant CLI...")
        print(f"Log file: {os.path.abspath(log_path)}")
        sys.exit(0)

    return False

@PrintFunctionName
def BasicCmdsMode(userInput: str) -> bool:
    """
    Handle basic CLI commands (mode changes).

    Returns True if the input was recognized and handled as a basic
    command, False if it should be passed on for further processing.
    """
    # PrintFunctionNames("cli BasicCmdsMode...")
    global MODE_SANDBOX

    parts = userInput.lower().split()

    if False:
        pass

    elif len(parts) <= 3 and parts[0] == "mode":
        modeName = "mode-" + parts[1]
        modeValue = parts[2] if len(parts) > 2 and parts[2] else None

        print(f"BasicCmdsMode {modeName} ==> {modeValue}")

        if modeName in ("mode-input", "mode-llm", "mode-stream", "mode-os"):
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
    if(text == "HumanMessage"):
        padding = (FORMAT_MESSAGE_WIDTH - len(text) - 4) // 2
        print("=" * padding + " " + "----------" + " " + "=" * padding + " " + "=" * padding + " " + "=" * padding)
        print("=" * padding + " " + "----------" + " " + "=" * padding)
        print("=" * padding + " " + text + " " + "=" * padding)
        print("=" * padding + " " + "----------" + " " + "=" * padding)
        print("=" * padding + " " + "----------" + " " + "=" * padding + " " + "=" * padding + " " + "=" * padding)
    else:
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


@PrintFunctionName
def PromptInjection(userInput: str) -> bool:
    """
    Handle prompt injection attempts by appending a safety note.
    
    Returns True if an attempt was detected and handled, False otherwise.
    """
    parts = userInput.lower().split()
    
    # Check if the first word is "cmd" (case-insensitive check on original input logic usually applies here)
    # "if the first word is CMD"sed on user request:
    # We will perform a case-insensitive split to be robust, but strictly check for 'cmd' as per instruction.
    
    if parts and parts[0].lower() == "cmd":
        original_input = userInput
        
        # Append the required note at the end of the input string
        # addNote = "\nNote: use one command at a time."
        # addNote = "\nNote: use one command at a time."
        addNote = (
            "\n\nImportant:\n"
            "- Execute exactly ONE PowerShell command per tool call.\n"
            "- Do not combine commands using ';', '&', '&&', or newlines.\n"
            "- If multiple commands are needed, invoke the tool multiple times."
        )
        
        # Construct the new full input to be processed (or logged)
        final_processed_input = f"{original_input}\n{addNote}"
        
        # print(f"PromptInjection detected. Processing with note appended:")
        logger.info(f"[INJECTED] note for CMD")
        
        # return True
    
    # else:
    #     # If not a CMD injection attempt, pass through or handle as normal (return False to indicate handled by this specific handler)
    #     FormatMessageTypes("")
    #     print()
    #     return False
        
# ---- Input / Output ----

# Global flag to track if OS prefix has been added in current session
_os_prefix_added = False

# @log_call
@PrintFunctionName
def Input() -> str:
    """Read user input according to the current mode-input setting."""
    # PrintFunctionNames("cli Input...")
    global _os_prefix_added
    
    if MODE_SANDBOX == "true":
        FormatMessageTypes("HumanMessage:Sandbox")
    else:
        FormatMessageTypes("HumanMessage")

    modeInput = GetModeValue("mode-input")

    try:
        if modeInput == "text":
            userInput = input("")
        elif modeInput == "multi":
            print(
                "Paste your multiline input\n"
                "To exit the mode multi type 'text'\n"
                "To submit input Ctrl-Z (Windows) or Ctrl-D (Linux/macOS) then Enter:"
            )
            # userInput = sys.stdin.read()
            userInput = sys.stdin.read().strip()
            if userInput == "text":
                userInput = "/input text"
        elif modeInput == "file":
            userInput = ReadUserInputFile()
            print(userInput)
            userChoice = input("Change to mode input text (y/N): ")
            if userChoice == "y":
                userInput = "/input text"
        elif modeInput == "speech":
            userInput = STT.Main()  # Speech To Text
        else:
            logger.info(f"Error: Invalid modeInput: {modeInput}")
            userInput = None
    except KeyboardInterrupt:
        print("\nExiting Personal Assistant CLI...")
        print(f"Log file: {os.path.abspath(log_path)}")
        sys.exit(0)

    # Apply OS mode prefix for Windows on first input (only if it's not a slash command)
    if userInput and len(userInput.strip()) > 0:
        modeOS = GetModeValue("mode-os")
        if modeOS == "windows" and not _os_prefix_added and not userInput.strip().startswith("/"):
            userInput = "You are using POWERSHELL CMD. \n" + userInput
            _os_prefix_added = True
            # logger.info(f"[OS Mode] Applied Windows prefix to first input")
        elif modeOS == "linux":
            # Linux mode - no prefix added
            pass

    # logger.debug(f"userInput: {userInput}")
    FormatMessageTypes("")
    return userInput


@PrintFunctionName
def Processing(userInput: str) -> Any:
    """Route user input through basic commands or the LLM framework."""
    # PrintFunctionNames("cli Processing...")
    global THREAD_ID, is_terminal_active

    userInput_str = userInput.strip() if userInput else ""

    # If terminal mode is active, handle stop command or execute shell commands directly
    if is_terminal_active:
        parts = userInput_str.split()
        if parts and parts[0].lower() == "/terminal" and len(parts) > 1 and parts[1].lower() == "stop":
            is_terminal_active = False
            FormatMessageTypes("SystemMessage")
            print("Terminal mode stopped. Returning to standard assistant mode.")
            print()
            return "Terminal mode stopped."

        import subprocess
        try:
            print(f"[Terminal Executing] {userInput_str}")
            result = subprocess.run(
                userInput_str,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout
            if result.stderr:
                output += "\n[stderr]:\n" + result.stderr
            
            print(output)
            return output
        except Exception as e:
            err_msg = f"Terminal execution error: {e}"
            print(err_msg)
            return err_msg

    if BasicCmdsMode(userInput):
        return None
    if BasicCmdsSlash(userInput):
        return None
    combined_input = BasicCmdsSkill(userInput)
    if combined_input:
        userInput = combined_input
        # return None combined_input

    # PromptInjection(userInput)
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
    # logger.info(f"[AgentOutput] {assistantOutput}")
    # logger.info(f"[Info] assistantOutput: {assistantOutput}")

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
    # logger.info("Welcome to Personal Assistant CLI")
    print("Welcome to Personal Assistant CLI")

    assistantOutput = Processing("/help")
    if assistantOutput is not None:
        Output(assistantOutput)


def ProcessCLIInput(userInput: str) -> Any:
    """
    Programmatic entry point for external bridges (such as WAHA WhatsApp bridge)
    to process user input through the CLI processing pipeline.
    """
    global USER_INPUT_COUNT
    USER_INPUT_COUNT += 1

    if userInput and len(userInput.strip()) > 0:
        turn = begin_turn(USER_INPUT_COUNT, userInput)
        try:
            assistantOutput = Processing(userInput)
            if assistantOutput is not None:
                Output(assistantOutput)
                set_agent_output(str(assistantOutput))
                return assistantOutput
            else:
                from Log.turn_logger import get_current_turn
                current_turn = get_current_turn()
                if current_turn and not current_turn.agent_output:
                    current_turn.set_agent_output("(No output or command handled)")
                return "(No output or command handled)"
        except Exception as e:
            from Log.turn_logger import get_current_turn
            current_turn = get_current_turn()
            if current_turn:
                current_turn.set_error(f"{type(e).__name__}: {e}")
            raise
        finally:
            end_turn()
    return None


@PrintFunctionName
def Main() -> None:
    """Run a single input -> processing -> output cycle."""
    # PrintFunctionNames("cli Main...")
    global USER_INPUT_COUNT

    USER_INPUT_COUNT += 1
    # logger.debug(f"[Debug] UserInputCount: {USER_INPUT_COUNT}")

    userInput = Input()
    # print(f"userInput after input: {userInput}")
    # if userInput is not None or userInput != "":
    if userInput and len(userInput.strip()) > 0: 
        # Begin turn logging
        turn = begin_turn(USER_INPUT_COUNT, userInput)
        
        try:
            # print(f"userInput before procesing: {userInput}")
            assistantOutput = Processing(userInput)
            if assistantOutput is not None:
                Output(assistantOutput)
                # Set agent output for turn logging
                set_agent_output(str(assistantOutput))
            else:
                # Fallback if processing returned None but an agent output or response was captured during execution
                from Log.turn_logger import get_current_turn
                current_turn = get_current_turn()
                if current_turn and not current_turn.agent_output:
                    current_turn.set_agent_output("(No output or command handled)")
        except Exception as e:
            # Mark turn as having an error, but still log it
            from Log.turn_logger import get_current_turn
            current_turn = get_current_turn()
            if current_turn:
                current_turn.set_error(f"{type(e).__name__}: {e}")
            raise
        finally:
            # Always end the turn to write the log block
            end_turn()


if __name__ == "__main__":
    WelcomeUser()
    while True:
        try:
            Main()
        except KeyboardInterrupt:
            print("\nExiting Personal Assistant CLI...")
            print(f"Log file: {os.path.abspath(log_path)}")
            sys.exit(0)
        except Exception as e:
            # Show the error and keep the REPL alive (e.g. LLM rate limits, network errors).
            # KeyboardInterrupt / SystemExit are not Exceptions, so Ctrl+C and exit still work.
            logger.exception(f"[Error] {type(e).__name__}: {e}")