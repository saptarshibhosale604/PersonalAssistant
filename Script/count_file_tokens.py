"""
Module: count_file_tokens.py
Description: Scans Log/UserContextRawInput/ for the latest generated session telemetry JSON file,
analyzes character and word counts, and applies Option C universal ratio heuristics
(approx. 4 characters per token) to estimate the total token count.
"""

import os
import glob

def count_tokens_option_c():
    output_dir = "Log/UserContextRawInput"
    
    if not os.path.exists(output_dir):
        print(f"[ERROR] Directory '{output_dir}' does not exist, General!")
        return

    # Find the latest JSON file in the UserContextRawInput directory
    json_files = glob.glob(os.path.join(output_dir, "session_*.json"))
    if not json_files:
        print(f"[WARNING] No session telemetry JSON files found in '{output_dir}'.")
        return

    # Get the most recently modified file
    latest_file = max(json_files, key=os.path.getmtime)
    
    print(f"[TACTICAL] Analyzing file: {latest_file}")

    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")
        return

    char_count = len(content)
    word_count = len(content.split())
    
    # Option C: Universal ratio heuristic (approx. 4 characters per token for JSON/English text)
    estimated_tokens_char_ratio = round(char_count / 4.0)
    
    # Alternative heuristic: word count multiplier (approx. 1.3 tokens per word)
    estimated_tokens_word_ratio = round(word_count * 1.3)

    print("\n==========================================")
    print("       FILE TOKEN COUNT ANALYSIS (Option C)")
    print("==========================================")
    print(f"File Path                 : {latest_file}")
    print(f"Total Characters          : {char_count:,}")
    print(f"Total Words               : {word_count:,}")
    print(f"Estimated Tokens (Char/4) : {estimated_tokens_char_ratio:,}")
    print(f"Estimated Tokens (Word*1.3): {estimated_tokens_word_ratio:,}")
    print("==========================================")
    print("[SUCCESS] Analysis complete, General!")

if __name__ == "__main__":
    count_tokens_option_c()
