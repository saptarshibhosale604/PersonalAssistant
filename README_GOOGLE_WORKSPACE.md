# 🛠️ Google Workspace Integration Guide (Gmail & Calendar)

This document provides complete instructions on how to set up, configure, and operate the **Google Workspace Toolkits** (Gmail and Google Calendar) within the RPI Personal Assistant project.

---

## 📂 Architecture & Location
- **Gmail Module:** `Langchain/Tools/ToolsGoogleWorkspace/toolsGmail.py`
- **Calendar Module:** `Langchain/Tools/ToolsGoogleWorkspace/toolsCalendar.py`
- **Tool Manager Registration:** `Langchain/Tools/toolsManager.py` (`toolsGmail`, `toolsCalendar`)
- **Dependencies Config:** `Langchain/Tools/ToolsGoogleWorkspace/requirements.txt`

---

## 🚀 Step 1: Install Dependencies
Ensure all required Google API and LangChain community packages are installed in your environment:
```bash
pip install -r Langchain/Tools/ToolsGoogleWorkspace/requirements.txt
```
*(Or install manually via: `pip install langchain-google-community[gmail,calendar] google-auth-oauthlib google-auth-httplib2 google-api-python-client`)*

---

## 🔑 Step 2: Generate and Place `credentials.json`

To allow the assistant to interact with your Gmail and Google Calendar securely via OAuth 2.0, you must obtain a `credentials.json` file from the Google Cloud Console:

1. **Open Google Cloud Console:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
2. **Create a Project:**
   - Click the project dropdown at the top-left and select **New Project**. Name it `RPI-PersonalAssistant` and click **Create**. Ensure it is selected.
3. **Enable APIs:**
   - Navigate to **APIs & Services** > **Library**.
   - Search for and **Enable**:
     - **Gmail API**
     - **Google Calendar API**
4. **Configure OAuth Consent Screen:**
   - Go to **APIs & Services** > **OAuth consent screen**.
   - Choose **External** (or Internal) and click **Create**.
   - Fill in **App name** (`RPI Assistant`), **User support email**, and **Developer contact information**. Click **Save and Continue**.
   - Under **Test users**, add your personal Gmail address. Click **Save and Finish**.
5. **Create OAuth Client ID:**
   - Go to **APIs & Services** > **Credentials**.
   - Click **+ Create Credentials** > **OAuth client ID**.
   - Set **Application type** to **Desktop app**.
   - Name it `RPI-Desktop-Client` and click **Create**.
6. **Download & Place Credentials:**
   - Click **Download JSON** on the created client.
   - Rename the downloaded file to exactly **`credentials.json`**.
   - Place **`credentials.json`** directly into the project root directory:
     `E:\WORK\PROJECT\git\PersonalAssistant\credentials.json`

---

## 🔒 Step 3: First-Time Authentication & Token Generation

1. When you run your assistant and trigger a Google Workspace tool (e.g., listing calendar events or searching emails) for the first time:
   - The application will look for `credentials.json`.
   - It will initiate an OAuth local server flow (or open your default web browser).
2. Log in with your authorized Google account, review the permissions, and click **Allow**.
3. Each service caches its own token in the project root: **`token_gmail.json`** (Gmail scope) and **`token_calendar.json`** (Calendar scope). They are kept separate because a token is only valid for the scopes it was granted with; sharing one file caused Calendar calls to fail with `403 insufficient authentication scopes`. Expect one consent prompt per service on first run. To re-authenticate a service, delete its token file.

---

## 📋 Available Tools
Through LangChain's prebuilt `GmailToolkit` and `CalendarToolkit`, your assistant can now dynamically utilize tools including:
- **Gmail Tools:** Send emails, search messages, get message details, draft emails, etc.
- **Calendar Tools:** Create calendar events, list upcoming events, search events, etc.
