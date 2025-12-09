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
# from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langchain_ollama.chat_models import ChatOllama
from datetime import datetime
import re
# from langgraph.types import Command
# from langgraph.checkpoint.memory import InMemorySaver
# from pprint import pprint

## Custom scripts
# from Log.custom_logger import logger

## Tools
# import Langchain.Tools.toolsTest as toolsTest
# import Langchain.Tools.toolsGeneral as toolsGeneral
# import Langchain.Tools.toolsPii as toolsPii
# import Langchain.Tools.toolsDataAnalysis as toolsDataAnalysis
# # import Langchain.toolsTravel as toolsTravel



## VARIABLES ##
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#   __     ___    ____  ___    _    ____  _     _____ ____     #
#   \ \   / / \  |  _ \|_ _|  / \  | __ )| |   | ____/ ___|    #
#    \ \ / / _ \ | |_) || |  / _ \ |  _ \| |   |  _| \___ \    #
#     \ V / ___ \|  _ < | | / ___ \| |_) | |___| |___ ___) |   #
#      \_/_/   \_\_| \_\___/_/   \_\____/|_____|_____|____/    #
#                                                              #
#                                                              #
llm = ChatOllama(model="llama3.2:1b", max_tokens=500, temperature=0, max_retries=1) # Default
modeCurrentLLM = "na" # save mode current llm, for detecting changes in the mode

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

def UpdateAgent(modeLLM):
    global llm
    global modeCurrentLLM
    # global agent
    # global tools
    # global logger

    # print(f"Agent UpdateAgent: modeLLM: {modeLLM}, modeCurrentLLM: {modeCurrentLLM}")
    if(modeLLM != modeCurrentLLM):
        # print("Changing the LLM")
        print(f"FabricMananger UpdateAgent Changing LLM: modeLLM: {modeLLM}, modeCurrentLLM: {modeCurrentLLM}")
        modeCurrentLLM = modeLLM
        # print(f"agent UpdateAgent02: modeLLM: {modeLLM} :: modeCurrentLLM: {modeCurrentLLM}")

        if(modeLLM == "local"):
            llm = ChatOllama(model="llama3.2:1b", streaming=True, max_tokens=500, temperature=0, max_retries=1)

        elif(modeLLM == "local-3b"):
            llm = ChatOllama(model="llama3.2", streaming=True, max_tokens=500, temperature=0, max_retries=1)
            # llm = ChatOllama(model="llama3.2:1b", temperature=0, verbose=True)

        elif(modeLLM == "global"):
            llm = ChatOpenAI(model="gpt-3.5-turbo", streaming=True, max_tokens=500, temperature=0, max_retries=1)
        
        elif(modeLLM == "globalGemini"):
            # llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key='AIzaSyBwIrjcMjKA1V3XJ_hCLurJx33wh33NWdk')
            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key='AIzaSyBPH-0Dd5e2Heu8lFs1rCci8ZdGxnr_ZvE')
        
        # rebuild the agent with new llm and tools
        # agent = BuildAgent()

fabricPatternPath = "/root/ProjectRpi/Fabric/Fabric/data/patterns"

def ReadPattern(fabricPatternPath, patternName):
    if os.path.exists(fabricPatternPath):
        patternFilePath = f"{fabricPatternPath}/{patternName}/system.md"
        print(f"patternFilePath: {patternFilePath}")
        # logger.debug("load modes: getting current mode config file")
        with open(patternFilePath, 'r') as f:
            return f.read()
    else:
        print("The userInput File do not exist")

outputDirPath = "/root/ProjectRpi/Fabric/Data"

def WriteOutputToFile(content, outputDirPath, patterName, outputFileTitle):
    try:
        
        timeStamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
        outputFileName = f"{timeStamp}-{patterName}-{outputFileTitle}.md"
        outputFilePath = f"{outputDirPath}/{outputFileName}"

        # print(f"outputFilePath: {outputFilePath}\n ")
        with open(outputFilePath, "w") as f:
            f.write(content)

        print()
        print(f"Output written: {outputFilePath}")
    except Exception as e:
        print(f"Failed to write content to file: {e}")
        return "error"

outputFileTitle = ""

def GenerateOutputFileInitials(output, wordsCount):
    global outputFileTitle

    # print(f"inside GenerateOutputFileInitials  output: {output}")
    # Split the output into words using space as a delimiter
    words = output.split()
    
    # Clean each word: remove special characters, keep only alphanumeric + spaces
    cleaned_words = []
    for word in words[:wordsCount]:
        # Remove special characters, keep letters, numbers, and spaces
        cleaned_word = re.sub(r'[^a-zA-Z0-9\s]', '', word)
        # Remove extra spaces and strip
        cleaned_word = ' '.join(cleaned_word.split())
        if cleaned_word:  # Only add non-empty words
            cleaned_words.append(cleaned_word)
    
    # Get the first N cleaned words and join them with hyphens
    firstCoupleOfWords = '-'.join(cleaned_words[:wordsCount])
    # # Get the first 4 words and join them back together with a space in between
    # firstCoupleOfWords = '-'.join(words[:wordsCount])
    
    # print(f"inside GenerateOutputFileInitials firstCoupleOfWords : {firstCoupleOfWords}")
    outputFileTitle = firstCoupleOfWords;
    # return firstCoupleOfWords

def Main(userInput, modeLLM):
    global llm
    global fabricPatternPath
    global outputDirPath
    global outputFileTitle

    UpdateAgent(modeLLM)

    # for chunk in llm.stream("Why do parrots have colorful feathers?"):
    # conversation = [
    #     {"role": "system", "content": "You are a helpful assistant that translates English to French."},
    #     {"role": "user", "content": "Translate: I love programming."},
    #     {"role": "assistant", "content": "J'adore la programmation."},
    #     {"role": "user", "content": "Translate: I love building applications."}
    # ]
    # if os.path.exists(FabricPatternPath):
    #     print("The path exists")
    # else:
    #     print("The path does not exist")
    #     return "The path does not exist"

    # patternName = "z_test"
    patternName = "youtube_summary"
    

    patternContent = ReadPattern(fabricPatternPath, patternName)

    conversation = [
        {"role": "system", "content": patternContent},
        {"role": "user", "content": userInput}
    ]
    
    print(f"conversation: {conversation}")

    countChunks = 0 #start the count
    output = "" 

    for chunk in llm.stream(conversation):
        # print(chunk.text, end="|", flush=True)
        output += chunk.text
        print(chunk.text, end="", flush=True)
        countChunks += 1
        if (countChunks >= 10):
            GenerateOutputFileInitials(output, 4)

    # print(f"before the writing outputFileTitle: {outputFileTitle}")
    
    WriteOutputToFile(output, outputDirPath, patternName, outputFileTitle)

    outputFileTitle = "" # reset
    return output
    # input("Human01")
