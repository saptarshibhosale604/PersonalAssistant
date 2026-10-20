import json
import os
from typing import List, Dict, Any, Annotated
from langchain.tools import tool

# Default output directory for Excalidraw JSON scenes
EXCALIDRAW_EXPORT_DIR = "./excalidraw/excalidraw-app/public/drawings"

@tool
def create_excalidraw_diagram(
    diagram_title: Annotated[str, "Title or name for the diagram file"],
    elements: Annotated[List[Dict[str, Any]], "List of Excalidraw elements (rectangles, text, arrows, etc.) as JSON dictionaries"]
) -> str:
    """
    Create or update an Excalidraw JSON scene file that can be instantly loaded into the local Excalidraw whiteboard.
    The elements list should contain valid Excalidraw JSON element objects (e.g., rectangles, ellipses, text, arrows).
    """
    try:
        os.makedirs(EXCALIDRAW_EXPORT_DIR, exist_ok=True)
        
        # Ensure safe filename
        safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in diagram_title).strip().replace(' ', '_')
        if not safe_title:
            safe_title = "diagram"
            
        file_path = os.path.join(EXCALIDRAW_EXPORT_DIR, f"{safe_title}.excalidraw")
        
        scene_data = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": elements,
            "appState": {
                "viewBackgroundColor": "#121212", # Dark background as requested!
                "gridSize": 20,
                "theme": "dark"
            },
            "files": {}
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(scene_data, f, indent=2)
            
        return f"[SUCCESS] Excalidraw diagram saved successfully to {file_path}. You can open or import this file in your running Excalidraw app at http://localhost:3000."
    except Exception as e:
        return f"[ERROR] Failed to create Excalidraw diagram: {str(e)}"

@tool
def generate_sample_architecture_diagram(
    system_name: Annotated[str, "Name of the system architecture to draw (e.g. 'Jarvis_AI_Pipeline')"]
) -> str:
    """
    Generates a pre-configured architecture diagram (User -> Agent Router -> LLM/Tools -> Whiteboard) on Excalidraw with dark background styling.
    """
    elements = [
        # Box 1: User
        {
            "type": "rectangle",
            "id": "box_user",
            "x": 100,
            "y": 200,
            "width": 140,
            "height": 80,
            "angle": 0,
            "strokeColor": "#6965db",
            "backgroundColor": "#1e1e2f",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "boundElements": [{"id": "text_user", "type": "text"}],
            "updated": 1,
            "link": None,
            "locked": False
        },
        {
            "type": "text",
            "id": "text_user",
            "x": 120,
            "y": 230,
            "width": 100,
            "height": 20,
            "angle": 0,
            "strokeColor": "#ffffff",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "text": "User Prompt",
            "fontSize": 16,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": "box_user",
            "originalText": "User Prompt",
            "lineHeight": 1.2,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False
        },
        # Box 2: Agent Router
        {
            "type": "rectangle",
            "id": "box_router",
            "x": 320,
            "y": 200,
            "width": 160,
            "height": 80,
            "angle": 0,
            "strokeColor": "#e056fd",
            "backgroundColor": "#2a1b3d",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "boundElements": [{"id": "text_router", "type": "text"}],
            "updated": 1,
            "link": None,
            "locked": False
        },
        {
            "type": "text",
            "id": "text_router",
            "x": 340,
            "y": 230,
            "width": 120,
            "height": 20,
            "angle": 0,
            "strokeColor": "#ffffff",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "text": "LangChain Router",
            "fontSize": 16,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": "box_router",
            "originalText": "LangChain Router",
            "lineHeight": 1.2,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False
        },
        # Box 3: Excalidraw Tool
        {
            "type": "rectangle",
            "id": "box_tool",
            "x": 560,
            "y": 200,
            "width": 160,
            "height": 80,
            "angle": 0,
            "strokeColor": "#00d2d3",
            "backgroundColor": "#133b3b",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "boundElements": [{"id": "text_tool", "type": "text"}],
            "updated": 1,
            "link": None,
            "locked": False
        },
        {
            "type": "text",
            "id": "text_tool",
            "x": 580,
            "y": 230,
            "width": 120,
            "height": 20,
            "angle": 0,
            "strokeColor": "#ffffff",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "text": "Excalidraw Tool",
            "fontSize": 16,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": "box_tool",
            "originalText": "Excalidraw Tool",
            "lineHeight": 1.2,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False
        },
        # Arrow 1: User -> Router
        {
            "type": "arrow",
            "id": "arrow_1",
            "x": 245,
            "y": 240,
            "width": 70,
            "height": 0,
            "angle": 0,
            "strokeColor": "#a4b0be",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "points": [[0, 0], [70, 0]],
            "startBinding": {"elementId": "box_user", "focus": 0, "gap": 5},
            "endBinding": {"elementId": "box_router", "focus": 0, "gap": 5},
            "start": None,
            "end": None,
            "updated": 1
        },
        # Arrow 2: Router -> Tool
        {
            "type": "arrow",
            "id": "arrow_2",
            "x": 485,
            "y": 240,
            "width": 70,
            "height": 0,
            "angle": 0,
            "strokeColor": "#a4b0be",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "points": [[0, 0], [70, 0]],
            "startBinding": {"elementId": "box_router", "focus": 0, "gap": 5},
            "endBinding": {"elementId": "box_tool", "focus": 0, "gap": 5},
            "start": None,
            "end": None,
            "updated": 1
        }
    ]
    
    return create_excalidraw_diagram.invoke({"diagram_title": system_name, "elements": elements})

# Standard tool module structure
toolsBasic = [create_excalidraw_diagram, generate_sample_architecture_diagram]
toolsIntermediate = []
toolsAdvance = []

tools = toolsAdvance + toolsIntermediate + toolsBasic


def ToolsList():
    """
    Return the list of tools provided by this module.

    Returns:
        List: List of tool functions.
    """
    global tools
    return tools
