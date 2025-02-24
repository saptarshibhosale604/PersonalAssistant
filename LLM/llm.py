import google.generativeai as genai
import os
import time

debug01 = False

os.environ["API_KEY"] = 'AIzaSyBhxh85Q70JQ933qu6cEcbh4EuK1gtIbpI'
genai.configure(api_key=os.environ["API_KEY"])

# Model Configuration
model_config = {
  "temperature": 1,
  "top_p": 0.99,
  "top_k": 0,
  "max_output_tokens": 4096,
}


# System Instruction
instruction = """You are a linguistic expert who specializes in the English language.
I will give you text to check grammar of the sentence. Provide corrected sentence."""

# Message
message = "Hello, how is you"

model = genai.GenerativeModel('gemini-1.5-pro-latest', 
                              generation_config=model_config)
                              # system_instruction=instruction)
# response = model.generate_content(message)
# print(response.text)


chat = model.start_chat(history=[])
print("Initialize Gemini Chat")

inpMessage = ""

# ~ while(inpMessage != "close"):
  # ~ inpMessage = input('Message: ')
  # ~ response = chat.send_message(inpMessage)
  # ~ print("Response: " + response.text)
  # ~ print("***************************************************************************************")
  # ~ time.sleep(2)

def Main(userInput):
	response = chat.send_message(userInput)
	if(debug01): print("Response: " + response.text)
	return response.text
 
# ~ print(Main("Hey there"))

# # Output
# # 2 + 2 = 4

# response = chat.send_message("square of it")
# print(response.text)
# # Output
# # The square of 4 is 16

# response = chat.send_message("Add 4 to it")
# print(response.text)
# Output
# Adding 4 to 16 gives us 20.

# model = genai.GenerativeModel('gemini-1.5-pro-latest', 
#                               generation_config=model_config)
# response = model.generate_content("the most efficient way to remove duplicates of a list in python. Less verbose response.")
# print(response.text)


# model = genai.GenerativeModel('gemini-1.5-pro-latest')
# response = model.generate_content("Give ans in one word only. Who is the President of USA?")
# print(response.text)
