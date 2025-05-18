from flask import Flask, render_template, request, jsonify
import time
import Langchain.agent as Agent

app = Flask(__name__)

debug01 = True

print("Initialized assistant.py")

modeLLM = "global" # local: Model running locally 
			# global: Model running on cloud / chatgpt
modeConversation = "awake" 	# sleep: Go to Hibernate
	                  	# awake: Goint to answer the user input
modeInput = "text" # text / speech
modeOutput = "text" # text / speech
modeContext = "no" # no: no context in conversation

			# yes: the conversation understand the context
	
listWakeUpCalls = ["hey there", "hi there", "hey rpi"]
listSleepCalls = ["sleep now", "go to sleep", "we are done", "got it"]

def UpdateModeLLM(inputData):
	global modeLLM
	if(inputData == "global"):
		modeLLM = "global"
	elif(inputData == "local"):
		modeLLM = "local"
	else:
		print("Error: Invalid inputData:", inputData)
	
	# print(f"modeLLM: {modeLLM}")


roleDefining = f"""For the 'User Input' given below
answer as you are a 'JARVIS' from the 'Iron Man' movie
User Input = """

# ~ roleDefining = f"""For the 'User Input' given below
# ~ answer as you are a 'JARVIS' from the 'Iron Man' movie
# ~ User Input = """


# ~ who is the presedent of india

threadId = 0	# Memory Id for agent graph
mainLoopCnt = 0 # counting looping of Main()

pathManInTheLoopResponse = "/root/Project/Rpi/PersonalAssistant/Langchain/manInTheLoopResponce.txt"
pathToolsRequired = "/root/Project/Rpi/PersonalAssistant/Langchain/toolsRequired.txt"
# Refresh the content in the manInTheLoopResponse.txt file
# def RefreshManInTheLoopResponse():
# 	# Open the file in write mode
# 	with open(pathManInTheLoopResponse, "w") as file:
# 		# Write the new content to the file
# 		file.write("na")

# Reset the content in the toolsRequired.txt file
def ResetToolsRequired():
	with open(pathToolsRequired, "w") as file:
		# Write the new content to the file
		file.write("na")

counter01 = 0

@app.route('/checkToolsRequiredFile', methods=['POST'])
def CheckToolsRequiredFile():
	global counter01

	while counter01 <= 5:
		counter01 += 1
		# Read from the file
		with open(pathToolsRequired, "r") as file:
			content = file.read()
			print(f"content pathToolsRequired file: {content}")
			# Check if the content is "y" or "n"
			if content.lower() != "na":
				# Append bot message
				# //work on this
				ResetToolsRequired()
				# return content
				# return jsonify({"human": "na", "bot": content})		
				return jsonify({"bot": f"{content}\nDo you want to proceed (y/n):"})		
			
		# Wait for a while before checking again
		time.sleep(0.5)  # Check every second (adjust as needed)

	# return "na"
	return jsonify({"bot": "na"})		


# Update the content in the manInTheLoopResponse.txt file
def UpdateManInTheLoopResponse(inputData):
	# Open the file in write mode
	with open(pathManInTheLoopResponse, "w") as file:
		file.write(inputData)

def BasicCmds(userInput):
	# global logger
	global modeConversation
	global modeInput
	global modeOutput
	global modeContext
	global modeLLM
	
	printData = ""
	if (userInput.lower() == "help"):
		# data = "1. input mode text\n"
		# data += "2. input mode speech\n"
		# data += "3. output mode text\n"
		# data += "4. output mode speech\n"
		# data += "5. wake up\n"
		# data += "6. sleep\n"
		# data += "7. mode context yes\n"
		# data += "8. mode context no\n"
		# data += "9. help\n\n"
		
		# printData = "help\n" 
		printData = "mode [options]: current mode\n"
		printData += f"mode input [text/speech]: {modeInput}\n"
		printData += f"mode output [text/speech]: {modeOutput}\n"
		printData += f"mode conversation [awake/sleep]: {modeConversation}\n"
		printData += f"mode context [yes/no]: {modeContext}\n"
		printData += f"mode LLM [local/global]: {modeLLM}\n"
		# logger.debug("## modeInput:", modeInput, ":modeOutput:" , modeOutput, ":modeConversation:" , modeConversation, "##")
		# printData += "CurrentStatus:: modeInput:", modeInput, ":modeOutput:" , modeOutput, ":modeConversation:" , modeConversation, ":modeContext:", modeContext, ":##"
		print(printData)
		return printData

	# Checking for input mode
	if (userInput.lower() == "input mode text"):
		modeInput = "text"
		return True
	
	elif (userInput.lower() == "input mode speech"):
		modeInput = "speech"
		return True

	# Checking for output mode
	elif (userInput.lower() == "output mode text"):
		modeOutput = "text"
		return True
	
	elif (userInput.lower() == "output mode speech"):
		modeOutput = "speech"
		return True

	# Checking for wake up call
	elif any(call in userInput.lower() for call in listWakeUpCalls):
		modeConversation = "awake"
		return True
	
	# Checking for sleep call
	elif any(call in userInput.lower() for call in listSleepCalls):
		modeConversation = "sleep"
		return True

	# checking for mode context 
	elif (userInput.lower() == "mode context yes"):
		modeContext = "yes"
		return True

	elif (userInput.lower() == "mode context no"):
		modeContext = "no"
		return True

	# checking for mode LLM
	elif (userInput.lower() == "mode llm local"):
		modeLLM = "local"
		return True

	elif (userInput.lower() == "mode llm global"):
		modeLLM = "global"
		return True
	
	else:
		return False

	# return printData

