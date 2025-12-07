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
import TextToSpeech.textToSpeechOnline02 as TTS
#import SpeechToText.speechToTextOnline as STT
#import LLM.llm as LLM
#import userInputToScriptInvocation as UITSI
import Langchain.agent as Agent

#from flask import Flask, request
#import requests

# import Log.custom_logger.logger as logger
from Log.custom_logger import logger

# input("Human interrupt")
# logger.debug("Initialized assistant.py")
logger.debug("Initialized assistant.py")

import json
import os

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


modeConfigFilePath = '/root/ProjectRpi/Rpi/PersonalAssistant/Log/modeConfigFilePath.json'
userInputFile = '/root/ProjectRpi/Rpi/PersonalAssistant/Log/userInput.txt'

# Define full mode configuration with current value and allowed options with descriptions
modeConfigInitializationJson = {
    'mode-llm': {
        'current': 'local',
        'allowed': {
            'local': 'Model running locally',
            'global': 'Model running on cloud / chatgpt'
        }
    },
    'mode-conversation': {
        'current': 'wakeUp',
        'allowed': {
            'sleep': 'Go to Hibernate',
            'wakeUp': 'Goint to answer the user input'
        }
    },
    'mode-input': {
        'current': 'text',
        'allowed': {
            'text': 'Text input mode',
            'speech': 'Speech input mode',
            'file': 'Read for the userInput.txt file'
        }
    },
    'mode-output': {
        'current': 'text',
        'allowed': {
            'text': 'Text output mode',
            'speech': 'Speech output mode'
        }
    },
    'mode-context': {
        'current': 'yes',
        'allowed': {
            'no': 'No context in conversation',
            'yes': 'The conversation understands the context'
        }
    },
    'mode-communication': {
        'current': 'langchain',
        'allowed': {
            'langchain': 'Use langchain agent',
            'fabric': 'Use fabric'
        }
    },
    'mode-multiline-input': {
        'current': 'true',
        'allowed': {
            'false': 'User input is in single line',
            'true': 'User input is in multiple lines'
        }
    }
}

COMMANDS = ['mode', 'input', 'text', 'speech', 'output', 'context', 'yes', 'no', 'llm', 'local', 'global', 'globalgemini', 'communication', 'langchain', 'fabric', 'multilineInput', 'True', 'False']

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
def save_modes(mode_config):
    with open(modeConfigFilePath, 'w') as f:
        json.dump(mode_config, f, indent=4)

# Load modes from the config file
def load_modes():
    if os.path.exists(modeConfigFilePath):
        logger.debug("load modes: getting current mode config file")
        with open(modeConfigFilePath, 'r') as f:
            return json.load(f)
    else: # Initialize the modeConfigFilePath
        logger.debug("load modes: initiaizing the mode config file")
        with open(modeConfigFilePath, 'w') as f:
            json.dump(modeConfigInitializationJson, f, indent=4)
        with open(modeConfigFilePath, 'r') as f:
            return json.load(f)
    # return mode_config

# Get a specific mode value
def GetModeValue(mode_name):
    mode_config = load_modes()
    return mode_config[mode_name]['current']

# Check for the basic cmds like help, mode change
def BasicCmds(userInput):
    mode_config_load = load_modes()

    parts = userInput.lower().split()


    if parts[0] == "help":
        FormatMessageTypes("SystemMessage")
        logger.info('Help:')

    # Check if user input matches the pattern: mode <mode-name> <mode-value>
    elif len(parts) == 3 and parts[0] == 'mode':
        mode_name = 'mode-' + parts[1]  # construct key, e.g. 'modeInput'
        mode_value = parts[2]
        if mode_name in mode_config_load:
            if mode_value in mode_config_load[mode_name]['allowed']:
                mode_config_load[mode_name]['current'] = mode_value
                logger.info(f"Set {mode_name} to {mode_value}")
                save_modes(mode_config_load)
            else:
                logger.info(f"Invalid option '{mode_value}' for {mode_name}. Use 'help' to see allowed options.")
        else:
            logger.info(f"Invalid mode '{mode_name}'. Use 'help' to see available modes.")
    
    else:
        # logger.info("Invalid mode. Use 'help' to see available modes.")

        return False

    for key, details in mode_config_load.items():
        key = key.replace("-", " ", 1) # replace - in front of the mode
        # print(f"key: {key}")
        logger.info(f"{key}: {details['current']}")
        for option, desc in details['allowed'].items():
            logger.info(f"  {option}: {desc}")

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
    global modeMultilineInput

    FormatMessageTypes("HumanMessage")
    modeInput = GetModeValue("mode-input")
    if (modeInput == "text"):
        if ((GetModeValue("mode-multiline-input")) == "true"):
            logger.info("Paste your multiline input followed by Ctrl-D (Linux/macOS) or Ctrl-Z (Windows) then Enter:")
            userInput = sys.stdin.read()
        else:
            # userInput = input("userInput: ")    # Text 
            userInput = input("")    # Text 
            # userInput = "whats my and my pets name?"
    elif(modeInput == "file"):
        # print("cli input file")
        userInput = ReadUserInputFile()
        print(userInput)
        userChoice = input("Change mode input text (N/y): ")
        if userChoice == "y":
            userInput = "mode input text"
    elif(modeInput == "speech"):
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
        
        # if(modeCommunication == "langchain"):
        if (GetModeValue("mode-communication") == "langchain"):
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
            agentResponce = Agent.Main(userInput, threadId, GetModeValue("mode-llm"))
            return agentResponce

        # elif(modeCommunication == "fabric"):
        if (GetModeValue("mode-communication") == "langchain"):
            logger.info("modeCommunication: fabric")
            # /home/ssbrpi/Project/Fabric/fabricPattern.sh <pattern_name>
            # Fabric pattern calling
            # script_path = "/home/ssbrpi/Project/Fabric/fabricPattern.sh"
            # script_path = "/root/Project/Fabric/fabricPattern.sh"
            script_path = "/root/Project/Fabric/fabric"

            # pattern_name = userInput.strip().replace(" ", "_").lower()

            # logger.info("Running:: ", script_path, " --version")
            logger.info("Running:: ", script_path, userInput)

            try:
                result = subprocess.run(
                    [script_path, userInput],
                    # [script_path, "--version"],
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                logger.info("Script output:")
                logger.info(result.stdout)
            except subprocess.CalledProcessError as e:
                logger.info("Script failed with error:")
                logger.info(e.stderr)

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
