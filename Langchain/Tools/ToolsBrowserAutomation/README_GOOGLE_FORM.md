# Google Forms Browser Automation Tool (RPI / JARVIS)

## 📌 Overview
The `toolsGoogleForms.py` module enables your tactical assistant (RPI) to interact directly with Google Forms open in Google Chrome via **Chrome DevTools Protocol (CDP)** and **Playwright**.

---

## 🚀 Prerequisites & Setup

### 1. Install Dependencies
Ensure Playwright and Chromium browser drivers are installed in your Python environment:
```powershell
pip install playwright
playwright install chromium
```

### 2. Launch Google Chrome with Remote Debugging
To allow RPI to inspect and fill forms in your browser, close all existing Chrome windows and launch Chrome with the remote debugging port enabled (`9222`):
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebugProfile"
```
Once Chrome opens, navigate to the Google Form you wish to fill.

---

## 🛠️ Available Tools

1. **`inspect_active_google_form`**
   - Connects to Chrome on port 9222.
   - Scans the active tab for Google Forms (`docs.google.com/forms`).
   - Extracts all questions, field types (`short_text`, `paragraph`, `multiple_choice`, `checkbox`), and available options.

2. **`fill_google_form`**
   - Takes a JSON payload mapping question titles, keywords, or question numbers to answers.
   - Automatically populates text fields and clicks corresponding radio buttons or checkboxes.
