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

# tools = toolsAdvance + toolsIntermediate + toolsBasic
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
def CustomOllama(userInput):

	# simple one question answer
	response: ChatResponse = chat(model='llama3.2:1b', messages=[
	{
		'role': 'user',
		'content': userInput,
	},
	])
	# print(response['message']['content'])
	# or access fields directly from the response object
	print(f"CustomOllama: {response.message.content}")
	humanBreak = input("humanBreak03:")
	return response.message.content

# from typing import Any, List, Optional, Dict, Union, Iterator
# # from langchain_core.chat_models import BaseChatModel
# from langchain_core.language_models import BaseChatModel
# from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
# from langchain_core.messages import AIMessage, ToolCall
# from langchain_core.outputs import ChatResult, ChatGeneration, GenerationChunk
# # from langchain_core.runnables import CallbackManagerForLLMRun

# # Assume CustomOllama(user_input: str) -> str is defined elsewhere

# class CustomLLM(BaseChatModel):
# 	global globalTools

# 	model_name: str = "CustomChatModel"

# 	tools: Optional[List[Any]] = globalTools  # <-- Add this line

# 	def bind_tools(self, tools: List[Any]) -> "CustomLLM":
# 	# You can store the tools if needed or just ignore them
# 		self.tools = tools
# 		return self

# 	def _generate(
# 		self,
# 		messages: List[BaseMessage],
# 		stop: Optional[List[str]] = None,
# 		run_manager: Optional[Any] = None,
# 		**kwargs: Any
# 	) -> ChatResult:
# 		# Extract the last Human message
# 		user_input = next(
# 			(m.content for m in reversed(messages) if isinstance(m, HumanMessage)), ""
# 		)

# 		print(f"self.tools: {self.tools}")
# 		humanBreak = input("humanBreak01:")
		
# 		# Try to find a matching tool by name in user input
# 		if self.tools:
# 			for tool in self.tools:
# 				if tool.name.lower() in user_input.lower():
# 					args = {}  # You can improve this with actual arg parsing
# 					return ChatResult(
# 						generations=[
# 							ChatGeneration(
# 								message=AIMessage(
# 									content=None,
# 									tool_calls=[ToolCall(name=tool.name, args=args)]
# 								)
# 							)
# 						]
# 					)

# 		# If no tool match, respond normally
# 		response = CustomOllama(user_input)
# 		return ChatResult(
# 			generations=[
# 				ChatGeneration(message=AIMessage(content=response))
# 			]
# 		)

# 	def invoke(
# 		self,
# 		messages: List[BaseMessage],
# 		stop: Optional[List[str]] = None,
# 		run_manager: Optional[CallbackManagerForLLMRun] = None,
# 		**kwargs: Any
# 	) -> ChatResult:
# 		# Get the last human message from the list
# 		last_message = ""
# 		for msg in reversed(messages):
# 			if isinstance(msg, HumanMessage):
# 				last_message = msg.content
# 				break

# 		response_text = CustomOllama(last_message)

# 		return ChatResult(
# 			generations=[
# 				ChatGeneration(message=AIMessage(content=response_text))
# 			]
# 		)

# 	def _llm_type(self) -> str:
# 		return "custom_chat"

# 	@property
# 	def _identifying_params(self) -> Dict[str, Any]:
# 		return {"model_name": self.model_name}

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
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableMap,
    RunnablePassthrough,
)
from langchain_core.language_models import LanguageModelInput

