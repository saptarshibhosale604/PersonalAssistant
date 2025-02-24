
import json
import CmdsScripts.smartSpace as smartSpace
import CmdsScripts.basicCmds as basicCmds
import os


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the JSON file
json_file_path = os.path.join(script_dir, "intentList.json")



# Load commands from the JSON file
try:
	with open(json_file_path, "r") as file:
		intentListFile = json.load(file)
except FileNotFoundError:
	print(f"Error: JSON file not found at {json_file_path}")
	

# ~ with open('intentList.json') as f:
	# ~ intentListFile = json.load(f)
	
def RecognizeIntent(userInp, intentListFile):
	print("RecognizeIntent()")
	print("userInp:",userInp)
	for intent in intentListFile['intents']:
		# ~ print("intent:",intent)
		for keywords in intent['keywords']:
			# ~ print("keywords: #",keywords,"#")
			# ~ for keyword in keywords:
				# ~ print("keyword: *",keyword,"*")
				
			if keywords in userInp.lower():
				# ~ print("userInp:",userInp)
				# ~ print("got the intent")
				return intent['script'], intent['parameter']				
				# ~ return intent['script']
					
	# ~ return None, None
	return None, None


def InvokeScript(scriptName, parameterList, userInput):
	print("InvokeScript()")
	if scriptName == "smartSpace.py":
		smartSpace.Main(userInput) 
	elif scriptName == "basicCmd.py":
		return basicCmds.Main(parameterList) 
	else:
		print("Unknown intent.")

def Main(userInput):	
	
	# ~ userInput = "here also cpu usage here and there"
	scriptName, parameterList = RecognizeIntent(userInput, intentListFile)
	print("RecognizeIntent scriptName:", scriptName, " :parameterList: ", parameterList)
	if(scriptName is not None):
		return InvokeScript(scriptName, parameterList, userInput)
	else:
		print("General query")

# ~ Main()
