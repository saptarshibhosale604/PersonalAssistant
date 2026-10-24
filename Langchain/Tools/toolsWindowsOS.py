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
    SetScreenBrightness,
    SetSystemVolume,
    PlayYouTubeMusic
]

def ToolsList():
    global toolsWindowsOS
    return toolsWindowsOS
