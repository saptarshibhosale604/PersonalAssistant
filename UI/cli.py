import TextToSpeech.textToSpeechOnline02 as TTS
#import SpeechToText.speechToTextOnline as STT
#import LLM.llm as LLM
#import userInputToScriptInvocation as UITSI
import Langchain.agent as Agent

#from flask import Flask, request
#import requests


debug01 = True

print("Initialized assistant.py")


modeLLM = "local" # local: Model running locally 
			# global: Model running on cloud / chatgpt
modeConversation = "wakeUp" 	# sleep: Go to Hibernate
	                  	# wakeUp: Goint to answer the user input
modeInput = "text" # text / speech
modeOutput = "text" # text / speech
modeContext = "yes" # no: no context in conversation

			# yes: the conversation understand the context
	
listWakeUpCalls = ["hey there", "hi there", "hey rpi"]
listSleepCalls = ["sleep now", "go to sleep", "we are done", "got it"]

roleDefining = f"""For the 'User Input' given below
answer as you are a 'JARVIS' from the 'Iron Man' movie
User Input = """

# ~ roleDefining = f"""For the 'User Input' given below
# ~ answer as you are a 'JARVIS' from the 'Iron Man' movie
# ~ User Input = """


# ~ who is the presedent of india

threadId = 0	# Memory Id for agent graph
mainLoopCnt = 0 # counting looping of Main()

import logging

# Create a logger
logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)



def InitializingLogging():
	global logger
	
	# Create a log file handler
	file_handler_log = logging.FileHandler("Logs/log.log")
	file_handler_log.setLevel(logging.DEBUG)
	# file_handler_log.setLevel(logging.INFO)

	# Create a chat file handler
	file_handler_chat = logging.FileHandler("Logs/chat.log")
	file_handler_chat.setLevel(logging.INFO)
	# file_handler_log.setLevel(logging.INFO)

	# Create a console handler
	console_handler = logging.StreamHandler()
	# console_handler.setLevel(logging.DEBUG)
	console_handler.setLevel(logging.INFO)

	# Create a formatter and set it for both handlers
	formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
	file_handler_log.setFormatter(formatter)
	file_handler_chat.setFormatter(formatter)
	console_handler.setFormatter(formatter)

	# Add the handlers to the logger
	logger.addHandler(file_handler_log)
	logger.addHandler(file_handler_chat)
	logger.addHandler(console_handler)

	
	# ~ logging.basicConfig(
		# ~ level=logging.DEBUG,
		# ~ format="%(asctime)s %(levelname)s %(message)s",
		# ~ datefmt="%Y-%m-%d %H:%M:%S",
		# ~ filename="Logs/basic.log")
		
	logger.debug("InitializingLogging()")
    # ~ logging.debug("This is a debug message.")
    # ~ logging.info("This is an info message.")
    # ~ logging.warning("This is a warning message.")
    # ~ logging.error("This is an error message.")
    # ~ logging.critical("This is a critical message.")

#InitializingLogging()

def BasicCmds(userInput):
	global logger
	global modeConversation
	global modeInput
	global modeOutput
	global modeContext
	global modeLLM
	
	printData = ""

	if (userInput.lower() == "help"):
		print("Help:")
		# printData += "CurrentStatus:: modeInput:", modeInput, ":modeOutput:" , modeOutput, ":modeConversation:" , modeConversation, ":modeContext:", modeContext, ":##"
		# print(printData)
		# return printData

	# Checking for input mode
	elif (userInput.lower() == "mode input text"):
		modeInput = "text"
		
	
	elif (userInput.lower() == "mode input speech"):
		modeInput = "speech"
		

	# Checking for output mode
	elif (userInput.lower() == "mode output text"):
		modeOutput = "text"
		
	
	elif (userInput.lower() == "mode output speech"):
		modeOutput = "speech"
		

	# Checking for wake up call
	elif any(call in userInput.lower() for call in listWakeUpCalls):
		modeConversation = "wakeUp"
		
	
	# Checking for sleep call
	elif any(call in userInput.lower() for call in listSleepCalls):
		modeConversation = "sleep"
		

	# checking for mode context 
	elif (userInput.lower() == "mode context yes"):
		modeContext = "yes"
		

	elif (userInput.lower() == "mode context no"):
		modeContext = "no"
		

	# checking for mode LLM
	elif (userInput.lower() == "mode llm local"):
		modeLLM = "local"
		

	elif (userInput.lower() == "mode llm global"):
		modeLLM = "global"
		

	else:
		return False

	# print("## modeInput:", modeInput, ":modeOutput:" , modeOutput, ":modeConversation:" , modeConversation, ":modeContext:", modeContext, ":modeLLM:", modeLLM, ":##")
	printData = "mode [options]: current mode\n"
	printData += f"mode input [text/speech]: {modeInput}\n"
	printData += f"mode output [text/speech]: {modeOutput}\n"
	printData += f"mode conversation [awake/sleep]: {modeConversation}\n"
	printData += f"mode context [yes/no]: {modeContext}\n"
	printData += f"mode llm [local/global]: {modeLLM}\n"
	
	print(printData)
	return True

