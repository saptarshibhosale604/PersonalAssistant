# Implementation Plan: Brave YouTube Music Tools in \	oolsWindowsOS.py\

This plan outlines the addition of simple, robust tools to \Langchain/Tools/toolsWindowsOS.py\ for launching the Brave browser with specific YouTube music URLs, search queries, or playlists.

## 1. Objectives
- Add new \@tool\ decorated functions in \	oolsWindowsOS.py\.
- Support opening the Brave browser directly to:
  1. **YouTube Music Home / General Music** (\https://music.youtube.com\)
  2. **Play a specific song or artist search query** on YouTube or YouTube Music via Brave.
- Ensure integration into the exported \	oolsWindowsOS\ list so the agent can discover and invoke them automatically.

---

## 2. Proposed Tools

### Tool 1: \open_brave_youtube_music\
- **Decorator / Name**: \@tool("open_brave_youtube_music", description="Opens Brave browser directly to the YouTube Music home page.")\
- **Parameters**: None.
- **Implementation Details**:
  - Opens \https://music.youtube.com\ in Brave by locating common Brave executable paths on Windows or falling back to the system start command.

### Tool 2: \play_youtube_music\
- **Decorator / Name**: \@tool("play_youtube_music", description="Opens Brave browser to search and play a specific song, artist, or music query on YouTube Music.")\
- **Parameters**:
  - \query\ (Annotated[str, "Song name, artist, or music search query"]): The search term (e.g. "lofi hip hop", "Queen Bohemian Rhapsody").
  - \use_youtube_music\ (Annotated[bool, "Whether to use music.youtube.com (True) or standard youtube search (False)"]): Defaults to \True\.
- **Implementation Details**:
  - Encodes the search query using \urllib.parse.quote\.
  - Constructs URL (\https://music.youtube.com/search?q={encoded_query}\).
  - Launches Brave via subprocess.

---

## 3. Detailed Code Implementation Design

`python
import urllib.parse
# ... existing imports ...

@tool("open_brave_youtube_music", description="Opens Brave browser directly to the YouTube Music home page.")
def OpenBraveYouTubeMusic() -> str:
    \"\"\"Opens Brave browser directly to YouTube Music home.\"\"\"
    try:
        url = "https://music.youtube.com"
        brave_paths = [
            r"C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
            r"C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\Application\\brave.exe")
        ]
        
        launched = False
        for path in brave_paths:
            if os.path.exists(path):
                subprocess.Popen([path, url])
                launched = True
                break
                
        if not launched:
            subprocess.run(["cmd", "/c", "start", url], shell=True)
            
        return "Successfully opened Brave to YouTube Music home."
    except Exception as e:
        return f"Error opening YouTube Music in Brave: {{str(e)}}"


@tool("play_youtube_music", description="Opens Brave browser to search and play a specific song, artist, or music query on YouTube Music.")
def PlayYouTubeMusic(
    query: Annotated[str, "Song name, artist, or music search query"],
    use_youtube_music: Annotated[bool, "Use YouTube Music (True) or standard YouTube (False)"] = True
) -> str:
    \"\"\"Opens Brave browser to search and play music.\"\"\"
    try:
        encoded_query = urllib.parse.quote(query)
        if use_youtube_music:
            url = f"https://music.youtube.com/search?q={{encoded_query}}"
        else:
            url = f"https://www.youtube.com/results?search_query={{encoded_query}}"
            
        brave_paths = [
            r"C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
            r"C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\Application\\brave.exe")
        ]
        
        launched = False
        for path in brave_paths:
            if os.path.exists(path):
                subprocess.Popen([path, url])
                launched = True
                break
                
        if not launched:
            subprocess.run(["cmd", "/c", "start", url], shell=True)
            
        return f"Successfully opened Brave with YouTube music query: '{query}'"
    except Exception as e:
        return f"Error opening YouTube music in Brave: {{str(e)}}"
`

---

## 4. Updating \	oolsWindowsOS\ List
Add \OpenBraveYouTubeMusic\ and \PlayYouTubeMusic\ to the \	oolsWindowsOS\ list:
`python
toolsWindowsOS = [
    GetSystemInfo,
    ListRunningProcesses,
    GetDiskUsage,
    ListDirectoryContents,
    SetScreenBrightness,
    SetSystemVolume,
    OpenBraveYouTubeMusic,
    PlayYouTubeMusic
]
`

---

## 5. Testing Plan
1. Apply changes to \Langchain/Tools/toolsWindowsOS.py\.
2. Run a quick python snippet to test \PlayYouTubeMusic(query="lofi beats")\ and \OpenBraveYouTubeMusic()\.
3. Verify Brave opens correctly with the expected URLs.
