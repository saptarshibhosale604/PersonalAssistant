# working perfect
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langchain_ollama.chat_models import ChatOllama
from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver
import os


# ============================================================================
# API KEYS 
# ============================================================================

def RemoveSpaces(input_string):
    # Remove spaces from the input string
    return input_string.replace(" ", "")

openai_key = "sk-proj-zP6XLa1m5gtlBcXJCaHZGmAvXEvUrP 5ATJSPBfLRdEuF-vSroLAG4V0zBdpwPz9PTXe9rM0-CgT3BlbkFJ83 AZyS7Zds5OT4G7S7MJslTok1O8P7ftX6Zz_IvdtMsy_CnjJeBoOv-o-G5t13-1Yw20ei_BwA" # myTestKey08, saptarshibhosale604@gmail.com
tavily_key = "tvly-kX76LCz C36oih0u9COcf6oa 53A47MX0g"

os.environ["OPENAI_API_KEY"] = RemoveSpaces(openai_key)
os.environ["TAVILY_API_KEY"] = RemoveSpaces(tavily_key)

# Define tools with @tool decorator (UpperCamelCase names)
@tool("SearchWeb", description="Search the web for information.")
def SearchWeb(query: str) -> str:
    # Placeholder for an actual web search
    return f"Simulated search results for: {query}"

@tool("GetWeather", description="Get weather information for a location.")
def GetWeather(location: str) -> str:
    # Placeholder for a real weather API call
    return f"Simulated weather for {location}: 72°F, Sunny"

@tool("CalculateExpression", description="Calculate an arithmetic expression.")
def CalculateExpression(expression: str) -> str:
    try:
        # Simple evaluation for demo (use with caution on untrusted input)
        result = eval(expression)
    except Exception as e:
        result = f"Error: {e}"
    return str(result)

@tool("CreatePoem", description="Create a poem on the topic given")
def CreatePoem(topic: str) -> str:
    # return f"create a 2 stanza poem on : {topic}"
    return f"create a 2 stanza poem on : {topic}"

llm = ChatOllama(model="llama3.2:1b", max_tokens=500, temperature=0, max_retries=1) # Default

def BuildAgent():
    """Create the LangChain agent with OpenAI and our tools, plus HITL middleware."""
    print("Agent BuildAgent new instance")
    # Initialize the OpenAI chat model (replace "gpt-4" with your model of choice)
    # model = ChatOpenAI(model="gpt-4", temperature=0.1)
    # model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
    # model = ChatOllama(model="llama3.2:1b", streaming=True, max_tokens=500, temperature=0, max_retries=1)
    model = llm
    # tools = [SearchWeb, GetWeather, CalculateExpression]
    # tools = [SearchWeb, GetWeather, CalculateExpression, CreatePoem]
    # tools = []
    # Require human approval for each tool call
    interrupt_policy = {
        "SearchWeb": True,
        "GetWeather": True,
        "CalculateExpression": True,
        "CreatePoem": True
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

from pprint import pprint
# userInput, threadId, GetModeValue("mode-llm"), GetModeValue("mode-context")
# def main():
# def Main(userInput, threadId, modeLLM, modeContextValue):

modeCurrentLLM = "na" # save mode current llm, for detecting changes in the mode

tools = []
# tools = [SearchWeb, GetWeather, CalculateExpression, CreatePoem]
agent = BuildAgent()

def UpdateLLM(modeLLM):
    global llm
    global modeCurrentLLM
    global agent
    global tools
    # global graph
    # llm = model
    #print(f"UpdateLLM: modeLLM: {modeLLM}")
    # print(f"agent UpdateLLM: modeLLM: {modeLLM} :: modeCurrentLLM: {modeCurrentLLM}")

    print(f"Agent UpdateLLM: modeLLM: {modeLLM}, modeCurrentLLM: {modeCurrentLLM}")
    if(modeLLM != modeCurrentLLM):
        print("Changing the LLM")
        modeCurrentLLM = modeLLM
        # print(f"agent UpdateLLM02: modeLLM: {modeLLM} :: modeCurrentLLM: {modeCurrentLLM}")

        if(modeLLM == "local"):
            llm = ChatOllama(model="llama3.2:1b", streaming=True, max_tokens=500, temperature=0, max_retries=1)
            # llm = ChatOllama(model="llama3.2:1b", temperature=0, verbose=True)

        elif(modeLLM == "local-3b"):
            llm = ChatOllama(model="llama3.2", streaming=True, max_tokens=500, temperature=0, max_retries=1)
            # llm = ChatOllama(model="llama3.2:1b", temperature=0, verbose=True)

        elif(modeLLM == "global"):
            # llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=500, temperature=0, max_retries=1)
            llm = ChatOpenAI(model="gpt-3.5-turbo", streaming=True, max_tokens=500, temperature=0, max_retries=1)
            tools = [SearchWeb, GetWeather, CalculateExpression, CreatePoem]
        
        elif(modeLLM == "globalGemini"):
            # llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key='AIzaSyBwIrjcMjKA1V3XJ_hCLurJx33wh33NWdk')
            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key='AIzaSyBPH-0Dd5e2Heu8lFs1rCci8ZdGxnr_ZvE')
        
        agent = BuildAgent()
        # graph = create_react_agent(
        # 	llm, 
        # 	tools, 
        # 	interrupt_before=["tools"], 
        # 	checkpointer=MemorySaver()
        # 	# debug=True
        #           # verbose=True
        # ) 
        # print(f"UpdateLLM llm: {llm}")
