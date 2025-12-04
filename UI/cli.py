import TextToSpeech.textToSpeechOnline02 as TTS
#import SpeechToText.speechToTextOnline as STT
#import LLM.llm as LLM
#import userInputToScriptInvocation as UITSI
import Langchain.agent as Agent

#from flask import Flask, request
#import requests



import logging

# Create a custom logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # Set global required log level

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler
# file_handler = logging.FileHandler('/tmp/personalAssistant.log')
file_handler = logging.FileHandler('/root/ProjectRpi/Rpi/PersonalAssistant/Log/log.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Console (stream) handler
console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# # Logging examples
# logger.info("start logging")
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.info("stop logging")


# input("Human interrupt")
logger.debug("Initialized assistant.py")


# modeLLM = "globalGemini" # local: Model running locally 
#             # global: Model running on cloud / chatgpt
# modeConversation = "wakeUp"     # sleep: Go to Hibernate
#                         # wakeUp: Goint to answer the user input
# modeInput = "text" # text / speech
# modeOutput = "text" # text / speech
# modeContext = "no" # no: no context in conversation
#             # yes: the conversation understand the context
# modeCommunication = "langchain" # langchain: use langchain agent
#                                 # fabric: use fabric    
# modeMultilineInput = False      # False: user input is in single line
#                                 # True: user input is in muliple lines

listWakeUpCalls = ["hey there", "hi there", "hey rpi"]
listSleepCalls = ["sleep now", "go to sleep", "we are done", "got it"]

roleDefining = f"""For the 'User Input' given below
answer as you are a 'JARVIS' from the 'Iron Man' movie
User Input = """

# ~ roleDefining = f"""For the 'User Input' given below
# ~ answer as you are a 'JARVIS' from the 'Iron Man' movie
# ~ User Input = """


# ~ who is the presedent of india

threadId = 0    # Memory Id for agent graph
mainLoopCnt = 0 # counting looping of Main()

# def InitializingLogging():
#     global logger
#
#     # Create a log file handler
#     # file_handler_log = logging.FileHandler("Logs/log.log")
#     file_handler_log = logging.FileHandler("/tmp/PersonalAssistant/log.log")
#     file_handler_log.setLevel(logging.DEBUG)
#     # file_handler_log.setLevel(logging.INFO)
#
#     # Create a chat file handler
#     # file_handler_chat = logging.FileHandler("Logs/chat.log")
#     # file_handler_chat.setLevel(logging.INFO)
#     # file_handler_log.setLevel(logging.INFO)
#
#     # Create a console handler
#     console_handler = logging.StreamHandler()
#     # console_handler.setLevel(logging.DEBUG)
#     console_handler.setLevel(logging.INFO)
#
#     # Create a formatter and set it for both handlers
#     formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
#     file_handler_log.setFormatter(formatter)
#     file_handler_chat.setFormatter(formatter)
#     console_handler.setFormatter(formatter)
#
#     # Add the handlers to the logger
#     logger.addHandler(file_handler_log)
#     logger.addHandler(file_handler_chat)
#     logger.addHandler(console_handler)
#
#
#     # ~ logging.basicConfig(
#         # ~ level=logging.DEBUG,
#         # ~ format="%(asctime)s %(levelname)s %(message)s",
#         # ~ datefmt="%Y-%m-%d %H:%M:%S",
#         # ~ filename="Logs/basic.log")
#
#     logger.debug("InitializingLogging()")
#     # ~ logging.debug("This is a debug message.")
#     # ~ logging.info("This is an info message.")
#     # ~ logging.warning("This is a warning message.")
#     # ~ logging.error("This is an error message.")
#     # ~ logging.critical("This is a critical message.")

#InitializingLogging()

# mode_config_file = '/tmp/mode_config_file.json'
mode_config_file = '/root/ProjectRpi/Rpi/PersonalAssistant/Log/mode_config_file.json'

# Define full mode configuration with current value and allowed options with descriptions
mode_config_initialization = {
    'mode-llm': {
        'current': 'local',
        'allowed': {
            'local': 'Model running locally',
            'global': 'Model running on cloud / chatgpt',
            'local01': 'test',
            'local-01': 'test',
            '0001local-01': 'test'
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
            'speech': 'Speech input mode'
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



import json
import os


def save_modes(mode_config):
    with open(mode_config_file, 'w') as f:
        json.dump(mode_config, f, indent=4)

def load_modes():
    if os.path.exists(mode_config_file):
        logger.debug("load modes: getting current mode config file")
        with open(mode_config_file, 'r') as f:
            return json.load(f)
    else: # Initialize the MODE_CONFIG_FILE
        logger.debug("load modes: initiaizing the mode config file")
        with open(mode_config_file, 'w') as f:
            json.dump(mode_config_initialization, f, indent=4)
        with open(mode_config_file, 'r') as f:
            return json.load(f)
    # return mode_config


def BasicCmds(userInput):
    # global mode_config
    mode_config_load = load_modes()

    parts = userInput.lower().split()


    if parts[0] == "help":
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
        logger.info(f"{key}: {details['current']}")
        for option, desc in details['allowed'].items():
            logger.info(f"  {option}: {desc}")
        # logger.info()

    return True

    # if userInput.lower() == 'help':
    #     logger.info('Help:')
    #
    # # Example to change modeInput
    # elif userInput.lower() == 'mode input blah':
    #     mode_config['modeInput']['current'] = 'blah'
    #     logger.info("Input mode set to blah")
    #
    # save_modes()
    #
    # # logger.info the values
    # for key, details in mode_config.items():
    #     logger.info(f"{key}: {details['current']}")
    #     for option, desc in details['allowed'].items():
    #         logger.info(f"  {option}: {desc}")
    #     logger.info()


# checkpoint
# save_modes()
# userInput02 = input("testing: ") 
# BasicCmds(userInput02)
# # return 
# # exit
# sys.exit()
# logger.info("still here")

# def BasicCmds(userInput):
#     global logger
#     global modeConversation
#     global modeInput
#     global modeOutput
#     global modeContext
#     global modeLLM
#     global modeCommunication
#     global modeMultilineInput
#
#     logger.infoData = ""
#
#     if (userInput.lower() == "help"):
#         print("Help:")
#         # printData += "CurrentStatus:: modeInput:", modeInput, ":modeOutput:" , modeOutput, ":modeConversation:" , modeConversation, ":modeContext:", modeContext, ":##"
#         # print(printData)
#         # return printData
#
#     # Checking for input mode
#     elif (userInput.lower() == "mode input text"):
#         modeInput = "text"
#
#
#     elif (userInput.lower() == "mode input speech"):
#         modeInput = "speech"
#
#
#     # Checking for output mode
#     elif (userInput.lower() == "mode output text"):
#         modeOutput = "text"
#
#
#     elif (userInput.lower() == "mode output speech"):
#         modeOutput = "speech"
#
#
#     # Checking for wake up call
#     elif any(call in userInput.lower() for call in listWakeUpCalls):
#         modeConversation = "wakeUp"
#
#
#     # Checking for sleep call
#     elif any(call in userInput.lower() for call in listSleepCalls):
#         modeConversation = "sleep"
#
#
#     # checking for mode context 
#     elif (userInput.lower() == "mode context yes"):
#         modeContext = "yes"
#
#
#     elif (userInput.lower() == "mode context no"):
#         modeContext = "no"
#
#
#     # checking for mode LLM
#     elif (userInput.lower() == "mode llm local"):
#         modeLLM = "local"
#
#
#     elif (userInput.lower() == "mode llm global"):
#         modeLLM = "global"
#         modeContext = "no"
#
#     elif (userInput.lower() == "mode llm globalgemini"):
#         modeLLM = "globalGemini"
#         modeContext = "no"
#
#     elif (userInput.lower() == "mode communication langchain"):
#         modeCommunication = "langchain"
#
#     elif (userInput.lower() == "mode communication fabric"):
#         modeCommunication = "fabric"
#
#     elif (userInput.lower() == "mode multilineinput true"):
#         modeMultilineInput = True
#
#     elif (userInput.lower() == "mode multilineinput false"):
#         modeMultilineInput = False
#
#     else:
#         return False
#
#     # print("## modeInput:", modeInput, ":modeOutput:" , modeOutput, ":modeConversation:" , modeConversation, ":modeContext:", modeContext, ":modeLLM:", modeLLM, ":##")
#     printData = "mode [options]: current mode\n"
#     printData += f"mode input [text/speech]: {modeInput}\n"
#     printData += f"mode output [text/speech]: {modeOutput}\n"
#     printData += f"mode conversation [awake/sleep]: {modeConversation}\n"
#     printData += f"mode context [yes/no]: {modeContext}\n"
#     printData += f"mode llm [local/global/globalGemini]: {modeLLM}\n"
#     printData += f"mode communication [langchain/fabric]: {modeCommunication}\n"
#     printData += f"mode multilineinput [true/false]: {modeMultilineInput}\n"
#
#     print(printData)
#     return True
#

import readline

# COMMANDS = ['hello', 'help', 'exit', 'weather', 'time']

COMMANDS = ['mode', 'input', 'text', 'speech', 'output', 'context', 'yes', 'no', 'llm', 'local', 'global', 'globalgemini', 'communication', 'langchain', 'fabric', 'multilineInput', 'True', 'False']

def completer(text, state):
    options = [i for i in COMMANDS if i.startswith(text)]
    if state < len(options):
        return options[state]
    return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")


def Input():    
    global logger
    # global modeInput
    global modeMultilineInput

    ## ## Input ## ##
    # Getting user input
    # userInput = "Hey there how its going on?" # sample 
    if (GetModeValue("mode-input") == "text"):
        # print(f"cli input GetModeValue(mode-multiline-input): {GetModeValue("mode-multiline-input")}")
        if ((GetModeValue("mode-multiline-input")) == "true"):
            logger.info("Paste your multiline input followed by Ctrl-D (Linux/macOS) or Ctrl-Z then Enter (Windows):")
            userInput = sys.stdin.read()
        else:
            userInput = input("userInput: ")    # Text 
    elif(modeInput == "speech"):
        userInput = STT.Main()          # Speech To Text
    else:
        logger.info("Error: Invalid modeInput:", modeInput)

    # ~ logger.info("userInput:",userInput)   
    logger.info(f"userInput: {userInput}")
    return userInput

import subprocess

def GetModeValue(mode_name):
    mode_config = load_modes()
    return mode_config[mode_name]['current']

# logger.info(GetModeValue("mode-conversation"))
# hahahah

def Processing(userInput):
    global logger
    # global modeConversation
    
    basicCmdReturn = BasicCmds(userInput)
    # logger.info(f"Processing basicCmdReturn: {basicCmdReturn} : type: {type(basicCmdReturn)} ")

    if(basicCmdReturn):
        # logger.info("Processing: UserInput is in BasicCmds")
        return
    # else: 
    #     logger.info("Processing: UserInput is NOT in BasicCmds")
    
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
            #userInput = "who is the PM of India?"
            #agentResponse = requests.get(f"http://agent_langchain:5011/?userInput={userInput}&threadId={threadId}")
            #logger.info(":agentResp:", agentResponce)
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

def Output(assistantOutput):
    global logger
    # global modeOutput

    logger.info(f"assistantOutput: {assistantOutput}")  # Text 
    
    if (GetModeValue("mode-output") == "text"):
        return
    elif (GetModeValue("mode-output") == "speech"):   
        TTS.Main(assistantOutput)           # Text to speech
    else:
        logger.info("Error: Invalid modeOutput:", modeOutput)
            

## ## FLASK APP INITIALIZATION ## ##

#app = Flask(__name__)
# Set debug mode to True
#app.debug = True

import sys

#@app.route('/')
def Main():
    global logger
    global mainLoopCnt
    #return "this is from ui app"


    mainLoopCnt += 1
    logger.debug(f"mainLoopCnt: {mainLoopCnt}")

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

def WelcomeUser():
    global logger
    logger.info("WelcomeUser()")
    
    logger.info("Welcome to Personal Assistant CLI")
    logger.info("Type 'help' for list of commands")
    
    assistantOutput = Processing("help")

    if (assistantOutput is not None):
        #logger.info("final:", assistantOutput)
        # return
        Output(assistantOutput)

#if __name__ == '__main__':
#   app.run(host='0.0.0.0', port=5010)
# Welcome User script
WelcomeUser()

while(True):
    Main()

# userInput = "The current Prime Minister of India is Narendra Modi. He has been in office since 2014 and is serving his third term as Prime Minister."
# Output(userInput)
    
# ~ userInput = "Give me a youtube video link on valorant"
# ~ step 1 find youtube video link of valorant, step 2 run firefox cmd with that link
# ~ Do 1 step at a time. step 1 get 2 youtube video links of valorant game, step 2 draft a mail to my brother ved with these links
# ~ Do 1 step at a time. step 1 find top 3 music artist, step 2 get 2 youtube video links of each artist from the 3 artist, step 3 draft a mail to my brother ved with these links

