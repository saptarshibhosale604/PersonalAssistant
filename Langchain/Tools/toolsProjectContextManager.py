"""
Tools Project Context Manager Module

This module provides the ReadProjectContext tool which reads and returns
the content of projectInfo.md for project overview and state awareness.

Author: Assistant
Created: October 2025
"""

import os
from langchain.tools import tool
from Log.log_utils import PrintFunctionName


@tool("ReadProjectContext", description="Read the projectInfo.md file to get project overview, technology stack, structure, and active status.")
@PrintFunctionName
def ReadProjectContext() -> str:
    """
    Read and return the content of projectInfo.md.

    Returns:
        str: Content of projectInfo.md or error message if not found.
    """
    possible_paths = [
        "projectInfo.md",
        "./projectInfo.md",
        "../projectInfo.md",
        "../../projectInfo.md",
        "/root/ProjectRpi/Rpi/PersonalAssistant/projectInfo.md",
        "/App/projectInfo.md"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(f"✓ Successfully read projectInfo.md from {path}")
                    return content
            except Exception as e:
                return f"Error reading projectInfo.md at {path}: {str(e)}"

    return "Error: projectInfo.md file not found."


# Standard tool module structure
toolsBasic = [ReadProjectContext]
toolsIntermediate = []
toolsAdvance = []

tools = toolsAdvance + toolsIntermediate + toolsBasic


@PrintFunctionName
def ToolsList():
    """
    Return the list of tools provided by this module.

    Returns:
        List: List of tool functions.
    """
    global tools
    return tools
