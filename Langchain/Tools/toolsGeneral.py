

## API keys

import os
def RemoveSpaces(input_string):
    # Remove spaces from the input string
    return input_string.replace(" ", "")

openai_key = "sk-proj-zP6XLa1m5gtlBcXJCaHZGmAvXEvUrP 5ATJSPBfLRdEuF-vSroLAG4V0zBdpwPz9PTXe9rM0-CgT3BlbkFJ83 AZyS7Zds5OT4G7S7MJslTok1O8P7ftX6Zz_IvdtMsy_CnjJeBoOv-o-G5t13-1Yw20ei_BwA" # myTestKey08, saptarshibhosale604@gmail.com
tavily_key = "tvly-kX76LCz C36oih0u9COcf6oa 53A47MX0g"

os.environ["OPENAI_API_KEY"] = RemoveSpaces(openai_key)
os.environ["TAVILY_API_KEY"] = RemoveSpaces(tavily_key)

from langchain_community.tools import ShellTool, YouTubeSearchTool
from langchain_community.tools.tavily_search import TavilySearchResults


# from langchain_google_community import GmailToolkit
# from langchain_google_community.gmail.utils import (
#     build_resource_service,
#     get_gmail_credentials,
# )

## ## INITIALIZING TOOLS ## ## 

# toolShell = ShellTool(ask_human_input=False, verbose=True)
# toolShell = ShellTool(ask_human_input=True ) # this is also working fine
toolShell = ShellTool() 
toolShell.description = toolShell.description + f" args {toolShell.args}".replace("{", "{{").replace("}", "}}")
# toolShell.description = f"This tool should only call if the input includes the phrase `my pc`. The tool " + toolShell.description

# ONLY FOR WINDOWS POWERSHELL
toolShell.description = toolShell.description.replace("shell", "PowerShell")
# toolShell.description = f"" + toolShell.description + " Note that multiple cmds should be separated by `;`"

# toolShell.description += """

# Execute a shell command on Windows.

# Rules:
# - Execute exactly one command per tool call.
# - If a task requires multiple commands, call this tool again for each command.
# - Use Windows powershell syntax.
# - Preserve quotes and escaping exactly as needed.
# """

# print(f"toolShell.description: {toolShell.description}")
print(f"toolShell.description: {toolShell.description}")
toolShell.name = "toolShell"

# ~ print("toolShell.description: ", toolShell.description)
# ~ humanBreak = input("humanBreak:")

# the gmail credentials temperary commented
#credentials = get_gmail_credentials(
#    token_file="/home/rpissb/ProjectRpiRpi/Rpi/ChatBot/Langchain/SecretFiles/token.json",
#    scopes=["https://mail.google.com/"],
#    client_secrets_file="/home/rpissb/ProjectRpiRpi/Rpi/ChatBot/Langchain/SecretFiles/credentials.json",
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
# db_url = "sqlite:////root/ProjectRpi/Rpi/PersonalAssistant/Langchain/ToolFinanceAssistant/Data/db_finance.db"

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

mycronFilePath = "/root/ProjectRpi/Rpi/PersonalAssistant/Langchain/ToolCronRemainder/Data/myCronJobs"
updateCronJobsFilePath = "/root/ProjectRpi/Rpi/PersonalAssistant/Langchain/ToolCronRemainder/updateCronJobsFile.sh"

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

# @tool
# def toolMyName(userInput :str) -> str:
# 	'''Returns My Name.'''
# 	userInput = f"user input = '{userInput}'"
#
# 	return {"SSB"}
#

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



# toolYoutube = YouTubeSearchTool()
toolWebSearch = TavilySearchResults(max_results=1)

toolWebSearch.name = "toolWebSearch"
# from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
# from langchain_community.tools.playwright.utils import (
#     create_async_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",	  },
# )
# This import is required only for jupyter notebooks, since they have their own eventloop
# import nest_asyncio
# import asyncio
# nest_asyncio.apply()

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

# for tool in toolShell.get_tools():
# 	print("tool: ", tool)
# 	print("tool.name: ", tool.name)

# print(" \n toolsGeneral: toolShell")
# print(toolShell)
#
# print(" \n toolsGeneral: toolSetCronRemainder")
# print(toolSetCronRemainder)
#
# # print(" \n toolsGeneral: toolYoutube")
# # print(toolYoutube)
#
# print(" \n toolsGeneral: toolWebSearch")
# print(toolWebSearch)
#
# print(" \n toolsGeneral: toolSetCronRemainder")
# print(toolSetCronRemainder)

toolsAdvance =  [toolShell]             	# Need for human in loop
# toolsAdvance =  toolPlaywright             	# Need for human in loop
toolsIntermediate = [toolSetCronRemainder]
# toolsBasic = [toolYoutube, toolWebSearch, toolMyName]                  # No need for human in loop
# toolsBasic = [toolYoutube, toolWebSearch]                  # No need for human in loop
toolsBasic = [toolWebSearch]                  # No need for human in loop

tools = toolsAdvance + toolsIntermediate + toolsBasic
# tools =  toolsAdvance 
# globalTools = tools


# tools 

# ~ tools = toolGmail
# ~ print("## ## tools:", tools)
# ~ humanBreak = input("humanBreak:")

def ToolsList():
    global tools
    return tools