class ChatParrotLink(BaseChatModel):
	"""A custom chat model that echoes the first `parrot_buffer_length` characters
	of the input.

	When contributing an implementation to LangChain, carefully document
	the model including the initialization parameters, include
	an example of how to initialize the model and include any relevant
	links to the underlying models documentation or API.

	Example:

		.. code-block:: python

			model = ChatParrotLink(parrot_buffer_length=2, model="bird-brain-001")
			result = model.invoke([HumanMessage(content="hello")])
			result = model.batch([[HumanMessage(content="hello")],
									[HumanMessage(content="world")]])
	"""
	# global globalTools

	# tools: Optional[List[Any]] = globalTools  # <-- Add this line
	# tools: Optional[List[Any]] = None  # <-- Add this line

	# def bind_tools(self, tools: List[Any]) -> "CustomLLM":
	# # You can store the tools if needed or just ignore them
	# 	# self.tools = tools
	# 	return self
	# def bind_tools(
	# 	self,
	# 	tools: Sequence[Union[dict, Type, Callable, BaseTool]],
	# 	*,
	# 	tool_choice: Union[dict, str, bool, None] = None,
	# 	strict: bool = False,
	# 	**kwargs: Any,
	# ) -> "ChatParrotLink":
	# 	"""
	# 	Bind tool-like objects to this chat model.

	# 	Parameters:
	# 		tools: A list of tool definitions to bind to this chat model.
	# 		tool_choice: Which tool to require the model to call.
	# 		strict: Whether to enforce strict schema validation.
	# 		**kwargs: Additional parameters.

	# 	Returns:
	# 		An instance of ChatParrotLink with tools bound.
	# 	"""
	# 	# Convert tools to OpenAI-compatible tool schemas
	# 	self._tools = [
	# 	    convert_to_openai_tool(tool, strict=strict) for tool in tools
	# 	]
	# 	self._tool_choice = tool_choice
	# 	return self

	model_name: str = Field(alias="model")
	"""The name of the model"""
	parrot_buffer_length: int
	"""The number of characters from the last message of the prompt to be echoed."""
	temperature: Optional[float] = None
	max_tokens: Optional[int] = None
	timeout: Optional[int] = None
	stop: Optional[List[str]] = None
	max_retries: int = 2

	def bind_tools(
		self,
		tools: Sequence[Union[dict[str, Any], type, Callable, BaseTool]],
		*,
		tool_choice: Optional[
			Union[dict, str, Literal["auto", "none", "required", "any"], bool]
		] = None,
		strict: Optional[bool] = None,
		parallel_tool_calls: Optional[bool] = None,
		**kwargs: Any,
	) -> Runnable[LanguageModelInput, BaseMessage]:
		"""Bind tool-like objects to this chat model.

		Assumes model is compatible with OpenAI tool-calling API.

		Args:
			tools: A list of tool definitions to bind to this chat model.
				Supports any tool definition handled by
				:meth:`langchain_core.utils.function_calling.convert_to_openai_tool`.
			tool_choice: Which tool to require the model to call. Options are:

				- str of the form ``"<<tool_name>>"``: calls <<tool_name>> tool.
				- ``"auto"``: automatically selects a tool (including no tool).
				- ``"none"``: does not call a tool.
				- ``"any"`` or ``"required"`` or ``True``: force at least one tool to be called.
				- dict of the form ``{"type": "function", "function": {"name": <<tool_name>>}}``: calls <<tool_name>> tool.
				- ``False`` or ``None``: no effect, default OpenAI behavior.
			strict: If True, model output is guaranteed to exactly match the JSON Schema
				provided in the tool definition. If True, the input schema will be
				validated according to
				https://platform.openai.com/docs/guides/structured-outputs/supported-schemas.
				If False, input schema will not be validated and model output will not
				be validated.
				If None, ``strict`` argument will not be passed to the model.
			parallel_tool_calls: Set to ``False`` to disable parallel tool use.
				Defaults to ``None`` (no specification, which allows parallel tool use).
			kwargs: Any additional parameters are passed directly to
				:meth:`~langchain_openai.chat_models.base.ChatOpenAI.bind`.

		.. versionchanged:: 0.1.21

			Support for ``strict`` argument added.

		"""  # noqa: E501

		if parallel_tool_calls is not None:
			kwargs["parallel_tool_calls"] = parallel_tool_calls
		formatted_tools = [
			convert_to_openai_tool(tool, strict=strict) for tool in tools
		]
		tool_names = []
		for tool in formatted_tools:
			if "function" in tool:
				tool_names.append(tool["function"]["name"])
			elif "name" in tool:
				tool_names.append(tool["name"])
			else:
				pass
		if tool_choice:
			if isinstance(tool_choice, str):
				# tool_choice is a tool/function name
				if tool_choice in tool_names:
					tool_choice = {
						"type": "function",
						"function": {"name": tool_choice},
					}
				elif tool_choice in (
					"file_search",
					"web_search_preview",
					"computer_use_preview",
				):
					tool_choice = {"type": tool_choice}
				# 'any' is not natively supported by OpenAI API.
				# We support 'any' since other models use this instead of 'required'.
				elif tool_choice == "any":
					tool_choice = "required"
				else:
					pass
			elif isinstance(tool_choice, bool):
				tool_choice = "required"
			elif isinstance(tool_choice, dict):
				pass
			else:
				raise ValueError(
					f"Unrecognized tool_choice type. Expected str, bool or dict. "
					f"Received: {tool_choice}"
				)
			kwargs["tool_choice"] = tool_choice
		return super().bind(tools=formatted_tools, **kwargs)


	def _generate(
		self,
		messages: List[BaseMessage],
		stop: Optional[List[str]] = None,
		run_manager: Optional[CallbackManagerForLLMRun] = None,
		**kwargs: Any,
	) -> ChatResult:
		"""Override the _generate method to implement the chat model logic.

		This can be a call to an API, a call to a local model, or any other
		implementation that generates a response to the input prompt.

		Args:
			messages: the prompt composed of a list of messages.
			stop: a list of strings on which the model should stop generating.
					If generation stops due to a stop token, the stop token itself
					SHOULD BE INCLUDED as part of the output. This is not enforced
					across models right now, but it's a good practice to follow since
					it makes it much easier to parse the output of the model
					downstream and understand why generation stopped.
			run_manager: A run manager with callbacks for the LLM.
		"""
		# Replace this with actual logic to generate a response from a list
		# of messages.
		last_message = messages[-1]
		print(f"inside custom llm: messages: {messages}")
		# last_message = messages[0]
		# tokens = last_message.content[: self.parrot_buffer_length]
		tokens = CustomOllama(last_message.content) 
		ct_input_tokens = sum(len(message.content) for message in messages)
		ct_output_tokens = len(tokens)
		message = AIMessage(
			content=tokens,
			additional_kwargs={},  # Used to add additional payload to the message
			response_metadata={  # Use for response metadata
				"time_in_seconds": 3,
				"model_name": self.model_name,
			},
			usage_metadata={
				"input_tokens": ct_input_tokens,
				"output_tokens": ct_output_tokens,
				"total_tokens": ct_input_tokens + ct_output_tokens,
			},
		)
		##
		# If tools are bound, include them in the message
		if hasattr(self, "_tools") and self._tools:
			message.tool_calls = self._tools

		generation = ChatGeneration(message=message)
		return ChatResult(generations=[generation])

	def _stream(
		self,
		messages: List[BaseMessage],
		stop: Optional[List[str]] = None,
		run_manager: Optional[CallbackManagerForLLMRun] = None,
		**kwargs: Any,
	) -> Iterator[ChatGenerationChunk]:
		"""Stream the output of the model.

		This method should be implemented if the model can generate output
		in a streaming fashion. If the model does not support streaming,
		do not implement it. In that case streaming requests will be automatically
		handled by the _generate method.

		Args:
			messages: the prompt composed of a list of messages.
			stop: a list of strings on which the model should stop generating.
					If generation stops due to a stop token, the stop token itself
					SHOULD BE INCLUDED as part of the output. This is not enforced
					across models right now, but it's a good practice to follow since
					it makes it much easier to parse the output of the model
					downstream and understand why generation stopped.
			run_manager: A run manager with callbacks for the LLM.
		"""
		last_message = messages[-1]
		tokens = str(last_message.content[: self.parrot_buffer_length])
		ct_input_tokens = sum(len(message.content) for message in messages)

		for token in tokens:
			usage_metadata = UsageMetadata(
				{
					"input_tokens": ct_input_tokens,
					"output_tokens": 1,
					"total_tokens": ct_input_tokens + 1,
				}
			)
			ct_input_tokens = 0
			chunk = ChatGenerationChunk(
				message=AIMessageChunk(content=token, usage_metadata=usage_metadata)
			)

			if run_manager:
				# This is optional in newer versions of LangChain
				# The on_llm_new_token will be called automatically
				run_manager.on_llm_new_token(token, chunk=chunk)

			yield chunk

		# Let's add some other information (e.g., response metadata)
		chunk = ChatGenerationChunk(
			message=AIMessageChunk(
				content="",
				response_metadata={"time_in_sec": 3, "model_name": self.model_name},
			)
		)
		if run_manager:
			# This is optional in newer versions of LangChain
			# The on_llm_new_token will be called automatically
			run_manager.on_llm_new_token(token, chunk=chunk)
		yield chunk

	@property
	def _llm_type(self) -> str:
		"""Get the type of language model used by this chat model."""
		return "echoing-chat-model-advanced"

	@property
	def _identifying_params(self) -> Dict[str, Any]:
		"""Return a dictionary of identifying parameters.

		This information is used by the LangChain callback system, which
		is used for tracing purposes make it possible to monitor LLMs.
		"""
		return {
			# The model name allows users to specify custom token counting
			# rules in LLM monitoring applications (e.g., in LangSmith users
			# can provide per token pricing for their model and monitor
			# costs for the given LLM.)
			"model_name": self.model_name,
		}

