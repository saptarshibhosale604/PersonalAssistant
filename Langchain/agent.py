## ## INFO ## ##
# llm model: chat gpt
# memory: for each new chat from assistant.py, new memory allocated, no context

## ## IMPORTING ## ## 
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from langchain_community.tools import ShellTool, YouTubeSearchTool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

#from flask import Flask, request
import os
import time

#Vars
pathManInTheLoopResponse = "/root/Project/Rpi/PersonalAssistant/Langchain/manInTheLoopResponce.txt"
pathToolsRequired = "/root/Project/Rpi/PersonalAssistant/Langchain/toolsRequired.txt"


modeUserInterface = "cli" # "web_app" / "cli"

def UpdateModeUserInterface(mode):
	global modeUserInterface
	modeUserInterface = mode
	
## ## API KEYS ## ## 

def RemoveSpaces(input_string):
    # Remove spaces from the input string
    return input_string.replace(" ", "")

openai_key = "sk-proj-zP6XLa1m5gtlBcXJCaHZGmAvXEvUrP 5ATJSPBfLRdEuF-vSroLAG4V0zBdpwPz9PTXe9rM0-CgT3BlbkFJ83 AZyS7Zds5OT4G7S7MJslTok1O8P7ftX6Zz_IvdtMsy_CnjJeBoOv-o-G5t13-1Yw20ei_BwA" # myTestKey08, saptarshibhosale604@gmail.com
tavily_key = "tvly-kX76LCz C36oih0u9COcf6oa 53A47MX0g"

os.environ["OPENAI_API_KEY"] = RemoveSpaces(openai_key)
os.environ["TAVILY_API_KEY"] = RemoveSpaces(tavily_key)

## ## INITIALIZATION ## ## 

## Initializing tools

toolShell = ShellTool(ask_human_input=False, verbose=True)
toolShell.description = toolShell.description + f"args {toolShell.args}".replace("{", "{{").replace("}", "}}")
toolShell.description += f" Note: This tool should only be called if the input explicitly includes the phrase 'my pc'"

# ~ print("toolShell.description: ", toolShell.description)
# ~ humanBreak = input("humanBreak:")

# the gmail credentials temperary commented
#credentials = get_gmail_credentials(
#    token_file="/home/rpissb/ProjectRpi/Rpi/ChatBot/Langchain/SecretFiles/token.json",
#    scopes=["https://mail.google.com/"],
#    client_secrets_file="/home/rpissb/ProjectRpi/Rpi/ChatBot/Langchain/SecretFiles/credentials.json",
#)
#api_resource = build_resource_service(credentials=credentials)
#toolkitGmail = GmailToolkit(api_resource=api_resource)
#toolGmail = [tool for tool in toolkitGmail.get_tools() if tool.name  == "create_gmail_draft"]

# getting tool list from toolkit
# ~ for tool in toolkit.get_tools():
	# ~ print("tool: ", tool)
	# ~ print("tool.name: ", tool.name)
	
## Tool Financial assistant
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool  # or another pool if needed
from langchain_community.utilities.sql_database import SQLDatabase  # adjust based on your module

# Create the engine by providing the correct SQLite URI.
# Notice the four slashes after 'sqlite:' (the fourth one indicates an absolute path).

# Define the database URL
# db_url = "sqlite:////root/Project/Rpi/PersonalAssistant/Langchain/ToolFinanceAssistant/Data/db_finance.db"

# # Create the engine using this URL
# engine = create_engine(db_url, poolclass=NullPool)

# # Create your SQLDatabase instance from the engine.
# db = SQLDatabase(engine)

# #print("db:",db)

# from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

# toolkitSQL_DB = SQLDatabaseToolkit(db=db, llm=llm)


# # getting tool list from toolkit
# #for tool in toolkitSQL_DB.get_tools():
# 	#print("tool: ", tool)
# 	#print("tool.name: ", tool.name)
	
# #available_tools = "sql_db_query", "sql_db_schema", "sql_db_list_tables", "sql_db_query_checker"
# needed_tools = ["sql_db_query", "sql_db_schema", "sql_db_list_tables", "sql_db_query_checker"]
# toolSQL_DB = [tool for tool in toolkitSQL_DB.get_tools() if tool.name in needed_tools]



## Tool Cron job remainder
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
import subprocess

