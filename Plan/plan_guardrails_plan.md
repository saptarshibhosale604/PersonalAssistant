# Plan: Implementing Strict Planning Mode Guardrails (`/plan`)

## 📌 Objective
Ensure that whenever the `/plan` command or skill is invoked, the AI assistant strictly formulates and presents an implementation blueprint without executing code, applying edits, or making codebase mutations.

---

## 🛠️ Implementation Steps & Guardrails

### 1. Update Core Directive Rules for Planning
- Whenever the user invokes `/plan` or requests a plan, the assistant must adopt the **Strategic Planner Protocol**:
  - **Read-Only Analysis:** Inspect existing code structure, requirements, and edge cases.
  - **No Workspace Mutations:** Do NOT modify files, do NOT run code commits, and do NOT execute system writes.
  - **Output Format:** Provide a clear, step-by-step implementation plan outlining files to modify, new files to create, and potential edge cases.

### 2. Update Plan Documentation Templates (`Plan/`)
- Add explicit warning headers to plan templates instructing executors to remain in read-only planning mode until explicit authorization (`/implement` or direct command) is received.

---

## ⚠️ Potential Edge Cases
- **User Ambiguity:** If the user prompt combines planning and implementation in a single request, the assistant must prioritize the **Planning** constraint first, present the plan, and await explicit authorization before executing.
- **Accidental Automation:** Ensure tool calls (such as `toolEditFile` or `toolWriteFile`) are strictly suppressed during plan generation mode.
