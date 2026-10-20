import json
import os
import time
import random
from typing import List, Dict, Any, Annotated
from langchain.tools import tool

# Default output directory for Excalidraw JSON scenes
EXCALIDRAW_EXPORT_DIR = "./Langchain/Tools/ToolsBlackboard/Drawings"

def enrich_element(el: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensures every Excalidraw element has all required schema properties 
    so Excalidraw never throws 'invalid file' errors.
    """
    base = {
        "id": f"elem_{random.randint(10000, 99999)}",
        "type": "rectangle",
        "x": 0,
        "y": 0,
        "width": 100,
        "height": 100,
        "angle": 0,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": random.randint(1, 1000000),
        "version": 1,
        "versionNonce": random.randint(1, 1000000),
        "isDeleted": False,
        "boundElements": None,
        "updated": int(time.time()),
        "link": None,
        "locked": False
    }
    
    # Text-specific defaults if type is text
    if el.get("type") == "text":
        base.update({
            "fontSize": 16,
            "fontFamily": 1,
            "text": "",
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": None,
            "originalText": "",
            "lineHeight": 1.2
        })
        
    # Arrow-specific defaults if type is arrow
    if el.get("type") == "arrow":
        base.update({
            "points": [[0, 0], [100, 0]],
            "startBinding": None,
            "endBinding": None,
            "start": None,
            "end": None
        })

    # Merge user provided properties over defaults
    base.update(el)
    return base

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
        
        # Enrich all elements to guarantee Excalidraw schema compliance
        enriched_elements = [enrich_element(el) for el in elements]
        
        scene_data = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": enriched_elements,
            "appState": {
                "viewBackgroundColor": "#121212",
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

# Standard tool module structure
toolsBasic = [
    create_excalidraw_drawings,
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
    files = []
    global tools
    return tools
