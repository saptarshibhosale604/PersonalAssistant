## IMPORT ##
# # # # # # # # # # # # # # # # # # # # # 
#    ___ __  __ ____   ___  ____ ___:_    #
#   |_ _|  \/  |  _ \ / _ \|  _ \_   _|   #
#    | || |\/| | |_) | | | | |_) || |     #
#    | || |  | |  __/| |_| |  _ < | |     #
#   |___|_|  |_|_|    \___/|_| \_\|_|     #
#                                         #
#                                         #
# # # # # # # # # # # # # # # # # # # # # 

import sys
import subprocess
import readline
# import TextToSpeech.textToSpeechOnline02 as TTS
from typing import Any, Iterable
#import SpeechToText.speechToTextOnline as STT
#import LLM.llm as LLM
#import userInputToScriptInvocation as UITSI
import Langchain.agent as Agent
import UserContext.userContext as UserContext
import Fabric.manager as Fabric

#from flask import Flask, request
#import requests

# import Log.custom_logger.logger as logger
from Log.custom_logger import logger

# input("Human interrupt")
# logger.debug("Initialized assistant.py")
logger.debug("Initialized assistant.py")

import json
import os

# Custom scripts
import Langchain.Tools.toolsManager as toolsManager
import UI.modesTUI as modesTUI
# import Langchain.Tools.modesTUI as modesTUI

## VARIABLES ##
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#   __     ___    ____  ___    _    ____  _     _____ ____     #
#   \ \   / / \  |  _ \|_ _|  / \  | __ )| |   | ____/ ___|    #
#    \ \ / / _ \ | |_) || |  / _ \ |  _ \| |   |  _| \___ \    #
#     \ V / ___ \|  _ < | | / ___ \| |_) | |___| |___ ___) |   #
#      \_/_/   \_\_| \_\___/_/   \_\____/|_____|_____|____/    #
#                                                              #
#                                                              #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


listWakeUpCalls = ["hey there", "hi there", "hey rpi"]
listSleepCalls = ["sleep now", "go to sleep", "we are done", "got it"]

threadId = 0    # Memory Id for agent graph
UserInputCount = 0 # counting looping of Main()


# modeConfigFilePath = '/root/ProjectRpi/Rpi/PersonalAssistant/Log/modeConfigFilePath.json'
# modeConfigFilePath = "/root/ProjectRpi/Rpi/PersonalAssistant/Langchain/Tools/toolsConfig.json"
# modeConfigFilePath = "/root/ProjectRpi/Rpi/PersonalAssistant/Langchain/Tools/modesConfig.json"
modeConfigFilePath = "/root/ProjectRpi/Rpi/PersonalAssistant/UI/modesConfig.json"
modeConfigSandboxFilePath = "/root/ProjectRpi/Rpi/PersonalAssistant/UI/modesConfigSandbox.json"
userInputFile = '/root/ProjectRpi/Rpi/PersonalAssistant/Log/userInput.txt'
modeSandbox = "false"


# Define full mode configuration with current value and allowed options with descriptions
# modeConfigInitializationJson = {
#     'mode-llm': {
#         'current': 'local',
#         'allowed': {
#             'local': 'Model running locally',
#             'global': 'Model running on cloud / chatgpt'
#         }
#     },
#     'mode-conversation': {
#         'current': 'wakeUp',
#         'allowed': {
#             'sleep': 'Go to Hibernate',
#             'wakeUp': 'Goint to answer the user input'
#         }
#     },
#     'mode-input': {
#         'current': 'text',
#         'allowed': {
#             'text': 'Text input mode',
#             'speech': 'Speech input mode',
#             'file': 'Read for the userInput.txt file',
#             'multiline': 'Text input mode multiline'
#         }
#     },
#     'mode-output': {
#         'current': 'text',
#         'allowed': {
#             'text': 'Text output mode',
#             'speech': 'Speech output mode'
#         }
#     },
#     'mode-context': {
#         'current': 'yes',
#         'allowed': {
#             'no': 'No context in conversation',
#             'yes': 'The conversation understands the context'
#         }
#     },
#     'mode-framework': {
#         'current': 'langchain',
#         'allowed': {
#             'langchain': 'Use langchain agent',
#             'fabric': 'Use fabric'
#         }
#     },
#     'mode-tools': {
#         'current': 'update',
#         'allowed': {
#             'get': 'get list of tools',
#             'update': 'update the list of tools'
#         }
#     },
#     'mode-reset': {
#         'current': 'now',
#         'allowed': {
#             'now': 'mode reset now',
#         }
#     }
# }
#
COMMANDS = ['mode', 'input', 'text', 'speech', 'output', 'context', 'yes', 'no', 'llm', 'local', 'global', 'globalgemini', 'framework', 'langchain', 'fabric', 'True', 'False', 'multiline']

