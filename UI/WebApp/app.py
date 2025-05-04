from flask import Flask, render_template, request, jsonify
import time
import Langchain.agent as Agent

app = Flask(__name__)

debug01 = True

print("Initialized assistant.py")

conversationMode = "wakeUp" 	# sleep: Go to Hibernate
	                  	# wakeUp: Goint to answer the user input
inputMode = "text" # text / speech
outputMode = "text" # text / speech

modeContext = "no" # no: no context in conversation
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

def BasicCmds(userInput):
	# global logger
	global conversationMode
	global inputMode
	global outputMode
	global modeContext
	
	if (userInput.lower() == "help"):
		print("1. input mode text")
		print("2. input mode speech")
		print("3. output mode text")
		print("4. output mode speech")
		print("5. wake up")
		print("6. sleep")
		print("7. mode context yes")
		print("8. mode context no")
		print("9. help")
		# logger.debug("## inputMode:", inputMode, ":outputMode:" , outputMode, ":conversationMode:" , conversationMode, "##")
		print("## inputMode:", inputMode, ":outputMode:" , outputMode, ":conversationMode:" , conversationMode, ":modeContext:", modeContext, ":##")
		return True

	# Checking for input mode
	if (userInput.lower() == "input mode text"):
		inputMode = "text"
		return True
	
	elif (userInput.lower() == "input mode speech"):
		inputMode = "speech"
		return True

	# Checking for output mode
	elif (userInput.lower() == "output mode text"):
		outputMode = "text"
		return True
	
	elif (userInput.lower() == "output mode speech"):
		outputMode = "speech"
		return True

	# Checking for wake up call
	elif any(call in userInput.lower() for call in listWakeUpCalls):
		conversationMode = "wakeUp"
		return True
	
	# Checking for sleep call
	elif any(call in userInput.lower() for call in listSleepCalls):
		conversationMode = "sleep"
		return True

	# checking for mode context 
	elif (userInput.lower() == "mode context yes"):
		modeContext = "yes"
		return True

	elif (userInput.lower() == "mode context no"):
		modeContext = "no"
		return True

	else:
		return False

def Processing(userInput):
	# global logger
	global conversationMode
	
	
	if(BasicCmds(userInput)):
		return
		
	
	# for debug only conversation mode only wake up
	# ~ conversationMode = "wakeUp"
	
		
	# ~ # Checking for sleep call
	# ~ if any(call in userInput.lower() for call in listSleepCalls):
		# ~ conversationMode = "sleep"
		
	# if(debug01): print("conversationMode:",conversationMode)
	
	if (conversationMode == "wakeUp"):
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
		
		if(modeContext == "no"):
			threadId += 1 # Always changing memory variable
		
		#agentResponce = "Na"	
		agentResponce = Agent.Main(userInput, threadId)
		#userInput = "who is the PM of India?"
		#agentResponse = requests.get(f"http://agent_langchain:5011/?userInput={userInput}&threadId={threadId}")
		#print(":agentResp:", agentResponce)
		return agentResponce

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/userInputMessage', methods=['POST'])
def get_user_input_message():
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
    time.sleep(3)
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
	global inputMode
		
	# userInput = "Hey there how its going on?" # sample 
	if(inputMode == "text"):
		userInput = input("userInput: ")	# Text 
	elif(inputMode == "speech"):
		userInput = STT.Main()			# Speech To Text
	else:
		print("Error: Invalid inputMode:", inputMode)
	
	# ~ print("userInput:",userInput)	
	logger.info(f"userInput: {userInput}")
	return userInput
	
def Output(assistantOutput):
	global logger
	global outputMode

	logger.info(f"assistantOutput: {assistantOutput}")	# Text 
	
	if(outputMode == "text"):
		return
	elif(outputMode == "speech"):	
		TTS.Main(assistantOutput) 			# Text to speech
	else:
		print("Error: Invalid outputMode:", outputMode)

##	
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5001)
