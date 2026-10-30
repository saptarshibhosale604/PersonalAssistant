"""
Module: extract_session_logs.py
Description: Scans Log/SessionLog/ for session JSON files starting from session 0445 onwards,
extracts turn-by-turn user inputs and agent outputs, estimates token counts per session
using Option C heuristic, and automatically chunks/dumps them into batch JSON files
whenever cumulative tokens exceed a 4,000-token threshold.
"""

import os
import re
import json
from datetime import datetime

def load_json_tolerant(filepath):
    """Loads JSON data from file, handling appended log text after the valid JSON object."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        content = content.lstrip()
        try:
            obj, idx = decoder.raw_decode(content)
            return obj
        except Exception as err:
            raise err

def estimate_tokens(text):
    """Option C heuristic: approx 4 characters per token."""
    if not text:
        return 0
    return int(len(str(text)) / 4.0)

def extract_and_chunk_sessions():
    source_dir = "Log/SessionLog"
    output_dir = "Log/UserContextRawInput"
    
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(source_dir):
        print(f"[ERROR] Source directory '{source_dir}' does not exist, General!")
        return

    session_pattern = re.compile(r"^session_(\d{4})_.*\.json$")
    
    matched_files = []
    # min_session_num = 445
    min_session_num = 400
    
    for filename in os.listdir(source_dir):
        match = session_pattern.match(filename)
        if match:
            sess_num = int(match.group(1))
            if sess_num >= min_session_num:
                matched_files.append((sess_num, filename))

    if not matched_files:
        print(f"[WARNING] No session files found from session {min_session_num:04d} onwards.")
        return

    matched_files.sort(key=lambda x: x[0])
    
    current_batch_sessions = []
    current_batch_tokens = 0
    batch_counter = 1
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    batch_start_sess = None

    print(f"[TACTICAL] Processing {len(matched_files)} session files with 4K token threshold per file batch...")

    for sess_num, filename in matched_files:
        filepath = os.path.join(source_dir, filename)
        
        if os.path.getsize(filepath) == 0:
            print(f"[SKIP] Session file {filename} is empty (0 bytes).")
            continue
            
        try:
            data = load_json_tolerant(filepath)
            turns = data.get("turns", [])
            
            session_turns = []
            session_tokens = 0
            
            for turn_entry in turns:
                turn_id = turn_entry.get("turn_id", 1)
                user_input = turn_entry.get("user_input", "")
                agent_output = turn_entry.get("agent_output", "")
                
                # Calculate tokens for this turn
                turn_tokens = estimate_tokens(user_input) + estimate_tokens(agent_output)
                session_tokens += turn_tokens
                
                session_turns.append({
                    "session_name": filename,
                    "turn": turn_id,
                    "user_input": user_input,
                    "agent_output": agent_output
                })
            
            if batch_start_sess is None:
                batch_start_sess = f"{sess_num:04d}"

            # Check if adding this session file's tokens exceeds 4k
            if current_batch_tokens + session_tokens > 4000 and current_batch_sessions:
                # Dump current batch
                batch_end_sess = f"{matched_files[[m[0] for m in matched_files].index(sess_num) - 1][0]:04d}"
                dump_batch(output_dir, batch_counter, batch_start_sess, batch_end_sess, current_batch_sessions, current_batch_tokens, timestamp_str)
                
                # Reset batch state
                batch_counter += 1
                current_batch_sessions = []
                current_batch_tokens = 0
                batch_start_sess = f"{sess_num:04d}"

            current_batch_sessions.extend(session_turns)
            current_batch_tokens += session_tokens
            
        except Exception as e:
            print(f"[ERROR] Failed to parse {filename}: {e}")

    # Dump any remaining sessions in the final batch
    if current_batch_sessions:
        batch_end_sess = f"{matched_files[-1][0]:04d}"
        dump_batch(output_dir, batch_counter, batch_start_sess, batch_end_sess, current_batch_sessions, current_batch_tokens, timestamp_str)

    print(f"[SUCCESS] All session telemetry processed and chunked successfully, General!")

def dump_batch(output_dir, batch_idx, start_sess, end_sess, sessions_data, total_tokens, timestamp_str):
    output_filename = f"session_batch_{batch_idx:02d}_{start_sess}_{end_sess}_{timestamp_str}.json"
    output_filepath = os.path.join(output_dir, output_filename)
    
    output_payload = {
        "metadata": {
            "batch_index": batch_idx,
            "from_session": start_sess,
            "to_session": end_sess,
            "total_turns": len(sessions_data),
            "estimated_total_tokens": total_tokens,
            "extracted_at": datetime.now().isoformat()
        },
        "sessions": sessions_data
    }

    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)
        
    print(f"[DUMP] Batch {batch_idx:02d} ({start_sess} to {end_sess}) saved with ~{total_tokens:,} tokens -> {output_filename}")

if __name__ == "__main__":
    extract_and_chunk_sessions()
