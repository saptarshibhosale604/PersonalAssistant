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

## API keys

import os
def RemoveSpaces(input_string):
    # Remove spaces from the input string
    return input_string.replace(" ", "")

openai_key = "sk-proj-zP6XLa1m5gtlBcXJCaHZGmAvXEvUrP 5ATJSPBfLRdEuF-vSroLAG4V0zBdpwPz9PTXe9rM0-CgT3BlbkFJ83 AZyS7Zds5OT4G7S7MJslTok1O8P7ftX6Zz_IvdtMsy_CnjJeBoOv-o-G5t13-1Yw20ei_BwA" # myTestKey08, saptarshibhosale604@gmail.com
tavily_key = "tvly-kX76LCz C36oih0u9COcf6oa 53A47MX0g"

os.environ["OPENAI_API_KEY"] = RemoveSpaces(openai_key)
os.environ["TAVILY_API_KEY"] = RemoveSpaces(tavily_key)

## Library
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langchain_ollama.chat_models import ChatOllama
from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver
from pprint import pprint

## Custom scripts
from Log.custom_logger import logger

## Tools
# import Langchain.Tools.toolsTest as toolsTest
# import Langchain.Tools.toolsGeneral as toolsGeneral
# import Langchain.Tools.toolsPii as toolsPii
# import Langchain.Tools.toolsDataAnalysis as toolsDataAnalysis
# import Langchain.Tools.ToolsFinanceAssist.toolsFinanceAssist as toolsFinanceAssist

import Langchain.Tools.toolsManager as toolsManager

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

llm = ChatOllama(model="llama3.2:1b", max_tokens=500, temperature=0, max_retries=1) # Default
# llm = ChatOpenAI(model="gpt-3.5-turbo", streaming=True, max_tokens=500, temperature=0, max_retries=1) # only for test


modeCurrentLLM = "na" # save mode current llm, for detecting changes in the mode

tools = [] # Default no tools

requestedToolsNumberPerUserInput = 0
requestedToolsNumberPerAgentInterrupt = 0 

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

# Format the AI, Human, Tool message types
def FormatMessageTypes(text):
    total_width = 60
    # total_width = 61
    text_length = len(text)
    padding = (total_width - text_length - 4) // 2
    print("=" * padding + " " + text + " " + "=" * padding)

# Build Langchain agent
def BuildAgent():
    """Create the LangChain agent with OpenAI and our tools, plus HITL middleware."""
    # print("Agent BuildAgent new instance")
    model = llm
    # Require human approval for each tool call
    interrupt_policy = {
        # toolsTest
        "toolTestGetWeather": True,
        "toolTestCalculateExpression": True,
        "toolTestCreatePoem": True,

        # toolsPii
        "toolMyName": True,
        "toolMyPetsName": True,

        # toolsGeneral
        "toolShell": True,
        # "toolShell": False,
        "toolSetCronRemainder": True,
        "toolWebSearch": True,

        #toolsDataAnalysis
        "execute_pyspark_code": True,
        "analyze_csv_data": True,

        #toolsFinanceAssist
        "ToolReadFinanceData": True,
        "ToolWriteFinanceData": True

    }
    middleware = [
        HumanInTheLoopMiddleware(
            interrupt_on=interrupt_policy,
            description_prefix="Tool execution pending approval"
        )
    ]

    # Create the agent with model, tools, and middleware
    agent = create_agent(model=model, tools=tools, middleware=middleware, checkpointer=InMemorySaver())
    return agent

agent = BuildAgent()