mycronFilePath = "/root/Project/Rpi/PersonalAssistant/Langchain/ToolCronRemainder/Data/myCronJobs"
updateCronJobsFilePath = "/root/Project/Rpi/PersonalAssistant/Langchain/ToolCronRemainder/updateCronJobsFile.sh"

from datetime import datetime

def CopyCronFile():
	# copy local file to root crontab
	try:
	    result = subprocess.run([updateCronJobsFilePath], check=True, text=True, capture_output=True)
	    print("Output:", result.stdout)
	    print("Error:", result.stderr)
	except subprocess.CalledProcessError as e:
	    print("An error occurred while running the script:", e)

def UpdateCronFile(data, filename):
	#update the cron job in local file
	with open(filename, 'a') as file:  # Open the file in append mode
		file.write(str(data) + '\n')  # Write the data followed by a newline

@tool
def toolMyName(userInput :str) -> str:
	'''Returns My Name.'''
	userInput = f"user input = '{userInput}'"

	return {"SSB"}


@tool
def toolSetCronRemainder(userInput :str) -> str:
	'''Expects an input including phrase 'set remainder', 'start remainder'.'''
	userInput = f"user input = '{userInput}'"

	# Get the current date and time
	currentDateTime = datetime.now()

	CREATE_CRONJOB_PROMPT = f'''From the give user input, Returns only CRON JOB output, Do not include any other text.
current date and time: {currentDateTime}
from user input parse the following data:
minute,
hour,
title,
message.
Make cron job with following format:
<minute> <hour> * * * echo "<title> - <message>" >> /var/log/notify.log 2>&1 '''

	messages = [
		SystemMessage(content=CREATE_CRONJOB_PROMPT),
		HumanMessage(content=userInput)
	]

	response = llm.invoke(messages)
	llmResponce = response.content
	
	UpdateCronFile(llmResponce, mycronFilePath)
	CopyCronFile()
	
	return {"Cron job": llmResponce}



toolYoutube = YouTubeSearchTool()
toolWebSearch = TavilySearchResults(max_results=1)

from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import (
    create_async_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",	  },
)
# This import is required only for jupyter notebooks, since they have their own eventloop
import nest_asyncio
import asyncio
nest_asyncio.apply()

# async_browser = create_async_playwright_browser()
# toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
# toolPlaywright = toolkit.get_tools()
# # print(f"toolplaywright:{toolPlaywright}")
# tools_by_name = {tool.name: tool for tool in toolPlaywright} 
# navigate_tool = tools_by_name["navigate_browser"]
# get_elements_tool = tools_by_name["get_elements"]
# # print(f"get_elements_tool: {get_elements_tool}")
# async def Test():
# 	result01 = await navigate_tool.arun(
# 		# {"url": "https://web.archive.org/web/20230428133211/https://cnn.com/world"}
# 		{"url": "https://google.com"}
# 	)
# 	print(f"result01: { result01 }")
# 	# The browser is shared across tools, so the agent can interact in a stateful man

# 	result02 = await get_elements_tool.arun(
# 		{"selector": ".container__headline", "attributes": ["innerText"]}
# 	)
# 	print(f"result02: {result02}")
	
# 	result03 = await tools_by_name["current_webpage"].arun({})
# 	print(f"result03: {result03}")
# 	input("HumanBreak04:")
# asyncio.run(Test())
# #toolsAdvance =  [toolShell] + toolGmail               	# Need for human in loop
# # toolsAdvance =  [toolShell] + toolSQL_DB                	# Need for human in loop
toolsAdvance =  [toolShell]             	# Need for human in loop
# toolsAdvance =  toolPlaywright             	# Need for human in loop
toolsIntermediate = [toolSetCronRemainder]
toolsBasic = [toolYoutube, toolWebSearch, toolMyName]                  # No need for human in loop

# tools = toolsAdvance + toolsIntermediate + toolsBasic
tools =  toolsAdvance 
# globalTools = tools


# tools 

# ~ tools = toolGmail
# ~ print("## ## tools:", tools)
# ~ humanBreak = input("humanBreak:")


## Initializing llm models
## Custom LLM

# from typing import Any, Dict, Iterator, List, Mapping, Optional

# from langchain_core.callbacks.manager import CallbackManagerForLLMRun
# from langchain_core.language_models.llms import LLM
# from langchain_core.outputs import GenerationChunk

