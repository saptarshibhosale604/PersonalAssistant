# README_BLACKBOARD.md

## 🖍️ Excalidraw Setup & Run Guide (`./excalidraw`)

This repository includes **Excalidraw** as a separate git repository located in the `./excalidraw` directory. Excalidraw is an open-source virtual collaborative whiteboard web application built as a React monorepo.

---

### 📂 Project Structure & Architecture

Excalidraw is structured as a **Yarn workspace monorepo**:
- **`excalidraw/packages/excalidraw/`**: The core React drawing library (published to npm as `@excalidraw/excalidraw`).
- **`excalidraw/excalidraw-app/`**: The full-featured web application (`excalidraw.com` interface).
- **`excalidraw/packages/`**: Core packages (`@excalidraw/common`, `@excalidraw/element`, `@excalidraw/math`, `@excalidraw/utils`, etc.).
- **`excalidraw/examples/`**: Integration examples (Next.js, browser script embeds).

---

### ⚙️ Prerequisites & Cloning

Before running Excalidraw in this project, ensure you have the following installed on your Windows machine:
- **Node.js** (v18.0.0 or higher recommended, e.g., v22.x)
- **Yarn** package manager (`yarn`)
- **Git**

If `./excalidraw` is not already present in your project workspace as a separate repository, clone it into the root directory:
```powershell
git clone https://github.com/excalidraw/excalidraw.git excalidraw
```

---

### 🚀 How to Install and Run

Open your terminal (PowerShell or Command Prompt) at the root of the project (`E:\WORK\PROJECT\git\PersonalAssistant`), then follow these steps:

#### 1. Navigate to the Excalidraw Directory
```powershell
cd excalidraw
```

#### 2. Install Dependencies
Install all workspace dependencies using Yarn:
```powershell
yarn install
```

#### 3. Start the Development Server
Run the local development server for the Excalidraw web application:
```powershell
yarn start
```
*(Alternatively, you can run `yarn --cwd excalidraw-app start` from the repository root).*

#### 4. Access the Whiteboard
Once the development server boots up (typically via Vite on port `3000` or `5173`), open your browser and navigate to:
👉 `http://localhost:3000` (or check your terminal output for the exact local URL).

---

### 🧪 Additional Commands

- **Type Checking:**
  ```powershell
  yarn test:typecheck
  ```
- **Run Tests:**
  ```powershell
  yarn test
  ```
- **Build for Production:**
  ```powershell
  yarn build
  ```
