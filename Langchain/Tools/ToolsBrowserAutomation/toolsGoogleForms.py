import os
import json
from typing import Annotated, Dict, Any, List
from langchain.tools import tool
from Log.log_utils import PrintFunctionName

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def _get_or_launch_browser(p):
    """Attempts to connect to Chrome over CDP on port 9222. If not running, launches Chrome automatically."""
    try:
        return p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    except Exception:
        # Fallback: Automatically launch Chrome in debug mode if not already running
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]
        
        launch_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                launch_path = path
                break
                
        if not launch_path:
            raise RuntimeError("Google Chrome executable not found on standard paths.")
            
        debug_dir = os.path.expandvars(r"%LOCALAPPDATA%\TempChromeDebug")
        os.makedirs(debug_dir, exist_ok=True)
        
        # Launch Chrome with debugging port
        import subprocess
        subprocess.Popen([launch_path, "--remote-debugging-port=9222", f"--user-data-dir={debug_dir}"])
        
        # Wait for port to become active
        import time
        for _ in range(10):
            try:
                return p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            except Exception:
                time.sleep(1)
        raise RuntimeError("Could not establish CDP connection after automatic Chrome launch.")


@tool("inspect_active_google_form", description="Inspects the active Google Form tab in Chrome (auto-launching debug session if needed), extracting all questions, field types, and identifiers.")
def InspectActiveGoogleForm() -> str:
    """Connects via CDP to Chrome, finds the active Google Form, and extracts question fields."""
    if not PLAYWRIGHT_AVAILABLE:
        return "[ERROR] Playwright is not installed. Please run 'pip install playwright' and 'playwright install chromium'."
    
    try:
        with sync_playwright() as p:
            browser = _get_or_launch_browser(p)
            
            contexts = browser.contexts
            target_page = None
            
            for context in contexts:
                for page in context.pages:
                    if "docs.google.com/forms" in page.url:
                        target_page = page
                        break
                if target_page:
                    break
            
            if not target_page:
                # If no form open, open a default placeholder or let user know
                if browser.contexts and browser.contexts[0].pages:
                    target_page = browser.contexts[0].pages[0]
                else:
                    target_page = browser.new_context().new_page()
                return "[INFO] Connected to Chrome, but no active Google Form tab was found. Please navigate to your Google Form in Chrome."
            
            # Extract form questions and fields using JS evaluation
            form_data = target_page.evaluate("""() => {
                const title = document.querySelector('div.F9hGLd') ? document.querySelector('div.F9hGLd').innerText : document.title;
                const questions = [];
                
                const blocks = document.querySelectorAll('div[role="listitem"]');
                for (let index = 0; index < blocks.length; index++) {
                    const block = blocks[index];
                    const headingEl = block.querySelector('div[role="heading"]');
                    const questionText = headingEl ? headingEl.innerText : 'Question ' + (index + 1);
                    
                    let fieldType = 'unknown';
                    if (block.querySelector('input[type="text"]')) fieldType = 'short_text';
                    else if (block.querySelector('textarea')) fieldType = 'paragraph';
                    else if (block.querySelectorAll('div[role="radio"]').length > 0) fieldType = 'multiple_choice';
                    else if (block.querySelectorAll('div[role="checkbox"]').length > 0) fieldType = 'checkbox';
                    else if (block.querySelector('select')) fieldType = 'dropdown';
                    
                    let options = [];
                    if (fieldType === 'multiple_choice' || fieldType === 'checkbox') {
                        const optEls = block.querySelectorAll('div[role="radio"], div[role="checkbox"]');
                        for (let j = 0; j < optEls.length; j++) {
                            const opt = optEls[j];
                            const optText = opt.getAttribute('aria-label') || opt.innerText;
                            if (optText) options.push(optText.trim());
                        }
                    }
                    
                    questions.push({
                        index: index + 1,
                        question: questionText.replace(/\\*/g, '').trim(),
                        type: fieldType,
                        options: options
                    });
                }
                
                return { form_title: title, total_questions: questions.length, fields: questions };
            }""")
            
            return json.dumps(form_data, indent=2)
            
    except Exception as e:
        return f"[ERROR] Failed to inspect Google Form: {str(e)}"


@tool("fill_google_form", description="Automatically fills out the active Google Form in Chrome using a provided dictionary mapping question titles or numbers to answer values.")
def FillGoogleForm(
    answers_json: Annotated[str, "JSON string mapping question identifiers (or keywords) to answer values"]
) -> str:
    """Fills out the active Google Form in Chrome using Playwright CDP connection."""
    if not PLAYWRIGHT_AVAILABLE:
        return "[ERROR] Playwright is not installed."
        
    try:
        answers = json.loads(answers_json)
    except json.JSONDecodeError as e:
        return f"[ERROR] Invalid JSON provided for answers: {str(e)}"
        
    try:
        with sync_playwright() as p:
            browser = _get_or_launch_browser(p)
            
            target_page = None
            for context in browser.contexts:
                for page in context.pages:
                    if "docs.google.com/forms" in page.url:
                        target_page = page
                        break
                if target_page:
                    break
                    
            if not target_page:
                return "[ERROR] No active Google Form tab found in Chrome. Please open the Google Form tab."
                
            results = target_page.evaluate("""(answersMap) => {
                const logs = [];
                const blocks = document.querySelectorAll('div[role="listitem"]');
                
                for (let i = 0; i < blocks.length; i++) {
                    const block = blocks[i];
                    const headingEl = block.querySelector('div[role="heading"]');
                    const qText = headingEl ? headingEl.innerText.toLowerCase() : '';
                    const qKeyNum = String(i + 1);
                    
                    let matchedVal = null;
                    for (const key in answersMap) {
                        if (Object.prototype.hasOwnProperty.call(answersMap, key)) {
                            const val = answersMap[key];
                            if (qText.indexOf(key.toLowerCase()) !== -1 || key === qKeyNum || key === 'q' + qKeyNum) {
                                matchedVal = val;
                                break;
                            }
                        }
                    }
                    
                    if (matchedVal !== null) {
                        const textInput = block.querySelector('input[type="text"], textarea');
                        if (textInput) {
                            textInput.focus();
                            textInput.value = matchedVal;
                            textInput.dispatchEvent(new Event('input', { bubbles: true }));
                            textInput.dispatchEvent(new Event('change', { bubbles: true }));
                            logs.push('Filled text for question ' + (i + 1) + ': ' + matchedVal);
                        } else {
                            const options = block.querySelectorAll('div[role="radio"], div[role="checkbox"]');
                            let foundOpt = false;
                            for (let j = 0; j < options.length; j++) {
                                const opt = options[j];
                                const optText = opt.getAttribute('aria-label') || opt.innerText;
                                if (optText && optText.toLowerCase().indexOf(String(matchedVal).toLowerCase()) !== -1) {
                                    opt.click();
                                    foundOpt = true;
                                    logs.push('Selected option for question ' + (i + 1));
                                    break;
                                }
                            }
                            if (!foundOpt) {
                                logs.push('Warning: Could not find option for question ' + (i + 1));
                            }
                        }
                    }
                }
                return logs;
            }""", answers)
            
            return f"Successfully executed form filling. Action logs:\n" + "\n".join(results)
            
    except Exception as e:
        return f"[ERROR] Failed during form filling: {str(e)}"