from ollama import chat
from ollama import ChatResponse


# print("initialized")
# def CustomOllamaOld(userInput):

# 	# simple one question answer
# 	response: ChatResponse = chat(model='llama3.2:1b', messages=[
# 	{
# 		'role': 'user',
# 		'content': userInput,
# 	},
# 	])
# 	# print(response['message']['content'])
# 	# or access fields directly from the response object
# 	# print(f"CustomOllama: {response.message.content}")
# 	# humanBreak = input("humanBreak03:")
# 	return response.message.content




# Initialize message history
localLLMMessages = []

# print("Welcome to ChatBot! Type 'exit' to quit.\n")
modeContext = 'no'

# V00
def CustomOllama(user_input):
	global localLLMMessages
	global modeContext
    # while True:
	# user_input = input("You: ")

	# if user_input.lower() in ['exit', 'quit']:
	#     print("Goodbye!")
	#     break
	# print("here03")
	# Add user message to history
	localLLMMessages.append({'role': 'user', 'content': user_input})

	# Get response from the model
	stream = chat(
		model='llama3.2:1b',
		messages=localLLMMessages,
		stream=True,
	)

	# Collect response and print it
	response = ""
	print("Streaming responce: ", end='', flush=True)
	for chunk in stream:
		content = chunk['message']['content']
		print(content, end='', flush=True)
		response += content  
		
	print()

	# Add assistant response to history
	if modeContext == 'yes':
		localLLMMessages.append({'role': 'assistant', 'content': response})
	elif modeContext == 'no':
		localLLMMessages = []

	return response

#V01 // working, but not ending
# # def CustomOllamaStream(user_input):
#     global localLLMMessages
#     global modeContext

#     localLLMMessages.append({'role': 'user', 'content': user_input})

#     stream = chat(
#         model='llama3.2:1b',
#         messages=localLLMMessages,
#         stream=True,
#     )

#     full_response = ""
#     print("Streaming response: ", end='', flush=True)

#     for chunk in stream:
#         content = chunk['message']['content']
#         print(content, end='', flush=True)
#         full_response += content
#         yield content  # <-- streaming each chunk

#     print()

#     if modeContext == 'yes':
#         localLLMMessages.append({'role': 'assistant', 'content': full_response})
#     elif modeContext == 'no':
#         localLLMMessages = []

#     # Optionally yield a final marker
#     # yield "[[END]]"

# V02
def CustomOllamaStream(user_input):
	global localLLMMessages
	global modeContext

	localLLMMessages.append({'role': 'user', 'content': user_input})

	stream = chat(
		model='llama3.2:1b',
		messages=localLLMMessages,
		stream=True,
	)

	full_response = ""
	print("Streaming response: ", end='', flush=True)

	for chunk in stream:
		content = chunk['message']['content']
		print(content, end='', flush=True)
		full_response += content
		yield content  # <-- streaming each chunk

	print()

	if modeContext == 'yes':
		localLLMMessages.append({'role': 'assistant', 'content': full_response})
	elif modeContext == 'no':
		localLLMMessages = []

	# Optionally yield a final marker
	yield "[[END]]"


from typing import Any, Dict, Iterator, List, Optional, Literal

from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
)
from langchain_core.messages.ai import UsageMetadata
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field

from typing import Sequence, Union, Callable, Type
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool

#for custom llm class
# llm = CustomLLM(n=5)
# llm = CustomLLM(givenTools=tools)
# llmRaw = ChatParrotLink(parrot_buffer_length=3, model="my_custom_model_02")
# llm = llmRaw.bind_tools(tools) # not working as expected


# llm = ChatParrotLink(parrot_buffer_length=3, model="my_custom_model_02")
from langchain_ollama.chat_models import ChatOllama
# llm = ChatOllama(model="llama3.2:1b", temperature=0, verbose=True)
llm = ChatOllama(model="llama3.2:1b", streaming=True, max_tokens=500, temperature=0, max_retries=1)

## Open AI LLM model
from langchain_openai import ChatOpenAI
# from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
# llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=500, temperature=0, max_retries=1)

# print(f"CustomLLM llm: {llm}::")
modeCurrentLLM = "na" # save mode current llm, for detecting changes in the mode

