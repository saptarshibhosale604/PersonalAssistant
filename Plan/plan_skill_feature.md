# Plan: Implement `/skill` Feature in Personal Assistant CLI

## 📌 Overview
Add a `/skill` command to the CLI (`UI/cli.py`) that presents an interactive menu of available skills from a `Skill/` directory, allows the user to select a skill by number (or quit with `'q'`), reads the selected skill file content, and injects it as the `userInput` into the agent processing pipeline.

---

## 🛠️ Implementation Steps

### Step 1: Create Directory and Sample Skill Files
- Create the `./Skill/` directory at the project root.
- Populate sample skill files inside `./Skill/`:
  - `git-push`
  - `understand-project`
  - `plan-this`
  - `implement-this`

### Step 2: Update Help Documentation in `UI/cli.py`
- Modify `BasicCmds02()` under the `command in ("/", "/help")` block to include `/skill` in the list of available commands.

### Step 3: Implement `/skill` Command Handler in `UI/cli.py`
Add `elif command == "/skill":` inside `BasicCmds02()` with the following logic:
1. **Directory Check:** Ensure `./Skill/` exists (create if missing).
2. **Scan Skills:** Read all files present in `./Skill/`. Fallback to standard default skill names if empty.
3. **Display Menu:** Print the menu format:
   ```text
   skillManager: select the mode:
   'q' to quit from the skillManager

   1. skill git-push            
   2. skill understand-project      
   3. skill plan-this
   4. skill implement-this
   ```
4. **User Input & Quit Handling:**
   - Prompt user via `input()`.
   - If user inputs `'q'` or `'Q'`, exit the skill manager (`skillManager: Goodbye!`).
   - If user inputs a number corresponding to a skill:
     - Resolve the file path (`Skill/<selected_skill>`).
     - Read file content.
     - Pass the content directly into `Processing(skill_content)` and output the result.
5. **Error Handling:** Catch invalid indices and non-numeric inputs gracefully.
