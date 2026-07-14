"""
Tools Manager Module

This module provides functionality to manage LangChain tools with dynamic selection
and persistent configuration. It allows users to selectively enable/disable tools
and retrieve the appropriate tool list based on saved preferences.

Uses functional programming paradigm with module-level state management.

Author: Data Engineer
Created: December 2025
"""

import json
import os
from typing import List, Any, Dict
import sys

from Log.log_utils import PrintFunctionName

# Module-level configuration
# CONFIG_FILE = "tools_cson"
# CONFIG_FILE = "/root/ProjectRpi/Rpi/PersonalAssistant/Langchain/Tools/toolsConfig.json"
CONFIG_FILE = "./Langchain/Tools/toolsConfig.json"

# Tool module mapping
TOOLS_MODULES = {
    "toolsGeneral": "Langchain.Tools.toolsGeneral",
    "toolsAskCloud": "Langchain.Tools.ToolsAskCloud.toolsAskCloud",
    "toolsTest": "Langchain.Tools.toolsTest",
    "toolsPii": "Langchain.Tools.toolsPii",
    "toolsDataAnalysis": "Langchain.Tools.toolsDataAnalysis",
    "toolsFinanceAssist": "Langchain.Tools.ToolsFinanceAssist.toolsFinanceAssist",
    "toolsProjectBuilder": "Langchain.Tools.ToolsProjectBuilder.toolsProjectBuilder",
}

# Default configuration
DEFAULT_CONFIG = {
    "toolsGeneral": True,
    "toolsTest": True,
    "toolsPii": True,
    "toolsDataAnalysis": False,  # Commented out by default
    "toolsFinanceAssist": True
}

# Global state for tools configuration
toolsConfig: Dict[str, bool] = {}


@PrintFunctionName
def LoadToolsConfig() -> None:
    """
    Load tools configuration from file or use defaults.

    Attempts to load configuration from CONFIG_FILE. If file doesn't exist,
    creates it with default settings. Updates the global toolsConfig variable.

    Raises:
        IOError: If unable to read/write configuration file

    Side Effects:
        Modifies global toolsConfig dictionary
    """
    global toolsConfig

    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as configFile:
                toolsConfig = json.load(configFile)
            print(f"✓ Tools configuration loaded from {CONFIG_FILE}")
        else:
            toolsConfig = DEFAULT_CONFIG.copy()
            SaveToolsConfig()
            print(f"✓ Created default configuration file: {CONFIG_FILE}")
    except (IOError, json.JSONDecodeError) as error:
        print(f"✗ Error loading configuration: {str(error)}")
        print("  Using default configuration...")
        toolsConfig = DEFAULT_CONFIG.copy()


@PrintFunctionName
def SaveToolsConfig() -> None:
    """
    Save current tools configuration to file.

    Writes the global toolsConfig dictionary to CONFIG_FILE in JSON format
    with proper formatting for readability.

    Raises:
        IOError: If unable to write configuration file

    Side Effects:
        Creates/overwrites CONFIG_FILE with current toolsConfig state
    """
    try:
        with open(CONFIG_FILE, 'w') as configFile:
            json.dump(toolsConfig, configFile, indent=4)
        print(f"✓ Tools configuration saved to {CONFIG_FILE}")
    except IOError as error:
        print(f"✗ Error saving configuration: {str(error)}")


import contextlib
from typing import Any

@PrintFunctionName
def ImportModule02(modulePath: str) -> Any:
    """
    Dynamically import a Python module by path with warnings suppressed.
    """
    try:
        # Suppress all warnings for this block (including deprecation warnings)
        with contextlib.suppress(UserWarning, DeprecationWarning): 
            parts = modulePath.split('.')
            
            if len(parts) > 1:
                # Navigate through nested modules
                current_module = __import__(parts[0])
                for part in parts[1:]:
                    try:
                        current_module = getattr(current_module, part)
                    except AttributeError as e:
                        raise ImportError(f"Cannot import {modulePath}: Attribute '{part}' not found") from e
            
            return current_module

    except (ImportError, AttributeError) as error:
        # Only print the actual error message here
        raise ImportError(f"Cannot import {modulePath}: {str(error)}")

def ImportModule(modulePath: str) -> Any:
    """
    Dynamically import a Python module by path.

    Args:
        modulePath (str): Full module path (e.g., 'Langchain.Tools.toolsGeneral')

    Returns:
        Any: The imported module object

    Raises:
        ImportError: If module cannot be imported

    Example:
        >>> module = ImportModule('Langchain.Tools.toolsGeneral')
        >>> tools = module.ToolsList()
    """
    try:
        parts = modulePath.split('.')
        module = __import__(modulePath)

        # Navigate through nested modules
        for part in parts[1:]:
            module = getattr(module, part)

        return module
    except (ImportError, AttributeError) as error:
        raise ImportError(f"Cannot import {modulePath}: {str(error)}")