def UpdateLLM(modeLLM):
	global llm
	global modeCurrentLLM
	# llm = model
	#print(f"UpdateLLM: modeLLM: {modeLLM}")
	# print(f"agent UpdateLLM: modeLLM: {modeLLM} :: modeCurrentLLM: {modeCurrentLLM}")

	if(modeLLM != modeCurrentLLM):
		modeCurrentLLM = modeLLM
		# print(f"agent UpdateLLM02: modeLLM: {modeLLM} :: modeCurrentLLM: {modeCurrentLLM}")

		if(modeLLM == "local"):
			# llm = ChatParrotLink(parrot_buffer_length=3, model="my_custom_model_02")
			llm = ChatOllama(model="llama3.2:1b", streaming=True, max_tokens=500, temperature=0, max_retries=1)
			# llm = ChatOllama(model="llama3.2:1b", temperature=0, verbose=True)
		elif(modeLLM == "global"):
			# llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=500, temperature=0, max_retries=1)
			llm = ChatOpenAI(model="gpt-3.5-turbo", streaming=True, max_tokens=500, temperature=0, max_retries=1)
		
		elif(modeLLM == "globalGemini"):
			# llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key='AIzaSyBwIrjcMjKA1V3XJ_hCLurJx33wh33NWdk')
			llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key='AIzaSyBwIrjcMjKA1V3XJ_hCLurJx33wh33NWdk')
		global graph
		
		graph = create_react_agent(
			llm, 
			tools, 
			interrupt_before=["tools"], 
			checkpointer=MemorySaver()
			# debug=True
		) 
		# print(f"UpdateLLM llm: {llm}")


# from pydantic import BaseModel, Field


# class GetWeather(BaseModel):
#     '''Get the current weather in a given location'''

#     location: str = Field(
#         ..., description="The city and state, e.g. San Francisco, CA"
#     )


# class GetPopulation(BaseModel):
#     '''Get the current population in a given location'''

#     location: str = Field(
#         ..., description="The city and state, e.g. San Francisco, CA"
#     )


# llm_with_tools = llm.bind_tools(
#     [GetWeather, GetPopulation]
#     # strict = True  # enforce tool args schema is respected
# )

# ai_msg = llm_with_tools.invoke(
#     "Which city is hotter today and which is bigger: LA or NY?"
# )
# ai_msg.tool_calls

# # print(f"ai_msg: {ai_msg}")
# print("#########################")
# print(f"ai_msg.tool_calls: {ai_msg.tool_calls}")
# print("#########################")
# humanBreak = input("humanBreak05:")

## memory
# ~ config = {"configurable": {"thread_id": "thread-1"}}
config = {"configurable": {"thread_id": "thread-1"}}

## UserInput
# ~ userInput = "Tell me where is 13_agentBasic.py file in my pc"
# ~ userInput = "step 1: Tell me where is 13_agentBasic.py file and step 2: then find other python files from same folder"
# ~ userInput = "start a timer for 10 sec and after timer over play alarm clock sound to notify"
# ~ userInput = "play blue eyes by honey singh youtube video on the firefox app"
# ~ userInput = "play blue eyes by honey singh youtube video using firefox cmd in background"
# ~ userInput = "play doku punjabi song youtube video using firefox cmd in background"
# ~ userInput = "start the stopwatch in terminal"
# ~ userInput = "start the timer for 5 sec and notify with alarm clock sound"
# userInput = "tell me storage information"
# ~ userInput = "get link for blue eyes by honey singh youtube video and then run the 1st link using only firefox cmd"
# ~ userInput = "play blue eyes by honey singh youtube video"
# ~ userInput = "find the location of lanchain dir and then Give me the list of python files from that langchain directory"
# ~ userInput = "find the location of 'Lanchain' dir"
# userInput = "Give me 1 link of youtube video of linux"

## other
loopCounter = 0
agentOutput = ""



# humanBreak = input("humanBreakLast:")
## graph and agent
graph = create_react_agent(
	llm, 
	tools, 
	interrupt_before=["tools"], 
	checkpointer=MemorySaver()
	# debug=True
) 

## ## SCRIPTS ## ##
# working
def print_stream_normal(graph, inputs, config):
	global agentOutput
	# humanBreak = input("humanBreak02:")
	for s in graph.stream(inputs, config, stream_mode="values"):
		message = s["messages"][-1]
		if isinstance(message, tuple):
			print(message)
		
		else:
			message.pretty_print()
			agentOutput = message.content

