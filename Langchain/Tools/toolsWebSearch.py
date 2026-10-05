from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Initialize search and wikipedia wrappers
_ddg_search = DuckDuckGoSearchRun()
_wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
_wiki_search = WikipediaQueryRun(api_wrapper=_wiki_wrapper)

@tool("toolSearchDuckDuckGo", description="Search the web using DuckDuckGo for up-to-date information, news, and facts.")
def SearchDuckDuckGo(query: str) -> str:
    """Search the web using DuckDuckGo."""
    try:
        return _ddg_search.run(query)
    except Exception as e:
        return f"Error executing DuckDuckGo search: {str(e)}"

@tool("toolSearchWikipedia", description="Search Wikipedia for summaries of encyclopedic knowledge, historical events, people, places, etc.")
def SearchWikipedia(query: str) -> str:
    """Search Wikipedia for encyclopedic information."""
    try:
        return _wiki_search.run(query)
    except Exception as e:
        return f"Error executing Wikipedia search: {str(e)}"

toolsBasic = [SearchDuckDuckGo, SearchWikipedia]
toolsIntermediate = []
toolsAdvance = []

tools = toolsAdvance + toolsIntermediate + toolsBasic

def ToolsList():
    global tools
    return tools