## FUNCTIONS ##
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#    _____ _   _ _   _  ____ _____ ___ ___  _   _ ____     #
#   |  ___| | | | \ | |/ ___|_   _|_ _/ _ \| \ | / ___|    #
#   | |_  | | | |  \| | |     | |  | | | | |  \| \___ \    #
#   |  _| | |_| | |\  | |___  | |  | | |_| | |\  |___) |   #
#   |_|    \___/|_| \_|\____| |_| |___\___/|_| \_|____/    #
#                                                          #
#                                                          #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


# Save modes to the config file
# def save_modes(mode_config):
#     with open(modeConfigFilePath, 'w') as f:
#         json.dump(mode_config, f, indent=4)

# Load modes from the config file
def load_modes():
    global modeConfigSandboxFilePath
    global modeConfigFilePath
    global modeSandbox

    # print(f"load_modes: modeSandbox: {modeSandbox}")
    if modeSandbox == "true":
       modeConfigFilePath = modeConfigSandboxFilePath

    # print(f"modeConfigFilePath cli load_modes modeConfigFilePath: {modeConfigFilePath}")

    if os.path.exists(modeConfigFilePath):
        logger.debug("load modes: getting current mode config file")
        with open(modeConfigFilePath, 'r') as f:
            return json.load(f)
    else: # Initialize the modeConfigFilePath
        logger.debug("load modes: initiaizing the mode config file")
        # print("load modes: initiaizing the mode config file")
        # modesTUI.LoadConfigurationFromFile(modeSandbox)        # with open(modeConfigFilePath, 'w') as f:
        modesTUI.LoadConfigurationFromFile(modeSandbox = modeSandbox)        # with open(modeConfigFilePath, 'w') as f:
        return None
        #     json.dump(modeConfigInitializationJson, f, indent=4)
        # with open(modeConfigFilePath, 'r') as f:
        #     return json.load(f)
    # return mode_config

def UpdateModeValue(mode_name, mode_value):
    # global defaultConfig
    global modeConfigFilePath 
    global modeConfigSandboxFilePath


    mode_config = load_modes() 
    # input(f"before mode_config: {mode_config} ::")
    mode_config[mode_name] = mode_value
    # input(f"after mode_config: {mode_config} ::")

    # print(f"load_modes: modeSandbox: {modeSandbox}")
    if modeSandbox == "true":
       modeConfigFilePath = modeConfigSandboxFilePath

    # print(f"modeConfigFilePath cli UpdateModeValue modeConfigFilePath: {modeConfigFilePath}")

    with open(modeConfigFilePath, 'w') as file:
        json.dump(mode_config, file, indent=2)

    print()

# Get all the mode values from the config file
def GetAllModeValues():
    mode_config = load_modes()
    for key, value in mode_config.items():
        print(f"  {key:<27} → {value}")

# Get a specific mode value
def GetModeValue(mode_name):
    mode_config = load_modes()
    # input(f"mode_config: {mode_config}::")
    # input(f"mode_name: {mode_name}::")
    # input(f"mode_config[mode_name]: {mode_config[mode_name]}::")
    # return mode_config[mode_name]['current']
    return mode_config[mode_name]

# Reset/ drop the mode value
def DropModeConfigFile():
    # Check if file exists before deleting
    if os.path.exists(modeConfigFilePath):
        os.remove(modeConfigFilePath)
        print(f"File '{modeConfigFilePath}' has been deleted successfully.")
    else:
        print(f"File '{modeConfigFilePath}' does not exist.")