#testing
import asyncio

# def print_stream(graph, inputs, config):
async def print_stream_coroutine(graph, inputs, config):
# def print_stream(graph, inputs, config):
	global agentOutput
	#print("inside print_stream_coroutine")
	print("\n============================================")  # final newline
	print("============================================\n")  # final newline
	async for event in graph.astream_events(inputs, config, version="v1"):
	# for event in graph.astream_events(inputs, config, version="v1"):
		if event["event"] == "on_chat_model_stream":
			chunk = event["data"]["chunk"]
			if chunk.content:
				# print(chunk.content, end="|", flush=True)
				print(chunk.content, end="", flush=True)
				agentOutput += chunk.content
				
	# print()  # final newline
	print("\n============================================")  # final newline
	print("============================================\n")  # final newline
	# message = "done"
	# message.pretty_print()
	# humanBreak = input("humanBreak02:")
		# message = s["messages"][stream_events-1]
		# if isinstance(message, tuple):
		# 	print(message)
		
		# else:
		# 	message.pretty_print()
		# 	agentOutput = message.content

# Refresh the content in the manInTheLoopResponse.txt file
def ResetManInTheLoopResponse():
	# Open the file in write mode
	with open(pathManInTheLoopResponse, "w") as file:
		# Write the new content to the file
		file.write("na")

# Update the content in the toolsRequired.txt file
def UpdateToolsRequired(toolsRequired):
	with open(pathToolsRequired, "w") as file:
		# Write the new content to the file
		file.write(toolsRequired)

# Check manInTheLoopResponse.txt file
def ManInTheLoopResponse(toolsRequired):
	UpdateToolsRequired(toolsRequired)
	while True:
		# Read from the file
		with open(pathManInTheLoopResponse, "r") as file:
			content = file.read()
			# print(f"content manInTheLoopResponse file: {content}")
			# Check if the content is "y" or "n"
			if content.lower() == "y":
				print("## Allowed")
				ResetManInTheLoopResponse()
				return "y"
			elif content.lower() == "n":
				print("## Denied")
				ResetManInTheLoopResponse()
				return "n"
			else:
				print("## No response")
			
		# Wait for a while before checking again
		time.sleep(0.5)  # Check every second (adjust as needed)

# Main loop to process the graph

def Main(userInput, threadId, modeLLM, modeContextValue):
#@app.route('/')
#def Main():
	#return "hey there, this is me"
	# print(f"## ## Main: userInput: {userInput} ::threadId: {threadId} :: modeLLM: {modeLLM} :: modeContextValue: {modeContextValue}")
	global modeContext
	modeContext = modeContextValue
	UpdateLLM(modeLLM)

	#userInput = request.args.get('userInput', 'how are you?')
	#threadId = request.args.get('threadId', '1')	
	
	#return "Hello there"

	# ~ RefreshGraph()
	inputs = {"messages": [("user", userInput)]}  # Replace with actual input

	while True:
		global loopCounter
		global agentOutput

		ResetManInTheLoopResponse()
		# Variable to hold the desired thread ID
		new_thread_id ="thread-" + str(threadId)
		#print("Memory: new_thread_id:", new_thread_id)

		# Update the thread_id in the config dictionary
		config["configurable"]["thread_id"] = new_thread_id

		# print("## ## config new:", config)
		#print(f"## ## config new: {config} :: loopCounter: {loopCounter} :: modeLLM: {modeLLM} :: modeContextValue: {modeContextValue}")
		# print(f"before graph stream llm:{llm}")
		
		# if(loopCounter == 0):
		# 	if(modeLLM == 'local'):
		# 	 	print_stream_normal(graph, inputs, config)
		# 	elif(modeLLM == 'global'):
		# 		#print("here01")
		# 		asyncio.run(print_stream_coroutine(graph, inputs, config))
		# else:
		# 	if(modeLLM == 'local'):
		# 		print_stream_normal(graph, None, config)
		# 	elif(modeLLM == 'global'):
		# 		asyncio.run(print_stream_coroutine(graph, None, config))
			
		if(loopCounter == 0):
			# if(modeLLM == 'local'):
			# print_stream_normal(graph, inputs, config)
			# elif(modeLLM == 'global'):
			# 	#print("here01")
			asyncio.run(print_stream_coroutine(graph, inputs, config))
		else:
			# if(modeLLM == 'local'):
			# print_stream_normal(graph, None, config)
			# elif(modeLLM == 'global'):
			asyncio.run(print_stream_coroutine(graph, None, config))
			# await print_stream_coroutine(graph, None, config)
			
		loopCounter += 1
		snapshot = graph.get_state(config)
		
		# Check if the graph has ended
		if not snapshot.next:  # If `snapshot.next` is None or empty, the graph is finished
			print("### Graph has ended.")
			# ~ checkpointer = MemorySaver()
			loopCounter = 0
			return agentOutput
			# break

		# Get the list of called tools
		existing_message = snapshot.values["messages"][-1]
		toolsRequired = existing_message.tool_calls

		print("####### Tools to be called ::: ", toolsRequired)
		
		global modeUserInterface
		
		if(modeUserInterface == "web_app"):
			manInTheLoop = ManInTheLoopResponse(str(toolsRequired))
		elif(modeUserInterface == "cli"):
			manInTheLoop = input("Do you want to proceed (y/n): ")
		
		if manInTheLoop.lower() == "y":
			print("## Allowed")
			snapshot.next
			inputs = None  # Continue with the next step
		else:
			print("## Denied")	
			return agentOutput
			# break

