## ## INFO ## ##
# llm model: chat gpt
# memory: for each new chat from assistant.py, new memory allocated, no context

## ## IMPORTING ## ## 

from langchain_openai import ChatOpenAI

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

## ## API KEYS ## ## 

def RemoveSpaces(input_string):
    # Remove spaces from the input string
    return input_string.replace(" ", "")

openai_key = "sk-proj-zP6XLa1m5gtlBcXJCaHZGmAvXEvUrP 5ATJSPBfLRdEuF-vSroLAG4V0zBdpwPz9PTXe9rM0-CgT3BlbkFJ83 AZyS7Zds5OT4G7S7MJslTok1O8P7ftX6Zz_IvdtMsy_CnjJeBoOv-o-G5t13-1Yw20ei_BwA" # myTestKey08, saptarshibhosale604@gmail.com
tavily_key = "tvly-kX76LCz C36oih0u9COcf6oa 53A47MX0g"

os.environ["OPENAI_API_KEY"] = RemoveSpaces(openai_key)
os.environ["TAVILY_API_KEY"] = RemoveSpaces(tavily_key)

## ## INITIALIZATION ## ## 

## Initializing llm models
llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=500, temperature=0, max_retries=1)

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


#toolsAdvance =  [toolShell] + toolGmail               	# Need for human in loop
# toolsAdvance =  [toolShell] + toolSQL_DB                	# Need for human in loop
toolsAdvance =  [toolShell]             	# Need for human in loop
toolsIntermediate = [toolSetCronRemainder]
toolsBasic = [toolYoutube, toolWebSearch]                  # No need for human in loop

tools = toolsAdvance + toolsIntermediate + toolsBasic


# ~ tools = toolGmail
# ~ print("## ## tools:", tools)
# ~ humanBreak = input("humanBreak:")

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


## graph and agent
graph = create_react_agent(
	llm, 
	tools, 
	interrupt_before=["tools"], 
	checkpointer=MemorySaver()
) 

## ## SCRIPTS ## ##
def print_stream(graph, inputs, config):
	global agentOutput
	for s in graph.stream(inputs, config, stream_mode="values"):
		message = s["messages"][-1]
		if isinstance(message, tuple):
			print(message)
		
		else:
			message.pretty_print()
			agentOutput = message.content


pathManInTheLoopResponse = "/root/Project/Rpi/PersonalAssistant/Langchain/manInTheLoopResponce.txt"
pathToolsRequired = "/root/Project/Rpi/PersonalAssistant/Langchain/toolsRequired.txt"
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
			print(f"content manInTheLoopResponse file: {content}")
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

def Main(userInput, threadId):
#@app.route('/')
#def Main():
	#return "hey there, this is me"

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

		print("## ## config new:", config)

		if(loopCounter == 0):
			print_stream(graph, inputs, config)
		else:
			print_stream(graph, None, config)
			
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
		
		manInTheLoop = ManInTheLoopResponse(str(toolsRequired))
		# manInTheLoop = input("Do you want to proceed (y/n): ")
		
		if manInTheLoop.lower() == "y":
			print("## Allowed")
			snapshot.next
			inputs = None  # Continue with the next step
		else:
			print("## Denied")	
			return agentOutput
			# break

#if __name__ == '__main__':
#	app.run(host='0.0.0.0', port=5011)

# AgentCall("Give me 1 link of youtube video of linux")

# print("Main return: ", Main("draft a mail about saying hi", 1))
# print("Main return: ", Main("Give me temperature of the cpu of my pc", 1))