# agent = BuildAgent()

def Main(userInput, threadId, modeLLM):
    # global modeContext
    # modeContext = modeContextValue
    UpdateLLM(modeLLM)
    # agent = BuildAgent()
    print("LangChain agent is ready. Type a question (or 'quit' to exit).")
    while True:
        print("Agent Main Entering the while loop ...")
        # userInput = input("\nUser: ")
        if not userInput or userInput.lower() == "quit":
            print("Goodbye!")
            break

        thread_id ="thread-" + str(threadId)
        # memory
        configMemory = {"configurable": {"thread_id": thread_id}}
        print(f"configMemory: {configMemory}")

        # result = agent.invoke({"messages": [{"role": "user", "content": userInput}]},config=configMemory)
        # result = agent.stream({"messages": [{"role": "user", "content": userInput}]},config=configMemory)
        # result = agent.stream({"messages": [{"role": "user", "content": userInput}]},config=configMemory)
        # for token, metadata in agent.stream( {"messages": [{"role": "user", "content": userInput}]},config=configMemory):
        # result = ""

        if "local" in modeLLM:
            print("agent while loop, LOCAL in the modeLLM")

            print("Direct Anwer:")
            # Working piece
            for token, metadata in agent.stream(
                        {"messages": [{"role": "user", "content": userInput}]},
                        stream_mode="messages",
                        config=configMemory
                    ):
                # stream_mode="messages",
                # Each token has content_blocks; we print the text
                # This loops until the final answer is complete
                if token.content_blocks:
                    # result += (token.content_blocks[0]["text"])
                    print(token.content_blocks[0]["text"], end="", flush=True)

            print()
            print()
            break

        elif "global" in modeLLM:

            print("agent while loop, GLOBAL in the modeLLM")
            # work in progress
            # for token, metadata in agent.stream(
            #             {"messages": [{"role": "user", "content": userInput}]},
            #             stream_mode="messages",
            #             config=configMemory
            #         ):
            #     # stream_mode="messages",
            #     # Each token has content_blocks; we print the text
            #     # This loops until the final answer is complete
            #     # if token.content_blocks:
            #     #     # result += (token.content_blocks[0]["text"])
            #     #     print(token.content_blocks[0]["text"], end="", flush=True)
            #     # stream tokens
            #     # what's the weather in PUNE?
            #     if token.content_blocks:
            #         first_block = token.content_blocks[0]
            #         if isinstance(first_block, dict) and "text" in first_block:
            #             print(token.content_blocks[0]["text"], end="", flush=True)
            #
            #     # check for interrupt in this streamed state/event
            #     interrupts = getattr(token, "__interrupt__", None) or metadata.get("__interrupt__")
            #     if interrupts:
            #         print("interrupt detected")  # newline before prompt to human;
            #
            # print("streaming done")
            # input("HumanInterrupt01")
            # break
            # continue

            result = agent.invoke({"messages": [{"role": "user", "content": userInput}]},config=configMemory)
            pprint(f"result before human interrupt: {result}")

            # Only show final answer content, not the full result
            interrupts = result.get("__interrupt__", [])
            if interrupts:
                # There is a tool call awaiting approval
                first_interrupt = interrupts[0]
                action = first_interrupt.value["action_requests"][0]
                tool_name = action["name"]
                args = action.get("args", action.get("arguments", {}))
                print(f"Agent is requesting to call tool '{tool_name}' with args {args}")
                decision = input("Approve this tool call? (approve/reject): ")
                if decision.strip().lower() == "reject":
                    print("Tool call rejected. Aborting this run.")
                    continue
                else:
                    # Approve and resume
                    # resumed = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}))
                    # working, but not streaming
                    # resumed = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)# Same thread ID to resume the paused conversation
                    # answer = resumed["messages"][-1].content

                    # Stream and print the final answer token-by-token
                    print("\nAgent stream Anwer:", end=" ", flush=True)
                    print("\n")
                    # for token, metadata in agent.stream(
                    #     {"messages": [{"role": "user", "content": userInput}]},
                    #     stream_mode="messages"
                    # ):
                    for token, metadata in agent.stream(
                        Command(resume={"decisions": [{"type": "approve"}]}),
                        config=configMemory,
                        stream_mode="messages"
                    ):
                        # Each token has content_blocks; we print the text
                        # This loops until the final answer is complete
                        if token.content_blocks:
                            print(token.content_blocks[0]["text"], end="", flush=True)
                    print()  # new line after answer

            else:
                # No interrupt, just take the agent's answer
                # answer = result["messages"][-1].content
                answer02 = result["messages"][-1].content
                print(f"Direct answer: {answer02}")

            # print(answer02)
            print("END")
            break


# if __name__ == "__main__":
#     main()