# Global dictionary to hold the response
# globalState = {
#     "manInTheLoopResponse": None
# }

# Get the content in the manInTheLoopResponse.txt file
def UpdateManInTheLoopResponse(inputData):
	# Open the file in write mode
	with open(pathManInTheLoopResponse, "w") as file:
		file.write(inputData)

def GetManInTheLoopResponse():
	with open(pathManInTheLoopResponse, "r") as file:
		content = file.read()
		# print(f"content manInTheLoopResponse file: {content}")
		return content

def HandleGraphWithManInTheLoop(user_input, thread_id, config):
	# print("agent HandleGraphWithManInTheLoop:: user_input:", user_input, ":: thread_id:", thread_id)
	global loopCounter, agentOutput, modeUserInterface
	agentOutput = ""

	inputs = {"messages": [("user", user_input)]}
	new_thread_id = "thread-" + str(thread_id)
	config["configurable"]["thread_id"] = new_thread_id

	while True:
		ResetManInTheLoopResponse()
		# print(f"agent HandleGraphWithManInTheLoop while loop")

		if loopCounter == 0:
			stream = graph.stream(inputs, config, stream_mode="values")
		else:
			stream = graph.stream(None, config, stream_mode="values")

		for s in stream:
			message = s["messages"][-1]
			if not isinstance(message, tuple):
				agentOutput = message.content
				yield agentOutput

		loopCounter += 1
		snapshot = graph.get_state(config)

		if not snapshot.next:
			loopCounter = 0
			return

		toolsRequired = snapshot.values["messages"][-1].tool_calls
		print("####### Tools to be called ::: ", toolsRequired)

		modeUserInterface = "web_app"  # or "cli", set this based on your application context
		
		if modeUserInterface == "web_app":
			# manInTheLoop = ManInTheLoopResponse(str(toolsRequired))
			# Send a special signal to frontend
			yield f"[[CONFIRM:{toolsRequired}]]"

			# Wait for confirmation to appear in a global or shared state
			while True:
				decision = GetManInTheLoopResponse()
				# print(f"agent HandleGraphWithManInThe waiting in the loop:: GetManInTheLoopResponse(): {GetManInTheLoopResponse()}")
				# print(f"agent HandleGraphWithManInThe waiting in the loop:: decision: {decision}")
				if(decision != "na"):
					# decision = globalState["manInTheLoopResponse"]
					# globalState["manInTheLoopResponse"] = None  # reset
					# print("agent HandleGraphWithManInTheLoop: decision:", decision)
					UpdateManInTheLoopResponse("na")  # reset the file
					break
				time.sleep(2)

			if(decision.lower() == "y"):
				# print("agent HandleGraphWithManInTheLoop: User chose to proceed.")
				inputs = None  # Continue
			else:
				# print("agent HandleGraphWithManInTheLoop: User chose NOT to proceed.")
				return

		elif modeUserInterface == "cli":
			manInTheLoop = input("Do you want to proceed (y/n): ")

			if manInTheLoop.lower() == "y":
				inputs = None  # Continue
			else:
				return