# llm = CustomLLM(n=5)
# llm = CustomLLM(givenTools=tools)
# llmRaw = ChatParrotLink(parrot_buffer_length=3, model="my_custom_model_02")
# llm = llmRaw.bind_tools(tools) # not working as expected
llm = ChatParrotLink(parrot_buffer_length=3, model="my_custom_model_02")

## Open AI LLM model
from langchain_openai import ChatOpenAI

# llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=500, temperature=0, max_retries=1)

# print(f"CustomLLM llm: {llm}::")



from pydantic import BaseModel, Field


class GetWeather(BaseModel):
    '''Get the current weather in a given location'''

    location: str = Field(
        ..., description="The city and state, e.g. San Francisco, CA"
    )


class GetPopulation(BaseModel):
    '''Get the current population in a given location'''

    location: str = Field(
        ..., description="The city and state, e.g. San Francisco, CA"
    )


llm_with_tools = llm.bind_tools(
    [GetWeather, GetPopulation]
    # strict = True  # enforce tool args schema is respected
)

ai_msg = llm_with_tools.invoke(
    "Which city is hotter today and which is bigger: LA or NY?"
)
ai_msg.tool_calls

# print(f"ai_msg: {ai_msg}")
print("#########################")
print(f"ai_msg.tool_calls: {ai_msg.tool_calls}")
print("#########################")
humanBreak = input("humanBreak05:")

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
	checkpointer=MemorySaver(),
	debug=True
	# verbose=True
) 

## ## SCRIPTS ## ##
def print_stream(graph, inputs, config):
	global agentOutput
	humanBreak = input("humanBreak02:")
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
	print(f"## ## Main: userInput: {userInput} threadId: {threadId}")
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

#if __name__ == '__main__':
#	app.run(host='0.0.0.0', port=5011)

# AgentCall("Give me 1 link of youtube video of linux")

# print("Main return: ", Main("draft a mail about saying hi", 1))
# print("Main return: ", Main("Give me temperature of the cpu of my pc", 1))
