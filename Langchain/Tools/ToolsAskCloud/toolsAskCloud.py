from langchain_core.tools import tool
import Langchain.Tools.ToolsAskCloud.ToolAskGPT.toolAskGPT as toolAskGPT

@tool
def AskChatgpt(userInput :str) -> str:
    '''If input asks "Ask ChatGPT" or "Ask GPT"'''
    # userInput = f"user input = '{userInput}'"
    return toolAskGPT.AskChatgpt(userInput)
    # return {"SSB"}


# toolsAdvance =  [toolShell]             	# Need for human in loop
# toolsIntermediate = [toolSetCronRemainder]
# toolsBasic = [toolMyName, toolMyPetsName]                  # No need for human in loop
# toolsBasic = [toolMyName]                  # No need for human in loop
toolsIntermediate = [AskChatgpt]                  # No need for human in loop

tools = toolsIntermediate

# ~ humanBreak = input("humanBreak:")

def ToolsList():
    global tools
    return tools