def FormatToolsPrinting(tools: Iterable[Any]) -> None:
    """
    Print tools in the format: <toolName>: <toolDescription>
    Supports LangChain StructuredTool/BaseTool, dicts, and callables with attributes.
    """
    for i, tool in enumerate(tools, start=1):
        name = None
        desc = None

        # LangChain StructuredTool or BaseTool
        if hasattr(tool, "name") and hasattr(tool, "description"):
            name = getattr(tool, "name", None)
            desc = getattr(tool, "description", None)

        # Dict-like tool
        elif isinstance(tool, dict):
            name = tool.get("name")
            desc = tool.get("description")

        # Callable with attributes (less common)
        elif callable(tool) and hasattr(tool, "__name__"):
            name = getattr(tool, "__name__", None)
            # Try to fetch a custom description attribute or docstring
            desc = getattr(tool, "description", None) or getattr(tool, "__doc__", None)

        # Fallback: try generic representation
        if not name:
            name = f"tool_{i}"

        if not desc:
            desc = "(no description available)"

        # print(f"{name}: {desc}")
        desc = desc.split('\n')[0].rstrip()  # create list of line, [0]:Selects first line, rstrip() removes trailing whitespace
        print(f"{name}: {desc}")
        # if 1 < len(print(f"{name}: {desc}")) < 3:
        #     print(f"{name}: {desc}")


# Check for the basic cmds like help, mode change
def BasicCmds(userInput):
    global modeSandbox
    mode_config_load = load_modes()

    parts = userInput.lower().split()


    if parts[0] == "help":
        FormatMessageTypes("SystemMessage")
        logger.info('Help:')
        GetAllModeValues()

    # Check if user input matches the pattern: mode <mode-name> <mode-value>
    elif len(parts) <= 3  and parts[0] == 'mode':
        mode_name = 'mode-' + parts[1]  # construct key, e.g. 'modeInput'
        mode_value = None
        if len(parts) > 2 and parts[2]:
            mode_value = parts[2]

        print(f"BasicCmds {mode_name} ==> {mode_value}")

        # if mode_name in mode_config_load:
        #     if mode_value in mode_config_load[mode_name]['allowed']:
        #         mode_config_load[mode_name]['current'] = mode_value
        #         logger.info(f"Set {mode_name} to {mode_value}")
        #         save_modes(mode_config_load)
        #     else:
        #         logger.info(f"Invalid option '{mode_value}' for {mode_name}. Use 'help' to see allowed options.")

        # else:
        #     logger.info(f"Invalid mode '{mode_name}'. Use 'help' to see available modes.")
        if mode_name == "mode-input":
            UpdateModeValue(mode_name, mode_value)
            return True

        elif mode_name == "mode-llm":
            UpdateModeValue(mode_name, mode_value)
            return True
    
        elif mode_name == "mode-get":
            # input("mode-get")
            GetAllModeValues()
            # modesTUI.Main()
            return True

        elif mode_name == "mode-update":
            # input("Entering modesTUI.Main()::")
            if modeSandbox == "true":
                modesTUI.Main(modeSandbox)
            else:
                modesTUI.Main()
            return True

        elif mode_name == "mode-sandbox":
            modeSandbox = mode_value
            modesTUI.LoadConfigurationFromFile(modeSandbox = modeSandbox)
            GetAllModeValues()
            return True

        elif mode_name == "mode-tools":
            if mode_value == "update":
                # input("Human00 tools update")
                tools = toolsManager.Main(mode_value) # "update" : update tools list
                FormatToolsPrinting(tools)
                # print(f"toolsManager tools: {tools}")
                # input("Human01")
            elif mode_value == "get":
                # input("Human00 tools get")
                tools = toolsManager.Main(mode_value) # "get" : get tools list
                FormatToolsPrinting(tools)
                # print(f"toolsManager tools: {tools}")
                # input("Human01")
            return True
        elif mode_name == "mode-reset":
            # input("human reset")
            DropModeConfigFile()
            return True
    else:
        # logger.info("Invalid mode. Use 'help' to see available modes.")

        return False

    # for key, details in mode_config_load.items():
    #     key = key.replace("-", " ", 1) # replace - in front of the mode
    #     # print(f"key: {key}")
    #     logger.info(f"{key}: {details['current']}")
    #     for option, desc in details['allowed'].items():
    #         logger.info(f"  {option}: {desc}")

    FormatMessageTypes("")
    print()
    return True