# Initialise new agent instance with updated LLM and Tools
def UpdateAgent(modeLLM):
    global llm
    global modeCurrentLLM
    global agent
    global tools
    global logger

    # print(f"Agent UpdateAgent: modeLLM: {modeLLM}, modeCurrentLLM: {modeCurrentLLM}")
    if(modeLLM != modeCurrentLLM):
        # print("Changing the LLM")
        logger.debug(f"Agent UpdateAgent Changing LLM: modeLLM: {modeLLM}, modeCurrentLLM: {modeCurrentLLM}")
        modeCurrentLLM = modeLLM
        # print(f"agent UpdateAgent02: modeLLM: {modeLLM} :: modeCurrentLLM: {modeCurrentLLM}")

        if(modeLLM == "local"):
            llm = ChatOllama(model="llama3.2:1b", streaming=True, max_tokens=500, temperature=0, max_retries=1)
            # llm = ChatOllama(model="llama3.2:1b", temperature=0, verbose=True)
            tools = []

        elif(modeLLM == "local-3b"):
            llm = ChatOllama(model="llama3.2", streaming=True, max_tokens=500, temperature=0, max_retries=1)
            # llm = ChatOllama(model="llama3.2:1b", temperature=0, verbose=True)

        elif(modeLLM == "global"):
            # llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=500, temperature=0, max_retries=1)
            llm = ChatOpenAI(model="gpt-3.5-turbo", streaming=True, max_tokens=500, temperature=0, max_retries=1)
            # tools = toolsGeneral.ToolsList() 
            tools = toolsManager.Main("get") # "get" : Get tools list
            # print(f"toolsManager tools: {tools}")
            # input("Human01")
            # tools = ( toolsGeneral.ToolsList()
            #     + toolsTest.ToolsList() 
            #     + toolsPii.ToolsList() 
            #     # + # toolsDataAnalysis.ToolsList()
            #     + toolsFinanceAssist.ToolsList() )
            # tools = toolsGeneral.ToolsList() +
            #     toolsTest.ToolsList() + 
            #     toolsPii.ToolsList() + 
            #     # toolsDataAnalysis.ToolsList() +
            #     toolsFinanceAssist.ToolsList() 

        elif(modeLLM == "globalGemini"):
            # llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key='AIzaSyBwIrjcMjKA1V3XJ_hCLurJx33wh33NWdk')
            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key='AIzaSyBPH-0Dd5e2Heu8lFs1rCci8ZdGxnr_ZvE')
        
        # rebuild the agent with new llm and tools
        agent = BuildAgent()

# Extracting interrupts, tools to be called, llm streamed chunks from the streamed data
def ExtractStreamContent(stream_mode, content):
    global requestedToolsNumberPerUserInput
    
    # content is related to the chunks generated from llm
    if stream_mode == "messages":
        # Extract AIMessageChunk content safely
        if isinstance(content, tuple) and len(content) >= 1:
            message_chunk = content[0]
            if hasattr(message_chunk, 'content'):
                # print("===============")
                # print(f"message_chunk.content: {message_chunk.content}")
                # Check if the content is an AIMessageChunk or ToolMessage
                # if isinstance(message_chunk, AIMessageChunk):
                #     content_type = "AIMessageChunk"
                # elif isinstance(message_chunk, ToolMessage):
                #     content_type = "ToolMessage"
                # else:
                #     content_type = "Unknown Content Type"
                # Check message type and print accordingly
                if hasattr(message_chunk, 'type'):
                    msg_type = message_chunk.type
                else:
                    # Fallback: check class name
                    msg_type = message_chunk.__class__.__name__
                
                # print(f"msg_type: [{msg_type}] ")
                # if msg_type == 
                if msg_type == "tool":
                    # print("print [toolMessage] ")
                    FormatMessageTypes("ToolMessage")
                    print(f"{message_chunk.content}", end="", flush=True)
                    print()
                    FormatMessageTypes("")
                    print()
                else:
                    print(f"{message_chunk.content}", end="", flush=True)
                # if msg_type == "AIMessageChunk":
                #     print("print [AIMessage] ")
                # if "AIMessageChunk" in msg_type:
                #     print("print02 [AIMessage] ")


                
                # Print the content type and content
                # print(f"{content_type}: {message_chunk.content}")
                # print(f"{message_chunk.content}")
                # print(f"{message_chunk.content}", end="", flush=True)
                # print(token.content_blocks[0]["text"], end="", flush=True)
                # print("===============")
                return message_chunk.content or ""
        
        # Extract metadata if needed
        # commented checking the effect
        # elif isinstance(content, tuple) and len(content) == 2:
        #     message_chunk, metadata = content
        #     if hasattr(message_chunk, 'content'):
        #         # print("===============")
        #         # print(f"message_chunk.content02: {message_chunk.content}")
        #         print(f"{message_chunk.content}", end="|", flush=True)
        #         # print("===============")
        #         return message_chunk.content or ""
        
    # content is related updates like interrupt
    elif stream_mode == "updates":
        # Handle updates format
       # Extract interrupt information
        interrupts = content.get("__interrupt__", [])
        if interrupts:
            # Handle tuple of interrupts (common in LangGraph)
            first_interrupt = interrupts[0] if isinstance(interrupts, tuple) else interrupts[0]
            
            requestedToolsNumberPerUserInput += 1

            global requestedToolsNumberPerAgentInterrupt
            requestedToolsNumberPerAgentInterrupt = len(first_interrupt.value["action_requests"])

            # logger.debug(f"requestedToolsNumberPerAgentInterrupt: {requestedToolsNumberPerAgentInterrupt}")

            for i in range(0, requestedToolsNumberPerAgentInterrupt):
                # Extract action details
                action = first_interrupt.value["action_requests"][i]
                tool_name = action["name"]
                args = action.get("args", action.get("arguments", {}))
                print(f"\n{'-'*60}")
                # print(f"tool_name: {tool_name}, args: {args}")
                logger.info(f"tool_name: {tool_name},\nargs: {args},\nrequestedToolsNumberPerUserInput: {requestedToolsNumberPerUserInput}\nrequestedToolsNumberPerAgentInterrupt: {requestedToolsNumberPerAgentInterrupt}")
                print(f"{'-'*60}")
                input("Is this approved or rejected?(Default: approved): ")
                
    return ""