@PrintFunctionName
def GetToolsList() -> List[Any]:
    """
    Retrieve filtered list of tools based on current configuration.

    Dynamically imports enabled tool modules and calls their ToolsList()
    method, concatenating results based on saved preferences stored in
    the global toolsConfig dictionary.

    Returns:
        List[Any]: Combined list of tools from enabled modules.
                  Empty list if no tools are enabled or import fails.

    Example:
        >>> tools = GetToolsList()
        >>> print(f"Loaded {len(tools)} tools")

    Side Effects:
        Prints status messages for each tool module processed
    """
    combinedToolsList: List[Any] = []

    try:
        toolTypeCounter = 0
        for toolName, modulePath in TOOLS_MODULES.items():
            toolTypeCounter += 1
            # Check if tool is enabled in configuration
            if toolsConfig.get(toolName, False):
                try:
                    # Dynamically import the module
                    module = ImportModule(modulePath)

                    # Call ToolsList() function from the module
                    if hasattr(module, 'ToolsList'):
                        toolsList = module.ToolsList()
                        # print("### finding the list here")
                        # print(f"toolsList: {toolsList}")
                        for toolsCounter, tool in enumerate(toolsList):
                            # print(f"{i+1}. toolsList: {tool.name}: {tool.description[:10]}")

                            print(f"    {toolTypeCounter}.{toolsCounter+1}. {tool.name}: {tool.description[:30]}")
                        combinedToolsList.extend(toolsList)
                        # print(f"combinedToolsList: {combinedToolsList}")
                        # for i, tool in enumerate(combinedToolsList):
                        #     print(f"{i+1}. combinedToolsList: {tool.name}: {tool.description[:10]}")
                        print(f"{toolTypeCounter} ✓ Loaded {toolName}: {len(toolsList)} tools")
                    else:
                        print(f"{toolTypeCounter} ⚠ Warning: {toolName} has no ToolsList() function")

                except ImportError as importError:
                    print(f"{toolTypeCounter} ⚠ Warning: Could not import {toolName}: {str(importError)}")
                    print(f"  Module path: {modulePath}")

                except Exception as error:
                    print(f"{toolTypeCounter} ⚠ Warning: Error loading {toolName}: {str(error)}")
            else:
                print(f"{toolTypeCounter} ⊘ Skipped {toolName} (disabled)")

    except Exception as error:
        print(f"✗ Error retrieving tools list: {str(error)}")
        return []

    print(f"\n✓ Total tools loaded: {len(combinedToolsList)}")
    return combinedToolsList


@PrintFunctionName
def SelectToolManger() -> str:
    """
    Display the tool-selection Manger screen (step 1 of the update workflow).

    Lists every configured tool with its current Enabled/Disabled status
    and prompts the user to pick one by number.

    Returns:
        str: The selected tool name, or "" if the selection was invalid.
    """
    toolNames = list(TOOLS_MODULES.keys())

    print("toolsManger: select the tool:")
    for index, toolName in enumerate(toolNames, start=1):
        status = "Enabled" if toolsConfig.get(toolName, False) else "Disabled"
        print(f"{index}. {toolName:<20} [{status}]")

    selection = input("Human:\n").strip()

    try:
        if selection == "q":
            return "quit"
        selectedIndex = int(selection) - 1
        if selectedIndex < 0 or selectedIndex >= len(toolNames):
            raise IndexError
        return toolNames[selectedIndex]
    except (ValueError, IndexError):
        print("⚠ Invalid tool selection.")
        return ""


@PrintFunctionName
def ToggleToolManger(toolName: str) -> bool:
    """
    Display the enable/disable Manger screen for a single tool (step 2 of the
    update workflow), save the new preference, and report the result.

    Args:
        toolName (str): The tool whose status is being changed.

    Returns:
        bool: True if the value was saved successfully, False otherwise.
    """
    global toolsConfig

    print(f"toolsManger: {toolName}")
    print("0 Disable")
    print("1 Enable")
    # print("0 Enable                llm streaming mode off")
    # print("1 Disable                 llm streaming mode on")

    choice = input("Human:\n").strip()

    if choice == "0":
        newStatus = False
    elif choice == "1":
        newStatus = True
    else:
        print("⚠ Invalid input. No changes made.")
        return False

    toolsConfig[toolName] = newStatus
    SaveToolsConfig()

    print("toolsManger:")
    print("The value saved succesfully")
    print(f"mode-stream: {str(newStatus).lower()}")

    return True


@PrintFunctionName
def Main(inputChoice="none") -> List[Any]:
    """
    Main entry point for the Tools Manager.

    Behavior:
        - inputChoice == "update": walks the user through the two-step
          toolsManger flow (pick a tool, then enable/disable it), saves the
          preference, and returns the refreshed tools list.
        - inputChoice == "get": simply returns the tools list built from
          the currently saved preferences.
        - anything else: reports an invalid choice and returns an empty list.

    Returns:
        List[Any]: The tools list appropriate for the enabled preferences.

    Side Effects:
        Loads configuration on startup; may update/save configuration;
        prints interactive prompts and status messages.
    """
    try:
        # Initialize by loading configuration
        LoadToolsConfig()

        if inputChoice == "update":
            while True:
                selectedTool = SelectToolManger()
                print(f"selectedTool: {selectedTool}")
                if selectedTool == "quit":
                    return GetToolsList()
                # if not selectedTool:
                #     return GetToolsList()

                ToggleToolManger(selectedTool)
                # return GetToolsList()

        elif inputChoice == "get":
            return GetToolsList()

        else:
            print("⚠ Invalid tools choice option.")
            return []

    except KeyboardInterrupt:
        print("\n\n✗ Program interrupted by user")
        sys.exit(1)
    except Exception as error:
        print(f"\n✗ Unexpected error in main: {str(error)}")
        sys.exit(1)


# if __name__ == "__main__":
#     Main("update")