def Processing(userInput):
	# global logger
	global modeConversation
	
	
	# if(BasicCmds(userInput)):
	# 	return
		
	
	basicCmdsReturn = BasicCmds(userInput)

	print(f"basicCmdsReturn: {basicCmdsReturn}")

	if(basicCmdsReturn == True): # Return True
		return
	elif(basicCmdsReturn != False): # Return the printData
		return basicCmdsReturn
								# if False then continue

	# for debug only conversation mode only wake up
	# ~ modeConversation = "wakeUp"
	
		
	# ~ # Checking for sleep call
	# ~ if any(call in userInput.lower() for call in listSleepCalls):
		# ~ modeConversation = "sleep"
		
	# if(debug01): print("modeConversation:",modeConversation)
	
	if (modeConversation == "awake"):
		# userInputToScriptInvocation
		
		# ~ terminalOutput = UITSI.Main(userInput)
		# ~ print(f"TerminalOutput: {terminalOutput}")
		
		# ~ if(terminalOutput is not None):
			# ~ # LLM User Responce generation
		# ~ else:
			# ~ # LLM General Question
		
		
		# define role to userInput
		# userInput = roleDefining + userInput			
		# logger.debug(f"userInputWithDefinedRole: {userInput}")
		
		# Getting responce from LLM model
		# llmResponce = LLM.Main(userInput)
		
		#print("agentResponce:")
		global threadId
		global modeLLM
		global modeContext

		if(modeContext == "no"):
			threadId += 1 # Always changing memory variable
		
		# CheckToolsRequiredFile() // make this asyncronic

		#agentResponce = "Na"	
		agentResponce = Agent.Main(userInput, threadId, modeLLM, modeContext)
		
		# agentResponce = Agent.Main(userInput, threadId, modeLLM)
		#userInput = "who is the PM of India?"
		#agentResponse = requests.get(f"http://agent_langchain:5011/?userInput={userInput}&threadId={threadId}")
		#print(":agentResp:", agentResponce)
		return agentResponce

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/userInputMessage', methods=['POST'])
def get_user_input_message():
    ResetToolsRequired()
    user_message = request.json.get("message", "")
    print(f"user_message: {user_message}")
    
    # Simple bot logic – you can replace this with any AI logic
    # time.sleep(3)
    # if "president" in user_message.lower():
    #     bot_reply = "There is no single president of the world, but leaders of individual countries."
    # else:
    #     # bot_reply = f"You said: {user_message}"
    #     bot_reply = "I don't know the answer to that. Can you ask something else?"
    bot_reply = Processing(user_message)

    return jsonify({"human": user_message, "bot": bot_reply})

@app.route('/userInputExtra', methods=['POST'])
def get_user_input_extra():
	user_message = request.json.get("message", "")
	print(f"user_message: {user_message}")
	if(user_message == "y" or user_message == "n"):
		UpdateManInTheLoopResponse(user_message)
	elif(user_message == "global" or user_message == "local"):	
		UpdateModeLLM(user_message)
	# time.sleep(3)
	return "None"

##  not in use
def Main():
	global logger
	global mainLoopCnt
	#return "this is from ui app"
	
	mainLoopCnt += 1
	logger.info(f"mainLoopCnt: {mainLoopCnt}")
	
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


def Input():	
	global logger
	global modeInput
		
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

##	
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5001)
