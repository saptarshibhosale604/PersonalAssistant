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


# Module-level configuration
# CONFIG_FILE = "tools_cson"
# CONFIG_FILE = "/root/ProjectRpi/Rpi/PersonalAssistant/Langchain/Tools/toolsConfig.json"
CONFIG_FILE = "./Langchain/Tools/toolsConfig.json"

# Tool module mapping
TOOLS_MODULES = {
    "toolsGeneral": "Langchain.Tools.toolsGeneral",
    "toolsTest": "Langchain.Tools.toolsTest",
    "toolsPii": "Langchain.Tools.toolsPii",
    "toolsDataAnalysis": "Langchain.Tools.toolsDataAnalysis",
    "toolsFinanceAssist": "Langchain.Tools.ToolsFinanceAssist.toolsFinanceAssist"
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
        for toolName, modulePath in TOOLS_MODULES.items():
            # Check if tool is enabled in configuration
            if toolsConfig.get(toolName, False):
                try:
                    # Dynamically import the module
                    module = ImportModule(modulePath)
                    
                    # Call ToolsList() function from the module
                    if hasattr(module, 'ToolsList'):
                        toolsList = module.ToolsList()
                        combinedToolsList.extend(toolsList)
                        print(f"✓ Loaded {toolName}: {len(toolsList)} tools")
                    else:
                        print(f"⚠ Warning: {toolName} has no ToolsList() function")
                
                except ImportError as importError:
                    print(f"⚠ Warning: Could not import {toolName}: {str(importError)}")
                    print(f"  Module path: {modulePath}")
                
                except Exception as error:
                    print(f"⚠ Warning: Error loading {toolName}: {str(error)}")
            else:
                print(f"⊘ Skipped {toolName} (disabled)")
    
    except Exception as error:
        print(f"✗ Error retrieving tools list: {str(error)}")
        return []
    
    print(f"\n✓ Total tools loaded: {len(combinedToolsList)}")
    return combinedToolsList


def updateToolsReturnValue() -> str:
    """
    Interactive CLI for managing tool selection preferences.
    
    Displays all available tools and prompts user to enable/disable each one.
    Saves preferences to configuration file after user completes selection.
    Updates the global toolsConfig dictionary with user choices.
    
    Returns:
        str: "okay" on successful completion, "error" on failure.
    
    User Interaction:
        - Displays current status of each tool
        - Prompts for yes/no response for each tool
        - Accepts: 'y', 'yes', 'n', 'no' (case-insensitive)
        - Invalid input defaults to current status with warning
    
    Example:
        >>> result = updateToolsReturnValue()
        >>> if result == "okay":
        ...     print("Configuration updated successfully")
    
    Side Effects:
        Modifies global toolsConfig and saves to CONFIG_FILE
        Prints interactive prompts and status messages
    """
    global toolsConfig
    
    try:
        print("\n" + "="*60)
        print("TOOLS CONFIGURATION MANAGER")
        print("="*60)
        print("\nUpdate tool return status (y/n for each tool):\n")
        
        userPreferences: Dict[str, bool] = {}
        
        # input("TODO A default selection current status")

        # Iterate through each tool and ask user
        for toolName in TOOLS_MODULES.keys():
            currentStatus = toolsConfig.get(toolName, False)
            statusText = "enabled" if currentStatus else "disabled"
            
            while True:
                try:
                    userInput = input(
                        f"Include {toolName}? ({statusText}) [y/n]: "
                    ).strip().lower()
                    
                    if userInput in ['y', 'yes']:
                        userPreferences[toolName] = True
                        print(f"  → {toolName} set to: enabled ✓")
                        break
                    elif userInput in ['n', 'no']:
                        userPreferences[toolName] = False
                        print(f"  → {toolName} set to: disabled ✗")
                        break
                    else:
                        userPreferences[toolName] = currentStatus
                        print(f"  → {toolName} no change")
                        break
                        # print(f"  ⚠ Invalid input. Please enter 'y' or 'n'")
                
                except KeyboardInterrupt:
                    print("\n⚠ Configuration update cancelled by user")
                    return "error"
                except Exception as error:
                    print(f"  ✗ Error processing input: {str(error)}")
                    userPreferences[toolName] = currentStatus
                    break
        
        # Update global configuration with user preferences
        toolsConfig = userPreferences
        SaveToolsConfig()
        
        print("\n" + "="*60)
        print("✓ Configuration updated successfully!")
        print("="*60 + "\n")
        
        return "okay"
    
    except Exception as error:
        print(f"\n✗ Error during configuration update: {str(error)}")
        return "error"


def Main(inputChoice="none") -> None:
    """
    Main entry point demonstrating tools manager usage.
    
    Provides interactive menu for:
    1. Retrieving current tools list
    2. Modifying tool selection
    3. Exiting the program
    
    Handles keyboard interrupts and unexpected errors gracefully.
    
    Side Effects:
        Loads configuration on startup
        Prints interactive menu prompts
        Calls GetToolsList() and updateToolsReturnValue() based on user input
    """
    try:
        # Initialize by loading configuration
        LoadToolsConfig()
        # input("Human01 ")

        while True:
            print("\n" + "="*60)
            print("TOOLS MANAGER MENU")
            print("="*60)
            print("\n1. get Tools List")
            print("2. update Tools Selection")
            print("3. Exit")
            print("-"*60)
            
            choice = "0"

            if inputChoice != "none":
                choice = inputChoice
            else:
                choice = input("\nSelect option (get, update, exit): ").strip()
            

            print(f"choice: {choice}")

            if choice == "get":
                print("\nRetrieving tools...")
                toolsList = GetToolsList()
                print(f"\nRetrieved {len(toolsList)} total tools")
                # input("Human02 ")
            
            elif choice == "update":
                result = updateToolsReturnValue()
                if result == "okay":
                    print("\nRefreshing tools list...")
                    toolsList = GetToolsList()
                # input("Human02 ")
            
            elif choice == "exit":
                print("\n✓ Exiting Tools Manager. Goodbye!")
                # input("Human02 ")
                break
            
            else:
                print("⚠ Invalid tools choice option.")
    
            return toolsList
    except KeyboardInterrupt:
        print("\n\n✗ Program interrupted by user")
        sys.exit(1)
    except Exception as error:
        print(f"\n✗ Unexpected error in main: {str(error)}")
        sys.exit(1)


# if __name__ == "__main__":
#     Main()