# Auto completion feature after pressing Tab
def completer(text, state):
    options = [i for i in COMMANDS if i.startswith(text)]
    if state < len(options):
        return options[state]
    return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")


# Format the AI, Human, Tool message types
def FormatMessageTypes(text):
    total_width = 60
    # total_width = 61
    text_length = len(text)
    padding = (total_width - text_length - 4) // 2
    print("=" * padding + " " + text + " " + "=" * padding)

# Read userInput.txt file
def ReadUserInputFile():
    if os.path.exists(userInputFile):
        # logger.debug("load modes: getting current mode config file")
        with open(userInputFile, 'r') as f:
            return f.read()
    else:
        print("The userInput File do not exist")

# Get user input
def Input():    
    global logger
    global modeSandbox

    # global modeMultilineInput

    if modeSandbox == "true":
        FormatMessageTypes("HumanMessage:Sandbox")
    else:
        FormatMessageTypes("HumanMessage")

    modeInput = GetModeValue("mode-input")

    if (modeInput == "text"):
        # if ((GetModeValue("mode-multiline-input")) == "true"):
        userInput = input("")    # Text 
        # userInput = "whats my and my pets name?"
    elif (modeInput == "multiline"):
        logger.info("Paste your multiline input followed by Ctrl-D (Linux/macOS) or Ctrl-Z (Windows) then Enter:")
        userInput = sys.stdin.read()
    elif (modeInput == "file"):
        # print("cli input file")
        userInput = ReadUserInputFile()
        print(userInput)
        userChoice = input("Change to mode input text (N/y): ")
        if userChoice == "y":
            userInput = "mode input text"
    elif (modeInput == "speech"):
        userInput = STT.Main()          # Speech To Text
    else:
        logger.info("Error: Invalid modeInput:", modeInput)

    logger.debug(f"userInput: {userInput}")
    FormatMessageTypes("")
    return userInput

# Process user input
def Processing(userInput):
    global logger
    
    basicCmdReturn = BasicCmds(userInput)

    if(basicCmdReturn):
        return
    
    # for debug only conversation mode only wake up
    # ~ modeConversation = "wakeUp"
    
        
    # ~ # Checking for sleep call
    # ~ if any(call in userInput.lower() for call in listSleepCalls):
        # ~ modeConversation = "sleep"
        
    # if(debug01): logger.info("modeConversation:",modeConversation)
    
    # if (modeConversation == "wakeUp"):
    if (GetModeValue("mode-conversation") == "wakeUp"):
        # userInputToScriptInvocation
        
        # ~ terminalOutput = UITSI.Main(userInput)
        # ~ logger.info(f"TerminalOutput: {terminalOutput}")
        
        # ~ if(terminalOutput is not None):
            # ~ # LLM User Responce generation
        # ~ else:
            # ~ # LLM General Question
        
        
        # define role to userInput
        # userInput = roleDefining + userInput          
        # logger.debug(f"userInputWithDefinedRole: {userInput}")
        
        # if(modeFramework == "langchain"):
        modeFramework = GetModeValue("mode-framework")
        # if (GetModeValue("mode-Framework") == "langchain"):
        if (modeFramework == "langchain"):
            # Getting responce from LLM model
            # llmResponce = LLM.Main(userInput)
            
            #logger.info("agentResponce:")
            global threadId
            # global modeLLM
            # global modeContext

            # if(modeContext == "no"):
            if (GetModeValue("mode-context") == "no"):
                threadId += 1 # Always changing memory variable
            
            #agentResponce = "Na"   
            # agentResponce = Agent.Main(userInput, threadId, GetModeValue("mode-llm"), GetModeValue("mode-context"))
            UserContext.Main(userInput)
            agentResponce = Agent.Main(userInput, threadId, GetModeValue("mode-llm"))
            return agentResponce

        elif (modeFramework == "fabric"):
        # if (GetModeValue("mode-Framework") == "langchain"):
            logger.info("modeFramework: fabric")
            
            # agentResponce = Fabric.Main(userInput, threadId, GetModeValue("mode-llm"))
            agentResponce = Fabric.Main(userInput, GetModeValue("mode-llm"))
            # /home/ssbrpi/Project/Fabric/fabricPattern.sh <pattern_name>
            # Fabric pattern calling
            # script_path = "/home/ssbrpi/Project/Fabric/fabricPattern.sh"
            # script_path = "/root/Project/Fabric/fabricPattern.sh"
            # script_path = "/root/Project/Fabric/fabric"
            #
            # # pattern_name = userInput.strip().replace(" ", "_").lower()
            #
            # # logger.info("Running:: ", script_path, " --version")
            # logger.info("Running:: ", script_path, userInput)
            #
            # try:
            #     result = subprocess.run(
            #         [script_path, userInput],
            #         # [script_path, "--version"],
            #         check=True,
            #         text=True,
            #         stdout=subprocess.PIPE,
            #         stderr=subprocess.PIPE
            #     )
            #     logger.info("Script output:")
            #     logger.info(result.stdout)
            # except subprocess.CalledProcessError as e:
            #     logger.info("Script failed with error:")
            #     logger.info(e.stderr)