# Main function
def Main(userInput, threadId, modeLLM):
    UpdateAgent(modeLLM)


    while True:
        # print("Agent Main Entering the while loop ...")

        # memory
        thread_id ="thread-" + str(threadId)
        configMemory = {"configurable": {"thread_id": thread_id}}
        # print(f"configMemory: {configMemory}")
        print(f"thread_id: {thread_id}")

        agentResponsePerUserInput = ""
    
        # Agent.stream handling for local llm
        if "local" in modeLLM:
            FormatMessageTypes("AIMessage")
            # print(f"\n{'='*60}")
            # print
            for stream_mode, chunk in agent.stream(  
                {"messages": [
                    {"role": "system", "content": "You are an assistance like a JARVIS from Iron Man. Your name is RPI. Your master name is SSB"},
                    {"role": "user", "content": userInput}
                ]},
                stream_mode=["updates", "messages"],
                config=configMemory
            ):
                # print(f"stream_mode: {stream_mode}")
                # print(f"content: {chunk}")
                # print("\n")
                chunk_text = ExtractStreamContent(stream_mode, chunk)
                if chunk_text:
                    agentResponsePerUserInput += chunk_text

            # print(f"\n{'='*60}")
            print()
            FormatMessageTypes("")
            print()

            return agentResponsePerUserInput

        # Agent.stream handling for global llm
        elif "global" in modeLLM:

            # print("agent while loop, GLOBAL in the modeLLM")
            agentCallingCountPerUserInput = 0

            while True: 
                global requestedToolsNumberPerUserInput
                agentCallingCountPerUserInput+= 1
                # print(f"while loop starting, agentCallingCountPerUserInput: {agentCallingCountPerUserInput}")

                # First time calling the Agent, and no interrupted tools request pending
                if agentCallingCountPerUserInput == 1 and requestedToolsNumberPerUserInput < 1:
                    FormatMessageTypes("AIMessage")
                    # print(f"\n{'='*60}")
                    # print
                    for stream_mode, chunk in agent.stream(  
                        {"messages": [{"role": "user", "content": userInput}]},
                        # stream_mode="updates, messages",
                        stream_mode=["updates", "messages"],
                        config=configMemory
                    ):
                        # print(f"01 stream_mode: {stream_mode}")
                        # print(f"content: {chunk}")
                        # print("\n")
                        chunk_text = ExtractStreamContent(stream_mode, chunk)
                        if chunk_text:
                            agentResponsePerUserInput += chunk_text

                    # print(f"\n{'='*60}")
                    print()
                    FormatMessageTypes("")
                    print()


                # Not the first time calling the Agent, OR Interrupted tools requests are pending
                elif requestedToolsNumberPerUserInput >= 1:
                    global requestedToolsNumberPerAgentInterrupt
                    requestedToolsNumberPerUserInput -= 1

                    # print(f"\n{'='*60}")
                    FormatMessageTypes("AIMessage")

                    # combine the decisions of all the interrupt requests togather
                    decisions = []
                    for i in range(requestedToolsNumberPerAgentInterrupt):
                        decisions.append({"type": "approve"})

                    requestedToolsNumberPerAgentInterrupt = 0

                    # print(f"decisions: {decisions}")
                    for stream_mode, chunk in agent.stream(  
                        Command(resume={"decisions": decisions}),
                        # Command(resume={"decisions": [{"type": "approve"}]}),
                        stream_mode=["updates", "messages"],
                        config=configMemory
                    ):
                        # print(f"02 stream_mode: {stream_mode}")
                        # print(f"content: {chunk}")
                        # print("\n")
                        chunk_text = ExtractStreamContent(stream_mode, chunk)
                        if chunk_text:
                            agentResponsePerUserInput += chunk_text

                    # print(f"\n{'='*60}")
                    print()
                    FormatMessageTypes("")
                    print()

                else:

                    return agentResponsePerUserInput

                logger.debug(f"agentCallingCountPerUserInput: {agentCallingCountPerUserInput}")
                # print(f"agentCallingCountPerUserInput: {agentCallingCountPerUserInput}, agentResponsePerUserInput: {agentResponsePerUserInput}")
                agentResponsePerUserInput = ""

