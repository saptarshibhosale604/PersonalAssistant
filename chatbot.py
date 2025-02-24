import TextToSpeech.textToSpeechOnline02 as TTS
import SpeechToText.speechToTextOnline as STT
import LLM.llm as LLM
import userInputToScriptInvocation as UITSI

debug01 = True

print("Initialized Chatbot")
conversationMode = "sleep" 	# sleep: Go to Hibernate
						# wakeUp: Goint to answer the user input
listWakeUpCalls = ["hey there", "hi there", "hey rpi"]
listSleepCalls = ["sleep now", "go to sleep", "we are done", "got it"]

roleDefining = f"""For the 'User Input' given below
answer as you are a 'JARVIS' from the 'Iron Man' movie
User Input = """

# ~ roleDefining = f"""For the 'User Input' given below
# ~ answer as you are a 'JARVIS' from the 'Iron Man' movie
# ~ User Input = """


# ~ who is the presedent of india


import logging

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def InitializingLogging():
	
	# Create a file handler
	file_handler = logging.FileHandler("Logs/basic.log")
	file_handler.setLevel(logging.DEBUG)

	# Create a console handler
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.DEBUG)

	# Create a formatter and set it for both handlers
	formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
	file_handler.setFormatter(formatter)
	console_handler.setFormatter(formatter)

	# Add the handlers to the logger
	logger.addHandler(file_handler)
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

InitializingLogging()

def Main():
	global conversationMode
	
	
	# Getting user input
	# userInput = "Hey there how its going on?" # sample 
	# ~ userInput = input("userInput: ")	# Text 
	userInput = STT.Main()			# Speech To Text
	
	# ~ print("userInput:",userInput)	
	logger.info(f"userInput: {userInput}")
	
	if (userInput is not None):
		if(debug01): print("userInput Not null")
		
		# for debug only conversation mode only wake up
		# ~ conversationMode = "wakeUp"
		
		# Checking for wake up call
		if any(call in userInput.lower() for call in listWakeUpCalls):
			conversationMode = "wakeUp"
		
		# Checking for sleep call
		elif any(call in userInput.lower() for call in listSleepCalls):
			conversationMode = "sleep"
			
		# ~ # Checking for sleep call
	   	# ~ if any(call in userInput.lower() for call in listSleepCalls):
			# ~ conversationMode = "sleep"
			
		if(debug01): print("conversationMode:",conversationMode)
		
		if (conversationMode == "wakeUp"):
			# userInputToScriptInvocation
			
			# ~ terminalOutput = UITSI.Main(userInput)
			# ~ print(f"TerminalOutput: {terminalOutput}")
			
			# ~ if(terminalOutput is not None):
				# ~ # LLM User Responce generation
			# ~ else:
				# ~ # LLM General Question
			
			
			# define role to userInput
			userInput = roleDefining + userInput			
			logger.info(f"userInputWithDefinedRole: {userInput}")
			
			# Getting responce from LLM model
			llmResponce = LLM.Main(userInput)	
			logger.info(f"llmResponce: {llmResponce}")
						
			# ~ # Text to speech
			TTS.Main(llmResponce)

while(True):
	Main()
	