# Output the assistant output
def Output(assistantOutput):
    global logger
    # global modeOutput

    logger.debug(f"assistantOutput: {assistantOutput}")  # Text 
    
    if (GetModeValue("mode-output") == "text"):
        return
    elif (GetModeValue("mode-output") == "speech"):   
        TTS.Main(assistantOutput)           # Text to speech
    else:
        logger.info("Error: Invalid modeOutput:", modeOutput)

# welcoming the user with some help
def WelcomeUser():
    global logger
    logger.debug("WelcomeUser()")
    
    logger.info("Welcome to Personal Assistant CLI")
    logger.info("Type 'help' for list of commands")
    
    assistantOutput = Processing("help")

    if (assistantOutput is not None):
        #logger.info("final:", assistantOutput)
        # return
        Output(assistantOutput)
        
# Main function
def Main():
    global logger
    global UserInputCount
    #return "this is from ui app"


    UserInputCount += 1
    logger.debug(f"UserInputCount: {UserInputCount}")

    # userInput = ""
    # userInput = "Give me list of 3 fruits"

    userInput = Input()
    #userInput = request.args.get('userInput', 'how are you?')

    #logger.info("userInput:",userInput)

    if (userInput is not None):

        # if(debug01): logger.info("input Not null")
        assistantOutput = Processing(userInput)

        if (assistantOutput is not None):
            #logger.info("final:", assistantOutput)
            # return
            Output(assistantOutput)

# call Welcome User script
WelcomeUser()

while(True):
    Main()

## OTHER ##
# # # # # # # # # # # # # # # # # # # 
#     ___ _____ _   _ _____ ____     #
#    / _ \_   _| | | | ____|  _ \    #
#   | | | || | | |_| |  _| | |_) |   #
#   | |_| || | |  _  | |___|  _ <    #
#    \___/ |_| |_| |_|_____|_| \_\   #
#                                    #
#                                    #
# # # # # # # # # # # # # # # # # # # 

# userInput = "The current Prime Minister of India is Narendra Modi. He has been in office since 2014 and is serving his third term as Prime Minister."
# Output(userInput)
    
# ~ userInput = "Give me a youtube video link on valorant"
# ~ step 1 find youtube video link of valorant, step 2 run firefox cmd with that link
# ~ Do 1 step at a time. step 1 get 2 youtube video links of valorant game, step 2 draft a mail to my brother ved with these links
# ~ Do 1 step at a time. step 1 find top 3 music artist, step 2 get 2 youtube video links of each artist from the 3 artist, step 3 draft a mail to my brother ved with these links

# which are the top 5 smallest file / directory in my current working directory except current working directory?
# which are the top 5 smallest file / directory in my current working directory in my PC?
# Generate a peom on money
# whats my and my pets name?
