"""
README.md
==========

# Personal Assistant Agent (LangChain + Ollama)

A simple command-line personal assistant built using LangChain's agent
framework, powered by a locally running Ollama model ("qwen3.5:4b").

## Features
- Uses a local LLM via Ollama (no API key required)
- Includes 2 custom tools:
    1. GetCurrentTime - returns the current date and time
    2. WordCounter - counts words in a given text
- Includes 2 default LangChain tools:
    1. Wikipedia - fetches summaries from Wikipedia
    2. DuckDuckGo Search - performs web searches
- Simple console-based chat loop (basic UI)

## Requirements
Install dependencies before running:

    pip install langchain langchain-community langchain-ollama wikipedia duckduckgo-search

Make sure Ollama is installed and running locally with the model pulled:

    ollama pull qwen3.5:4b
    ollama serve

## Usage
Run the script:

    python main.py

Then type your queries at the prompt. Type 'exit' or 'quit' to stop.

## Example Queries
- "What time is it right now?"
- "Count the words in this sentence: Hello world this is a test"
- "Search the web for the latest AI news"
- "Tell me about Python programming language from Wikipedia"
"""

import sys
import datetime

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper


def GetCurrentTime(query: str = "") -> str:
    """
    Custom tool function that returns the current date and time.

    Args:
        query (str): Unused input, required for tool signature compatibility.

    Returns:
        str: Current date and time as a formatted string.
    """
    try:
        currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"The current date and time is: {currentTime}"
    except Exception as error:
        return f"Error while getting current time: {error}"


def WordCounter(text: str) -> str:
    """
    Custom tool function that counts the number of words in the given text.

    Args:
        text (str): The input text to count words from.

    Returns:
        str: A message with the word count.
    """
    try:
        wordList = text.strip().split()
        wordCount = len(wordList)
        return f"The text contains {wordCount} word(s)."
    except Exception as error:
        return f"Error while counting words: {error}"


def BuildTools() -> list:
    """
    Builds and returns the list of tools available to the agent.
    Includes 2 custom tools and 2 default LangChain tools.

    Returns:
        list: A list of Tool objects.
    """
    toolsList = []

    try:
        # Custom Tool 1: Get current time
        timeTool = Tool(
            name="GetCurrentTime",
            func=GetCurrentTime,
            description="Useful for getting the current date and time. No input required."
        )
        toolsList.append(timeTool)

        # Custom Tool 2: Word counter
        wordCountTool = Tool(
            name="WordCounter",
            func=WordCounter,
            description="Useful for counting the number of words in a given piece of text. Input should be the text to count."
        )
        toolsList.append(wordCountTool)

        # Default Tool 1: Wikipedia search
        wikipediaWrapper = WikipediaAPIWrapper()
        wikipediaTool = WikipediaQueryRun(api_wrapper=wikipediaWrapper)
        toolsList.append(wikipediaTool)

        # Default Tool 2: DuckDuckGo web search
        searchTool = DuckDuckGoSearchRun()
        toolsList.append(searchTool)

    except Exception as error:
        print(f"Error while building tools: {error}")

    return toolsList


def CreateAgent():
    """
    Creates and returns a LangChain AgentExecutor using a local Ollama LLM,
    a tool-calling agent, and the available tools.

    Returns:
        AgentExecutor: The initialized agent executor, or None if creation fails.
    """
    try:
        # Initialize local Ollama LLM
        llmModel = ChatOllama(model="qwen3.5:4b", temperature=0)

        # Build tools list
        toolsList = BuildTools()

        # Create prompt template required for tool-calling agent
        promptTemplate = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful personal assistant. Use the available tools when needed to answer the user's query accurately."),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the tool-calling agent
        agent = create_tool_calling_agent(
            llm=llmModel,
            tools=toolsList,
            prompt=promptTemplate
        )

        # Wrap agent in an executor to handle running and tool invocation
        agentExecutor = AgentExecutor(
            agent=agent,
            tools=toolsList,
            verbose=True,
            handle_parsing_errors=True
        )

        return agentExecutor

    except Exception as error:
        print(f"Error while creating agent: {error}")
        return None


def RunAssistant():
    """
    Runs the main chat loop for the personal assistant.
    Takes user input from the console, sends it to the agent,
    and prints the response. Handles exit commands and errors.
    """
    print("=" * 50)
    print("Personal Assistant (powered by Ollama + LangChain)")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 50)

    agentExecutor = CreateAgent()

    if agentExecutor is None:
        print("Failed to initialize the agent. Exiting.")
        sys.exit(1)

    while True:
        try:
            userInput = input("\nYou: ").strip()

            if userInput.lower() in ["exit", "quit"]:
                print("Assistant: Goodbye!")
                break

            if not userInput:
                print("Assistant: Please enter a valid query.")
                continue

            response = agentExecutor.invoke({"input": userInput})

            outputText = response.get("output", "No response generated.")
            print(f"Assistant: {outputText}")

        except KeyboardInterrupt:
            print("\nAssistant: Interrupted by user. Goodbye!")
            break

        except Exception as error:
            print(f"Assistant: An error occurred while processing your request: {error}")


if __name__ == "__main__":
    RunAssistant()
