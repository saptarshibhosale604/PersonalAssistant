import sys
import os

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Langchain.Tools.toolsManager import LoadToolsConfig, GetToolsList

def test_project_context_tool():
    print("=== Testing toolsProjectContextManager ===")
    LoadToolsConfig()
    tools = GetToolsList()
    print(f"Enabled tools count: {len(tools)}")
    
    found = False
    for tool in tools:
        if tool.name == "ReadProjectContext":
            found = True
            print(f"Found tool: {tool.name} - {tool.description}")
            result = tool.invoke({})
            print(f"\n--- Result Preview (first 300 chars) ---\n{result[:300]}...\n----------------------------------------")
            break
            
    assert found, "ReadProjectContext tool not found in enabled tools!"
    print("Test passed successfully!")

if __name__ == "__main__":
    test_project_context_tool()
