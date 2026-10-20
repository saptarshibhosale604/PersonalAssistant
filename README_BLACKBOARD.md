# Excalidraw Whiteboard Integration & Setup Guide

This project integrates **Excalidraw** as a local submodule/sub-repository inside the `./excalidraw` directory, providing interactive whiteboard and canvas state capabilities directly within the Personal Assistant web application (`UI/WebApp/app.py`) and LangChain tools (`toolsExcalidraw`).

---

## 📂 Project Structure & Components

1. **`./excalidraw/`**: Separate Git repository containing the full Excalidraw React application source code.
2. **`UI/WebApp/app.py`**: Flask web server configured with routes:
   - `/whiteboard`: Renders the whiteboard interface (`whiteboard.html`).
   - `/api/canvas/state`: GET/POST endpoints to persist and sync canvas state (`./Langchain/Tools/whiteboard_state.json`).
3. **`Langchain/Tools/toolsExcalidraw`**: LangChain tool module registered in `toolsManager.py` to allow AI agents to interact with whiteboard elements and state.
4. **`.gitignore`**: Configured to ignore the local `./excalidraw/` build artifacts, node modules, and state files.

---

## ⚙️ How to Setup & Run

### 1. Install Excalidraw Dependencies
Navigate into the `./excalidraw` directory and install the required npm packages:
```powershell
cd excalidraw
npm install
# or yarn install
```

### 2. Run Excalidraw Development Server
Excalidraw runs locally as a React Vite/Webpack app (typically on port `3000` or `5173`):
```powershell
npm run start
# or yarn start
```

### 3. Run the Personal Assistant Web Application
In a separate PowerShell terminal, start the main Flask web application:
```powershell
python UI/WebApp/app.py
```
* Access the whiteboard view at: `http://localhost:5000/whiteboard` (or the configured Flask port).

---

## 🛠️ API & Tool Integration
- **State persistence**: Canvas JSON elements are stored locally at `./Langchain/Tools/whiteboard_state.json`.
- **AI Agent Tool**: The `toolsExcalidraw` tool enables agents to read, write, and update whiteboard elements programmatically during assistant turns.
