import subprocess
import json
import os

def CallCmds(inputCmds):
    
	# Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the JSON file
    json_file_path = os.path.join(script_dir, "basicCmds.json")
    
    
    
    # Load commands from the JSON file
    try:
        with open(json_file_path, "r") as file:
            cmd_mapping = json.load(file)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return

	
    # Check if the inputCmds key exists in the mapping
    if inputCmds in cmd_mapping:
        command = cmd_mapping[inputCmds]
        try:
            # Execute the command and capture the output
            result = subprocess.check_output(command, shell=True, text=True)
            # ~ print(f"Output of {inputCmds}:")
            # ~ print(result)
            return result
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while executing {inputCmds}: {e}")
    else:
        print(f"Command for {inputCmds} not found in the JSON file.")


def Main(cmd):
    # Example: Get input from the user
    # ~ user_input = input("Enter the command keyword (e.g., ram, rom, cpu, screenshot): ").strip()
    # ~ user_input = "ram"
    return CallCmds(cmd)

# ~ Main("na")
