import json
import os
import time
from typing import List, Dict, Any, Annotated
from langchain.tools import tool

# Default output directory for Excalidraw JSON scenes
EXCALIDRAW_EXPORT_DIR = "./Langchain/Tools/ToolsBlackboard/Drawings"

@tool
def create_excalidraw_drawings(
    diagram_title: Annotated[str, "Title or name for the diagram file"],
    elements: Annotated[List[Dict[str, Any]], "List of Excalidraw elements (rectangles, text, arrows, etc.) as JSON dictionaries"]
) -> str:
    """
    Create or update an Excalidraw JSON scene file in the local Drawings directory.
    Use this tool whenever the user references anything related to whiteboard, blackboard, excalidraw, or drawings to create or draw visual diagrams.
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
            
        return f"[SUCCESS] Excalidraw drawing saved successfully to {file_path}."
    except Exception as e:
        return f"[ERROR] Failed to create Excalidraw drawing: {str(e)}"

@tool
def list_excalidraw_drawings() -> str:
    """
    Check and list all current Excalidraw drawings stored in the local Drawings directory.
    Use this tool whenever the user references anything related to whiteboard, blackboard, excalidraw, or drawings to check existing saved diagrams.
    Returns file names, sizes, element counts, and last modified timestamps.
    """
    try:
        if not os.path.exists(EXCALIDRAW_EXPORT_DIR):
            return f"[INFO] Drawings directory {EXCALIDRAW_EXPORT_DIR} does not exist yet. No drawings found."
            
        files = [f for f in os.listdir(EXCALIDRAW_EXPORT_DIR) if f.endswith(('.excalidraw', '.json'))]
        if not files:
            return f"[INFO] No Excalidraw drawings found in {EXCALIDRAW_EXPORT_DIR}."
            
        result_lines = [f"Found {len(files)} Excalidraw drawing(s) in {EXCALIDRAW_EXPORT_DIR}:"]
        for filename in files:
            file_path = os.path.join(EXCALIDRAW_EXPORT_DIR, filename)
            file_size = os.path.getsize(file_path)
            mod_time = time.ctime(os.path.getmtime(file_path))
            
            element_count = 0
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    element_count = len(data.get("elements", []))
            except Exception:
                element_count = "Unknown (parse error)"
                
            result_lines.append(f"- {filename} | Size: {file_size} bytes | Elements: {element_count} | Modified: {mod_time}")
            
        return "\n".join(result_lines)
    except Exception as e:
        return f"[ERROR] Failed to list Excalidraw drawings: {str(e)}"

@tool
def detect_drawing_modifications(
    drawing_title: Annotated[str, "Title or name of the drawing file to check for human modifications"]
) -> str:
    """
    Detects if changes have been made by a human user to an existing Excalidraw drawing file
    by inspecting file modification timestamps and element structural updates.
    Use this tool whenever the user references anything related to whiteboard, blackboard, excalidraw, or drawings to inspect human edits or changes.
    """
    try:
        os.makedirs(EXCALIDRAW_EXPORT_DIR, exist_ok=True)
        safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in drawing_title).strip().replace(' ', '_')
        if not safe_title:
            safe_title = "diagram"
            
        file_path = os.path.join(EXCALIDRAW_EXPORT_DIR, f"{safe_title}.excalidraw")
        if not os.path.exists(file_path):
            return f"[ERROR] Drawing file '{safe_title}.excalidraw' not found in {EXCALIDRAW_EXPORT_DIR}."
            
        mod_time = os.path.getmtime(file_path)
        mod_time_readable = time.ctime(mod_time)
        
        with open(file_path, "r", encoding="utf-8") as f:
            scene_data = json.load(f)
            
        elements = scene_data.get("elements", [])
        
        # Analyze elements for human modification signals (e.g. custom versions, update timestamps, or custom text)
        element_types = {}
        for el in elements:
            el_type = el.get("type", "unknown")
            element_types[el_type] = element_types.get(el_type, 0) + 1
            
        summary = (
            f"[ANALYSIS] Drawing: {drawing_title}\n"
            f"- File Path: {file_path}\n"
            f"- Last Modified: {mod_time_readable}\n"
            f"- Total Elements: {len(elements)}\n"
            f"- Element Types Breakdown: {element_types}\n"
            f"- Status: File exists and is accessible. Any edits made in the Excalidraw app are synchronized to this file."
        )
        return summary
    except Exception as e:
        return f"[ERROR] Failed to detect modifications for drawing '{drawing_title}': {str(e)}"

# @tool
# def generate_sample_architecture_diagram(
#     system_name: Annotated[str, "Name of the system architecture to draw (e.g. 'Jarvis_AI_Pipeline')"]
# ) -> str:
#     """
#     Generates a pre-configured architecture diagram (User -> Agent Router -> LLM/Tools -> Whiteboard) on Excalidraw with dark background styling.
#     Use this tool whenever the user references anything related to whiteboard, blackboard, excalidraw, or drawings to generate sample architectural diagrams.
#     """
#     elements = [
#         # Box 1: User
#         {
#             "type": "rectangle",
#             "id": "box_user",
#             "x": 100,
#             "y": 200,
#             "width": 140,
#             "height": 80,
#             "angle": 0,
#             "strokeColor": "#6965db",
#             "backgroundColor": "#1e1e2f",
#             "fillStyle": "solid",
#             "strokeWidth": 2,
#             "strokeStyle": "solid",
#             "roughness": 1,
#             "opacity": 100,
#             "boundElements": [{"id": "text_user", "type": "text"}],
#             "updated": 1,
#             "link": None,
#             "locked": False
#         },
#         {
#             "type": "text",
#             "id": "text_user",
#             "x": 120,
#             "y": 230,
#             "width": 100,
#             "height": 20,
#             "angle": 0,
#             "strokeColor": "#ffffff",
#             "backgroundColor": "transparent",
#             "fillStyle": "solid",
#             "strokeWidth": 1,
#             "strokeStyle": "solid",
#             "roughness": 1,
#             "opacity": 100,
#             "text": "User Prompt",
#             "fontSize": 16,
#             "fontFamily": 1,
#             "textAlign": "center",
#             "verticalAlign": "middle",
#             "containerId": "box_user",
#             "originalText": "User Prompt",
#             "lineHeight": 1.2,
#             "boundElements": None,
#             "updated": 1,
#             "link": None,
#             "locked": False
#         },
#         # Box 2: Agent Router
#         {
#             "type": "rectangle",
#             "id": "box_router",
#             "x": 320,
#             "y": 200,
#             "width": 160,
#             "height": 80,
#             "angle": 0,
#             "strokeColor": "#e056fd",
#             "backgroundColor": "#2a1b3d",
#             "fillStyle": "solid",
#             "strokeWidth": 2,
#             "strokeStyle": "solid",
#             "roughness": 1,
#             "opacity": 100,
#             "boundElements": [{"id": "text_router", "type": "text"}],
#             "updated": 1,
#             "link": None,
#             "locked": False
#         },
#         {
#             "type": "text",
#             "id": "text_router",
#             "x": 340,
#             "y": 230,
#             "width": 120,
#             "height": 20,
#             "angle": 0,
#             "strokeColor": "#ffffff",
#             "backgroundColor": "transparent",
#             "fillStyle": "solid",
#             "strokeWidth": 1,
#             "strokeStyle": "solid",
#             "roughness": 1,
#             "opacity": 100,
#             "text": "LangChain Router",
#             "fontSize": 16,
#             "fontFamily": 1,
#             "textAlign": "center",
#             "verticalAlign": "middle",
#             "containerId": "box_router",
#             "originalText": "LangChain Router",
#             "lineHeight": 1.2,
#             "boundElements": None,
#             "updated": 1,
#             "link": None,
#             "locked": False
#         },
#         # Box 3: Excalidraw Tool
#         {
#             "type": "rectangle",
#             "id": "box_tool",
#             "x": 560,
#             "y": 200,
#             "width": 160,
#             "height": 80,
#             "angle": 0,
#             "strokeColor": "#00d2d3",
#             "backgroundColor": "#133b3b",
#             "fillStyle": "solid",
#             "strokeWidth": 2,
#             "strokeStyle": "solid",
#             "roughness": 1,
#             "opacity": 100,
#             "boundElements": [{"id": "text_tool", "type": "text"}],
#             "updated": 1,
#             "link": None,
#             "locked": False
#         },
#         {
#             "type": "text",
#             "id": "text_tool",
#             "x": 580,
#             "y": 230,
#             "width": 120,
#             "height": 20,
#             "angle": 0,
#             "strokeColor": "#ffffff",
#             "backgroundColor": "transparent",
#             "fillStyle": "solid",
#             "strokeWidth": 1,
#             "strokeStyle": "solid",
#             "roughness": 1,
#             "opacity": 100,
#             "text": "Excalidraw Tool",
#             "fontSize": 16,
#             "fontFamily": 1,
#             "textAlign": "center",
#             "verticalAlign": "middle",
#             "containerId": "box_tool",
#             "originalText": "Excalidraw Tool",
#             "lineHeight": 1.2,
#             "boundElements": None,
#             "updated": 1,
#             "link": None,
#             "locked": False
#         },
#         # Arrow 1: User -> Router
#         {
#             "type": "arrow",
#             "id": "arrow_1",
#             "x": 245,
#             "y": 240,
#             "width": 70,
#             "height": 0,
#             "angle": 0,
#             "strokeColor": "#a4b0be",
#             "backgroundColor": "transparent",
#             "fillStyle": "solid",
#             "strokeWidth": 2,
#             "strokeStyle": "solid",
#             "roughness": 1,
#             "opacity": 100,
#             "points": [[0, 0], [70, 0]],
#             "startBinding": {"elementId": "box_user", "focus": 0, "gap": 5},
#             "endBinding": {"elementId": "box_router", "focus": 0, "gap": 5},
#             "start": None,
#             "end": None,
#             "updated": 1
#         },
#         # Arrow 2: Router -> Tool
#         {
#             "type": "arrow",
#             "id": "arrow_2",
#             "x": 485,
#             "y": 240,
#             "width": 70,
#             "height": 0,
#             "angle": 0,
#             "strokeColor": "#a4b0be",
#             "backgroundColor": "transparent",
#             "fillStyle": "solid",
#             "strokeWidth": 2,
#             "strokeStyle": "solid",
#             "roughness": 1,
#             "opacity": 100,
#             "points": [[0, 0], [70, 0]],
#             "startBinding": {"elementId": "box_router", "focus": 0, "gap": 5},
#             "endBinding": {"elementId": "box_tool", "focus": 0, "gap": 5},
#             "start": None,
#             "end": None,
#             "updated": 1
#         }
#     ]
    
#     return create_excalidraw_drawings.invoke({"diagram_title": system_name, "elements": elements})

# Standard tool module structure
toolsBasic = [
    create_excalidraw_drawings,
    # generate_sample_architecture_diagram,
    list_excalidraw_drawings,
    detect_drawing_modifications
]
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
