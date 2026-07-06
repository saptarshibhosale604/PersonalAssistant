#!/usr/bin/env python3
"""
userContext.py - Middleware script that processes user input, updates user context file,
and forwards input to PersonalAssistant.py.

Usage:
    python userContext.py "Your question here"
"""

import sys
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List

# userContextFile = "/root/ProjectRpi/Rpi/PersonalAssistant/UserContext/userContext.json"
userContextFile = "./UserContext/userContext.json"

def ExtractUserContextFromInput(userInput: str) -> Dict[str, Any]:
    """
    Extract potential user context information from user input.
    
    Args:
        userInput (str): Raw user input from user
        
    Returns:
        Dict[str, Any]: Extracted context information
    """
    context = {
        "timestamp": datetime.now().isoformat(),
        "input_length": len(userInput),
        "contains_question": bool(re.search(r'\?', userInput)),
        "keywords": re.findall(r'\b\w{4,}\b', userInput.lower()),
        "intent_categories": []
    }
    
    # Simple intent detection
    question_patterns = {
        'technical': ['python', 'code', 'script', 'data', 'snowflake', 'aws', 'docker'],
        'fitness': ['gym', 'workout', 'protein', 'exercise', 'cardio'],
        'travel': ['travel', 'flight', 'hotel', 'thailand', 'pune'],
        'personal': ['i am', 'my', 'me', 'schedule']
    }
    
    input_lower = userInput.lower()
    for category, keywords in question_patterns.items():
        if any(keyword in input_lower for keyword in keywords):
            context["intent_categories"].append(category)
    
    return context

def LoadExistingUserContext() -> Dict[str, Any]:
    """
    Load existing user context file or create empty structure.
    
    Args:
        userContextFile (str): Path to user context file
        
    Returns:
        Dict[str, Any]: Current user context data
    """
    global userContextFile
    if os.path.exists(userContextFile):
        try:
            with open(userContextFile, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load existing context file: {e}")
    
    # Initialize default user context structure
    return {
        "user_profile": {
            "interactions_count": 0,
            "last_interaction": None,
            "common_topics": [],
            "preferences": {}
        },
        "interaction_history": [],
        "session_info": {}
    }

def UpdateUserContext(userContextData: Dict[str, Any], newContext: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user context with new information from current input.
    
    Args:
        userContextData (Dict[str, Any]): Existing user context
        newContext (Dict[str, Any]): New context from current input
        
    Returns:
        Dict[str, Any]: Updated user context
    """
    profile = userContextData["user_profile"]
    
    # Update interaction count and timestamp
    profile["interactions_count"] += 1
    profile["last_interaction"] = newContext["timestamp"]
    
    # Update common topics
    if newContext["intent_categories"]:
        for category in newContext["intent_categories"]:
            if category not in profile["common_topics"]:
                profile["common_topics"].append(category)
    
    # Add to interaction history
    interaction_entry = {
        "timestamp": newContext["timestamp"],
        "input_length": newContext["input_length"],
        "intent_categories": newContext["intent_categories"][:3],  # Limit to top 3
        "keywords": newContext["keywords"][:5]  # Limit to top 5 keywords
    }
    userContextData["interaction_history"].insert(0, interaction_entry)
    
    # Keep only last 50 interactions
    if len(userContextData["interaction_history"]) > 50:
        userContextData["interaction_history"] = userContextData["interaction_history"][:50]
    
    return userContextData

def SaveUserContext(userContextData: Dict[str, Any]) -> bool:
    """
    Save updated user context to file.
    
    Args:
        userContextData (Dict[str, Any]): User context data to save
        userContextFile (str): Path to save user context file
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    global userContextFile
    try:
        with open(userContextFile, 'w', encoding='utf-8') as f:
            json.dump(userContextData, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving user context: {e}")
        return False

def PrintContextChanges(newContext: Dict[str, Any]) -> None:
    """
    Print what information was added/updated in user context file.
    
    Args:
        newContext (Dict[str, Any]): Newly extracted context
        userContextFile (str): User context file path
    """
    global userContextFile
    print("\n📝 User Context Updated Successfully!")
    print(f"📁 File: {userContextFile}")
    print(f"⏰ Timestamp: {newContext['timestamp']}")
    print(f"📊 Input Length: {newContext['input_length']} characters")
    
    if newContext["intent_categories"]:
        print(f"🎯 Detected Topics: {', '.join(newContext['intent_categories'])}")
    
    print(f"🔑 Keywords: {', '.join(newContext['keywords'][:3])}...")
    print("✅ Interaction logged in history\n")

def ForwardToPersonalAssistant(userInput: str) -> None:
    """
    Forward user input to PersonalAssistant.py script.
    
    Args:
        userInput (str): Original user input
    """
    # try:
        # # Check if PersonalAssistant.py exists
        # if not os.path.exists("PersonalAssistant.py"):
        #     print("⚠️  PersonalAssistant.py not found. Input ready for forwarding:")
        #     print(f"   '{userInput}'")
        #     return
        
        # Forward input via command line
    #     import subprocess
    #     result = subprocess.run(
    #         ["python", "PersonalAssistant.py", userInput],
    #         capture_output=True,
    #         text=True,
    #         timeout=30
    #     )
    #
    #     if result.returncode == 0:
    #         print("🤖 Personal Assistant Response:")
    #         print(result.stdout)
    #     else:
    #         print("⚠️  PersonalAssistant.py executed with warnings/errors:")
    #         print(result.stderr)
    #
    # except subprocess.TimeoutExpired:
    #     print("⚠️  PersonalAssistant.py timed out")
    # except FileNotFoundError:
    #     print("⚠️  python command not found. Install Python or check PATH")
    # except Exception as e:
    #     print(f"⚠️  Error forwarding to PersonalAssistant: {e}")

def Main(userInput: str) -> None:
    """
    Main processing function.
    
    Args:
        userInput (str): User input to process
    """
    if not userInput or not userInput.strip():
        print("❌ Error: No input provided")
        sys.exit(1)
    
    try:
        # Step 1: Extract context from input
        newContext = ExtractUserContextFromInput(userInput)
        
        # Step 2: Load existing context
        existingContext = LoadExistingUserContext()
        
        # Step 3: Update context
        updatedContext = UpdateUserContext(existingContext, newContext)
        
        # Step 4: Save context
        if SaveUserContext(updatedContext):
            PrintContextChanges(newContext)
        else:
            print("❌ Failed to save user context")
            sys.exit(1)
        
        # Step 5: Forward to Personal Assistant (non-blocking info only)
        # print("🔄 Forwarding input to PersonalAssistant.py...")
        # ForwardToPersonalAssistant(userInput)
        
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

# if __name__ == "__main__":
#     # Get user input from command line arguments
#     if len(sys.argv) > 1:
#         userInput = " ".join(sys.argv[1:])
#     else:
#         print("Usage: python userContext.py \"Your question here\"")
#         print("Example: python userContext.py \"How do I optimize my Snowflake queries?\"")
#         sys.exit(1)
#
#     Main(userInput)


