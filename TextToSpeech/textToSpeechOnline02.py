# Import the required module for text 
# to speech conversion
from gtts import gTTS

# This module is imported so that we can 
# play the converted audio
import os
import subprocess
import threading

# The text that you want to convert to audio
# ~ mytext = 'Welcome to geeksforgeeks Joe!'
mytext = '........Hey SSB, This is your Personal Assistant. Ask me anything to do!'

# ~ mytext = 
""" The Raspberry Pi 5 is a significant upgrade and a really exciting development for the single-board computer world.  Here's my take, breaking it down into pros and cons:

**Pros:**

* **Significant performance boost:** The new processor is a game-changer, offering substantially improved performance over the Pi 4.  This opens doors for more demanding applications, smoother multitasking, and a generally more responsive experience.
* **Improved connectivity:**  Faster USB 3.2 ports, improved networking with faster Ethernet options, and the continued availability of wireless connectivity make it a versatile device for various projects.
* **Dual HDMI output:** This is a great addition for desktop use, allowing for dual monitor setups.
* **PoE support (with separate HAT):** While requiring an additional purchase, the official PoE HAT is well-integrated and provides a clean power solution.
* **Maintained affordability:** Despite the upgrades, the Raspberry Pi Foundation has managed to keep the price remarkably accessible.

**Cons:**

* **PoE HAT as a separate purchase:**  While convenient, some users might have preferred integrated PoE.
* **Software compatibility:**  While most software should be compatible, there might be some initial teething issues with certain applications as developers optimize for the new hardware.  This is typical with any new hardware release.
* **Potential for overheating:** With increased performance comes increased heat generation.  While the standard cooling solutions should be adequate for most uses, more demanding applications might require additional cooling.

**Overall:**

The Raspberry Pi 5 represents a major step forward and is a worthy successor to the Pi 4.  The performance improvements alone make it a compelling upgrade for many users. While there are a few minor drawbacks, the pros significantly outweigh the cons, making it an excellent choice for hobbyists, educators, and even professionals looking for a versatile and affordable computing platform.


What are you thinking of using a Raspberry Pi 5 for?  Knowing your use case might help me give you more specific advice.

"""

# Language in which you want to convert
language = 'en'

def Main02(inputVal):
	# Passing the text and language to the engine, 
	# here we have marked slow=False. Which tells 
	# the module that the converted audio should 
	# have a high speed
	print(inputVal)
	
	myobj = gTTS(text=inputVal, lang=language, slow=False)
	
	# Saving the converted audio in a mp3 file named
	# welcome 
	myobj.save("welcome.mp3")
	
	# Playing the converted file
	# ~ os.system("cvlc welcome.mp3")
	
	# Use the --play-and-exit flag to make VLC close automatically after playback
	subprocess.run(["cvlc", "--play-and-exit", "welcome.mp3"])

def text_to_speech(chunk):
    # Create a gTTS object for the chunk
    tts = gTTS(text=chunk, lang='en')
    # Save the audio to a temporary file
    tts.save("temp.mp3")
    # Play the audio file
    subprocess.run(["cvlc", "--play-and-exit", "temp.mp3"])
    # Optionally, remove the file after playing
    os.remove("temp.mp3")


def Main(inputVal):
    # Your large paragraph
    text = """This is a large paragraph that you want to convert to speech. 
    It contains multiple sentences and should be spoken in a natural manner. 
    The goal is to start speaking as soon as possible without waiting for the entire 
    text to be converted to audio. Let's break this down into smaller chunks 
    for better processing and playback."""

    # Split the text into chunks (you can adjust the size of the chunks)
    chunks = inputVal.split('. ')  # Split by sentences for this example

    for chunk in chunks:
        # Start the TTS conversion in a separate thread for each chunk
        tts_thread = threading.Thread(target=text_to_speech, args=(chunk,))
        tts_thread.start()
        
        # Wait for the TTS thread to finish before moving to the next chunk
        tts_thread.join()

# ~ Main(mytext)
# ~ main()

# Import the required module for text 
# ~ # to speech conversion
# ~ from gtts import gTTS

# ~ # Import pygame for playing the converted audio
# ~ import pygame

# ~ # The text that you want to convert to audio
# ~ mytext = 'Welcome to geeksforgeeks!'

# ~ # Language in which you want to convert
# ~ language = 'en'

# ~ # Passing the text and language to the engine, 
# ~ # here we have marked slow=False. Which tells 
# ~ # the module that the converted audio should 
# ~ # have a high speed
# ~ myobj = gTTS(text=mytext, lang=language, slow=False)

# ~ # Saving the converted audio in a mp3 file named
# ~ # welcome 
# ~ myobj.save("welcome.mp3")

# ~ # Initialize the mixer module
# ~ pygame.mixer.init()

# ~ # Load the mp3 file
# ~ pygame.mixer.music.load("welcome.mp3")

# ~ # Play the loaded mp3 file
# ~ pygame.mixer.music.play()