def Input():	
	global logger
	global modeInput
		
	## ## Input ## ##
	# Getting user input
	# userInput = "Hey there how its going on?" # sample 
	if(modeInput == "text"):
		userInput = input("userInput: ")	# Text 
	elif(modeInput == "speech"):
		userInput = STT.Main()			# Speech To Text
	else:
		print("Error: Invalid modeInput:", modeInput)
	
	# ~ print("userInput:",userInput)	
	logger.info(f"userInput: {userInput}")
	return userInput
	
def Processing(userInput):
	global logger
	global modeConversation
	
	
	if(BasicCmds(userInput)):
		return
		
	
	# for debug only conversation mode only wake up
	# ~ modeConversation = "wakeUp"
	
		
	# ~ # Checking for sleep call
	# ~ if any(call in userInput.lower() for call in listSleepCalls):
		# ~ modeConversation = "sleep"
		
	# if(debug01): print("modeConversation:",modeConversation)
	
	if (modeConversation == "wakeUp"):
		# userInputToScriptInvocation
		
		# ~ terminalOutput = UITSI.Main(userInput)
		# ~ print(f"TerminalOutput: {terminalOutput}")
		
		# ~ if(terminalOutput is not None):
			# ~ # LLM User Responce generation
		# ~ else:
			# ~ # LLM General Question
		
		
		# define role to userInput
		# userInput = roleDefining + userInput			
		logger.debug(f"userInputWithDefinedRole: {userInput}")
		
		# Getting responce from LLM model
		# llmResponce = LLM.Main(userInput)
		
		#print("agentResponce:")
		global threadId
		global modeLLM
		global modeContext

		if(modeContext == "no"):
			threadId += 1 # Always changing memory variable
		
		#agentResponce = "Na"	
		agentResponce = Agent.Main(userInput, threadId, modeLLM, modeContext)
		#userInput = "who is the PM of India?"
		#agentResponse = requests.get(f"http://agent_langchain:5011/?userInput={userInput}&threadId={threadId}")
		#print(":agentResp:", agentResponce)
		return agentResponce

def Output(assistantOutput):
	global logger
	global modeOutput

	logger.info(f"assistantOutput: {assistantOutput}")	# Text 
	
	if(modeOutput == "text"):
		return
	elif(modeOutput == "speech"):	
		TTS.Main(assistantOutput) 			# Text to speech
	else:
		print("Error: Invalid modeOutput:", modeOutput)
			

## ## FLASK APP INITIALIZATION ## ##

#app = Flask(__name__)
# Set debug mode to True
#app.debug = True

#@app.route('/')
def Main():
	global logger
	global mainLoopCnt
	#return "this is from ui app"
	
	mainLoopCnt += 1
	logger.info(f"mainLoopCnt: {mainLoopCnt}")
	
	# userInput = "Give me list of 3 fruits"
	userInput = Input()
	#userInput = request.args.get('userInput', 'how are you?')
	
	#print("userInput:",userInput)
	
	if (userInput is not None):

		# if(debug01): print("input Not null")
		assistantOutput = Processing(userInput)

		if (assistantOutput is not None):
			#print("final:", assistantOutput)
			# return
			Output(assistantOutput)


#if __name__ == '__main__':
#	app.run(host='0.0.0.0', port=5010)
		
while(True):
	Main()

# userInput = "The current Prime Minister of India is Narendra Modi. He has been in office since 2014 and is serving his third term as Prime Minister."
# Output(userInput)
	
# ~ userInput = "Give me a youtube video link on valorant"
# ~ step 1 find youtube video link of valorant, step 2 run firefox cmd with that link
# ~ Do 1 step at a time. step 1 get 2 youtube video links of valorant game, step 2 draft a mail to my brother ved with these links
# ~ Do 1 step at a time. step 1 find top 3 music artist, step 2 get 2 youtube video links of each artist from the 3 artist, step 3 draft a mail to my brother ved with these links

