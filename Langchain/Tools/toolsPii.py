from langchain_core.tools import tool

@tool
def toolMyName(userInput :str) -> str:
	'''If input asks "what is my name?"'''
	# userInput = f"user input = '{userInput}'"

	return {"SSB"}

@tool
def toolMyPetsName(userInput :str) -> str:
	'''If input asks "what is my pets name?"'''
	# userInput = f"user input = '{userInput}'"

	return {"RPI"}


# toolsAdvance =  [toolShell]             	# Need for human in loop
# toolsIntermediate = [toolSetCronRemainder]
# toolsBasic = [toolMyName, toolMyPetsName]                  # No need for human in loop
# toolsBasic = [toolMyName]                  # No need for human in loop
toolsBasic = [toolMyName, toolMyPetsName]                  # No need for human in loop

tools = toolsBasic

# ~ humanBreak = input("humanBreak:")

def ToolsList():
    global tools
    return tools