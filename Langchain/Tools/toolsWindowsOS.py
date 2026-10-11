import urllib.parse
import os
import platform
import subprocess
import shutil
import getpass
import socket
from typing import Annotated, List, Any
from langchain.tools import tool
from Log.log_utils import PrintFunctionName

@tool("get_system_info", description="Retrieves basic Windows system information, including OS release, architecture, computer name, and current username.")
def GetSystemInfo() -> str:
    """Retrieves basic Windows system information, including OS release, architecture, computer name, and current username."""
    try:
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "node": platform.node(),
            "username": getpass.getuser(),
            "hostname": socket.gethostname()
        }
        return str(info)
    except Exception as e:
        return f"Error retrieving system info: {str(e)}"

@tool("list_running_processes", description="Lists top running Windows processes (Name, PID, and WorkingSet) to check system activity.")
def ListRunningProcesses(
    limit: Annotated[int, "Number of top processes to list (default 15)"] = 15
) -> str:
    """Lists top running Windows processes (Name and PID) using PowerShell."""
    try:
        cmd = f"Get-Process | Select-Object -First {limit} Name, Id, WorkingSet"
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode == 0:
            return result.stdout.strip() or "No process output."
        return result.stderr.strip() or "Error listing processes."
    except Exception as e:
        return f"Error listing processes: {str(e)}"

@tool("get_disk_usage", description="Checks available disk space and total storage capacity for specified Windows drives (e.g. C:\\).")
def GetDiskUsage(
    drive_path: Annotated[str, "Drive path (e.g., 'C:\\')"] = "C:\\"
) -> str:
    """Checks available disk space and total storage capacity for specified Windows drives."""
    try:
        usage = shutil.disk_usage(drive_path)
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        percent_free = (usage.free / usage.total) * 100
        
        info = (
            f"Drive: {drive_path}\n"
            f"Total Capacity: {total_gb:.2f} GB\n"
            f"Used Space: {used_gb:.2f} GB\n"
            f"Free Space: {free_gb:.2f} GB ({percent_free:.1f}% free)"
        )
        return info
    except Exception as e:
        return f"Error checking disk usage for {drive_path}: {str(e)}"

@tool("list_directory_contents", description="Lists files and folders in a specified Windows directory path with file sizes and item counts.")
def ListDirectoryContents(
    directory_path: Annotated[str, "Target directory path"]
) -> str:
    """Lists files and folders in a specified Windows directory path."""
    try:
        if not os.path.exists(directory_path):
            return f"Directory not found: {directory_path}"
        
        items = os.listdir(directory_path)
        result_lines = [f"Contents of {directory_path}: (Total items: {len(items)})"]
        for item in items[:50]:  # limit to first 50 items
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                result_lines.append(f"  [DIR]  {item}")
            else:
                try:
                    size = os.path.getsize(item_path)
                    result_lines.append(f"  [FILE] {item} ({size} bytes)")
                except Exception:
                    result_lines.append(f"  [FILE] {item}")
                    
        if len(items) > 50:
            result_lines.append(f"  ... and {len(items) - 50} more items.")
            
        return "\n".join(result_lines)
    except Exception as e:
        return f"Error listing directory {directory_path}: {str(e)}"

@tool("set_screen_brightness", description="Sets the display brightness of the Windows PC to a specified percentage (0-100%).")
def SetScreenBrightness(
    brightness_percentage: Annotated[int, "Brightness percentage (0 to 100)"]
) -> str:
    """Sets the display brightness of the Windows PC via PowerShell WMI."""
    try:
        bp = max(0, min(100, brightness_percentage))
        cmd = f"(Get-WmiObject -Namespace root\\wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {bp})"
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode == 0:
            return f"Successfully set screen brightness to {bp}%."
        return f"Failed to set brightness. Note: Some desktop monitors or VMs do not support WMI brightness control. Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error setting screen brightness: {str(e)}"

@tool("set_system_volume", description="Sets the master system audio volume to a specified percentage (0-100%).")
def SetSystemVolume(
    volume_percentage: Annotated[int, "Volume percentage (0 to 100)"]
) -> str:
    """Sets the master system audio volume using PowerShell audio endpoint or sound control."""
    try:
        vp = max(0, min(100, volume_percentage))
        cmd_vbs = f"""
        $obj = New-Object -ComObject WScript.Shell
        for ($i=0; $i -lt 50; $i++) {{ $obj.SendKeys([char]174) }}
        $steps = [Math]::Round({vp} / 2)
        for ($i=0; $i -lt $steps; $i++) {{ $obj.SendKeys([char]175) }}
        """
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd_vbs],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode == 0:
            return f"Successfully set system volume approximately to {vp}%."
        return result.stderr.strip() or f"Successfully executed volume command."
    except Exception as e:
        return f"Error setting system volume: {str(e)}"


# @tool("open_brave_youtube_music", description="Opens Brave browser directly to the YouTube Music home page.")
# def OpenBraveYouTubeMusic() -> str:
#     """Opens Brave browser directly to YouTube Music home."""
#     try:
#         url = "https://music.youtube.com"
#         brave_paths = [
#             r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
#             r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
#             os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe")
#         ]
        
#         launched = False
#         for path in brave_paths:
#             if os.path.exists(path):
#                 subprocess.Popen([path, url])
#                 launched = True
#                 break
                
#         if not launched:
#             subprocess.run(["cmd", "/c", "start", url], shell=True)
            
#         return "Successfully opened Brave to YouTube Music home."
#     except Exception as e:
#         return f"Error opening YouTube Music in Brave: {str(e)}"

@tool("play_youtube_music", description="Opens Brave browser to play a specific song, artist, or music query directly on YouTube.")
def PlayYouTubeMusic(
    query: Annotated[str, "Song name, artist, or music search query"],
    use_youtube_music: Annotated[bool, "Use YouTube Music (True) or standard YouTube (False)"] = False
) -> str:
    """Opens Brave browser to play music directly on YouTube using yt-dlp video ID lookup."""
    try:
        result = subprocess.run(
            ["yt-dlp", f"ytsearch1:{query}", "--get-id"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10
        )
        video_ids = result.stdout.strip().splitlines()
        
        if video_ids:
            vid = video_ids[0]
            url = f"https://www.youtube.com/watch?v={vid}"
        else:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
        brave_paths = [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe")
        ]
        
        launched = False
        for path in brave_paths:
            if os.path.exists(path):
                subprocess.Popen([path, url])
                launched = True
                break
                
        if not launched:
            subprocess.run(["cmd", "/c", "start", url], shell=True)
            
        return f"Successfully opened YouTube and playing: '{query}'"
    except Exception as e:
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            subprocess.run(["cmd", "/c", "start", url], shell=True)
            return f"Successfully opened YouTube with search query: '{query}'"
        except Exception as inner_e:
            return f"Error playing YouTube video in Brave: {str(inner_e)}"


toolsWindowsOS = [
    GetSystemInfo,
    ListRunningProcesses,
    GetDiskUsage,
    ListDirectoryContents,
    SetScreenBrightness,
    SetSystemVolume,
    # OpenBraveYouTubeMusic,
    PlayYouTubeMusic
]

def ToolsList():
    global toolsWindowsOS
    return toolsWindowsOS

