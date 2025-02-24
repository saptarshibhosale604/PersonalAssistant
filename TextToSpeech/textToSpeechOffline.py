# ~ import pyttsx3

# ~ print("initialized")
# ~ # Initialize the text-to-speech engine
# ~ engine = pyttsx3.init()

# ~ # Set the voice (optional)
# ~ voices = engine.getProperty('voices')
# ~ engine.setProperty('voice', voices[1].id)  # Change index for different voices

# ~ # Text to be spoken
# ~ text = "Hello, world! This is a text-to-speech example."

# ~ print("text", text)
# ~ # Speak the text
# ~ engine.say(text)
# ~ engine.runAndWait()
# ~ print("done")



# ~ import pyttsx3

# ~ try:
    # ~ engine = pyttsx3.init('espeak')  # Specify the engine as 'espeak'
    # ~ engine.say("Hello, world!, this is me. What is your name. Whats your problem")
    # ~ engine.runAndWait()
# ~ except RuntimeError as e:
    # ~ print(f"Error: {e}")
    # ~ print("Please install eSpeak or eSpeak-ng.")
    
    
# ~ import pyttsx3

# ~ engine = pyttsx3.init() 
# ~ engine.say("Test speech.") 
# ~ engine.runAndWait()

# ~ from espeak import espeak

# ~ espeak.synth("Hello Instructables!")
import os

# ~ cmd = "espeak -v en-us -s 120 -a 150 -p 10 'This is a test with adjusted speed, volume, and voice.'"
cmd = "espeak -v en-us -s 120 -a 150 -p 10 'Hey SSB, This is your Personal Assistant. Ask me anything to do'"
output = os.popen(cmd).read()