#V01
# def StreamingResponse(user_input, threadId, modeLLM, modeContextValue):
#     global modeContext
#     modeContext = modeContextValue
#     UpdateLLM(modeLLM)

#     inputs = {"messages": [("user", user_input)]}
#     global loopCounter
#     global agentOutput

#     ResetManInTheLoopResponse()
#     new_thread_id = "thread-" + str(threadId)
#     config["configurable"]["thread_id"] = new_thread_id

#     if modeLLM == 'local':
#         stream = graph.stream(inputs, config, stream_mode="values")
#     else:
#         stream = asyncio.run(graph.astream(inputs, config, stream_mode="values"))

#     for s in stream:
#         message = s["messages"][-1]
#         if isinstance(message, tuple):
#             yield str(message)
#         else:
#             content = message.content
#             agentOutput = content
#             yield content  # <-- This sends each chunk

#         snapshot = graph.get_state(config)
#         if not snapshot.next:
#             loopCounter = 0
#             break

# V02
# def StreamingResponse(user_input, threadIdValue, modeLLMValue, modeContextValue):
# 	global modeContext
# 	# global modeLLM
# 	modeContext = modeContextValue
# 	modeLLM = modeLLMValue
# 	print(f"agent StreamingResponse: user_input: {user_input} :: threadIdValue: {threadIdValue} :: modeLLMValue: {modeLLMValue} :: modeContextValue: {modeContextValue}")
# 	threadId = threadIdValue
# 	UpdateLLM(modeLLMValue)
# 	print(f"agent StreamingResponse02: modeLLM: {modeLLM} :: modeContext: {modeContext}")

# 	global loopCounter
# 	global agentOutput

# 	ResetManInTheLoopResponse()
# 	new_thread_id = "thread-" + str(threadId)
# 	config["configurable"]["thread_id"] = new_thread_id

# 	print(f"agent here02:: modeLLM: {modeLLM}")
# 	# If you're using your own custom Ollama stream:
# 	if modeLLM == "local":
# 		for chunk in CustomOllamaStream(user_input):
# 			agentOutput = chunk
# 			yield chunk

# 	else:
# 		# fallback: stream from langgraph graph
# 		print("agent stream from langgraph graph::")
# 		inputs = {"messages": [("user", user_input)]}
# 		stream = graph.stream(inputs, config, stream_mode="values")
# 		for s in stream:
# 			message = s["messages"][-1]
# 			if not isinstance(message, tuple):
# 				agentOutput = message.content
# 				print(agentOutput)
# 				yield message.content

# V04
def StreamingResponse(user_input, threadIdValue, modeLLMValue, modeContextValue):
	global modeContext
	# global modeLLM
	modeContext = modeContextValue
	modeLLM = modeLLMValue
	# print(f"agent StreamingResponse: user_input: {user_input} :: threadIdValue: {threadIdValue} :: modeLLMValue: {modeLLMValue} :: modeContextValue: {modeContextValue}")
	threadId = threadIdValue
	UpdateLLM(modeLLMValue)
	# print(f"agent StreamingResponse02: modeLLM: {modeLLM} :: modeContext: {modeContext}")

	global loopCounter
	global agentOutput

	ResetManInTheLoopResponse()
	new_thread_id = "thread-" + str(threadId)
	config["configurable"]["thread_id"] = new_thread_id

	# print(f"agent here02:: modeLLM: {modeLLM}")
	# If you're using your own custom Ollama stream:
	if modeLLM == "local":
		for chunk in CustomOllamaStream(user_input):
			agentOutput = chunk
			yield chunk

	else:
		# print("agent stream from langgraph graph with man-in-the-loop::")
		print("=====================================================")
		for chunk in HandleGraphWithManInTheLoop(user_input, threadId, config):
			print(chunk)
			yield chunk
		print("=====================================================")
	

#if __name__ == '__main__':
#	app.run(host='0.0.0.0', port=5011)

# AgentCall("Give me 1 link of youtube video of linux")

# print("Main return: ", Main("draft a mail about saying hi", 1))
# print("Main return: ", Main("Give me temperature of the cpu of my pc", 1))
