from langchain.tools import tool

# Define tools with @tool decorator (UpperCamelCase names)
# @tool("toolTestSearchWeb", description="Search the web for information.")
# def SearchWeb(query: str) -> str:
#     # Placeholder for an actual web search
#     return f"Simulated search results for: {query}"

@tool("toolTestGetWeather", description="Get weather information for a location.")
def GetWeather(location: str) -> str:
    # Placeholder for a real weather API call
    return f"Simulated weather for {location}: 72°F, Sunny"

@tool("toolTestCalculateExpression", description="Calculate an arithmetic expression.")
def CalculateExpression(expression: str) -> str:
    try:
        # Simple evaluation for demo (use with caution on untrusted input)
        result = eval(expression)
    except Exception as e:
        result = f"Error: {e}"
    return str(result)

@tool("toolTestCreatePoem", description="Create a poem on the topic given")
def CreatePoem(topic: str) -> str:
    # return f"create a 2 stanza poem on : {topic}"
    return f"create a 2 stanza poem on : {topic}"

# toolsAdvance =  [toolShell]             	# Need for human in loop
toolsAdvance =  []             	# Need for human in loop
# toolsAdvance =  toolPlaywright             	# Need for human in loop
toolsIntermediate = []
# toolsBasic = [toolYoutube, toolWebSearch, toolMyName]                  # No need for human in loop
# toolsBasic = [toolYoutube, toolWebSearch]                  # No need for human in loop
# toolsBasic = [toolWebSearch]                  # No need for human in loop
# toolsBasic = [SearchWeb, GetWeather, CalculateExpression, CreatePoem]
toolsBasic = [GetWeather, CalculateExpression, CreatePoem]

tools = toolsAdvance + toolsIntermediate + toolsBasic

def ToolsList():
    global tools
    return tools
