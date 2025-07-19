import subprocess
import re
from datetime import datetime


# Current timestamp in desired format (you can customize it)
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
def run_command(command):
    try:
        print(f"command: {command}")
        # Run the command and capture output
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        # result = subprocess.run(command, check=True, shell=True, text=True, capture_output=True)
        # result = subprocess.run(command, check=True, shell=True, text=True, capture_output=True)
        # result = subprocess.run(command, shell=True, check=True)
        # result = subprocess.run(command + ["2>&1"], shell=True, text=True)
        # print("Output:\n", result.stdout)
        return result.stdout
        # with open(output_file, "w") as f:
        #     f.write(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Run command Error:\n", e.stderr)
        return "error"
    except FileNotFoundError:
        print("The 'fabric' binary was not found at the specified path.")
        return "error"
def write_output_to_file(content, output_file):
    try:
        with open(output_file, "w") as f:
            f.write(content)
        print(f"Output written : {output_file}")
    except Exception as e:
        print(f"Failed to write content to file: {e}")
        return "error"

def main():

    # user_cmd = input("Enter the cmd [txt]: ") or "txt" # txt: feed txt input to fabric
    user_cmd = input("Enter the cmd [txt]: ") or "youtube" # txt: feed txt input to fabric
                                                 # file: feed file input to fabric
                                                 # youtube: feed youtube url
                                                 # help: show help
                                                 # helpPattern: show list of fabric patterns

    # # print(f"Using command: {user_cmd}")
    # # print(f"User input: {user_input}")
    # # print(f"Pattern name: {pattern_name}")
    # return 0


    if user_cmd == "txt":
        # command = ["/home/ssbrpi/Project/Fabric/fabric", user_input, "-sp", pattern_name, " | tee", output_file]
        user_input = input("Enter the input: ") or "hey there"
        pattern_name = input("Enter the pattern_name for -sp [test]: ") or "test"
        output_file = f"/home/ssbrpi/Project/Rpi/PersonalAssistant/Fabric/Data/{timestamp}-{pattern_name}.md"
        command = ["/home/ssbrpi/Project/Fabric/fabric", user_input, "-sp", pattern_name]
        result = run_command(command)
        if result != "error":
            write_output_to_file(result, output_file)
        return

    elif user_cmd == "youtube":
        youtube_url = input("Enter the YouTube URL: ") or "https://www.youtube.com/watch?v=example"
        # pattern_name = input("Enter the pattern_name for -sp [test]: ") or "test"
        # youtube_transcript_file = f"/home/ssbrpi/Project/Rpi/PersonalAssistant/Fabric/Data/{timestamp}-{pattern_name}.md"
        # output_file = f"/home/ssbrpi/Project/Rpi/PersonalAssistant/Fabric/Data/{timestamp}-{pattern_name}.md"
        # Get Youtube title 
        # commandYoutubeTitle = ["yt-dlp", "--get-title", youtube_url]
        commandYoutubeTitle = ["yt-dlp", "--user-agent", "Mozilla/5.0", "--get-title", youtube_url]
        # command = f"/home/ssbrpi/Project/Fabric/fabric '{youtube_url}' -sp {pattern_name} | tee {output_file}"
        # input("HumanInTheLoop01:")
        resultYoutubeTitle = run_command(commandYoutubeTitle)
        # resultYoutubeTitle = "testYoutubeTitle"

        if resultYoutubeTitle != "error":
            resultYoutubeTitle = resultYoutubeTitle.strip()  # Clean up the title
            # Clean the title to make it suitable for a filename
            clean_title = re.sub(r'[^a-zA-Z0-9 ]+', '', resultYoutubeTitle) # Remove special characters, keep only words and spaces
            words = clean_title.split() # Split into words
            youtubeTitle = "_".join(words[:5]) # Take the first 5 words
            youtubeTitle = f"{timestamp}_{youtubeTitle}" # Add timestamp prefix
            print(f"Youtube Title: {youtubeTitle}.md")

            # Get the youtube transcript
            commandYoutubeTrascript = ["/home/ssbrpi/Project/Fabric/fabric", "-y", youtube_url]
            # input("HumanInTheLoop02:")
            resultYoutubeTranscript = run_command(commandYoutubeTrascript)

            if resultYoutubeTranscript != "error":
                output_file = f"/home/ssbrpi/Project/Rpi/PersonalAssistant/Fabric/Data/YoutubeTranscript/{youtubeTitle}.md"
                write_output_to_file(resultYoutubeTranscript, output_file)

                # run fabric pattern cmd
                pattern_name = input("Enter the pattern_name for -sp [youtube_summary/helpPattern]: ") or "youtube_summary"
                if (pattern_name == "helpPattern"):
                    fabricPatternLists_file = "/home/ssbrpi/Project/Rpi/PersonalAssistant/Fabric/Data/Reference/fabricPatternsList.md"
                    with open(fabricPatternLists_file, "r") as f:
                        fabricPatternsList_data = f.read().strip()
                        print(f"Available fabric patterns:\n{fabricPatternsList_data}")
                    # pattern_name = input("Enter the pattern_name for -sp [test]: ") or "test"
                    pattern_name = input("Enter the pattern_name for -sp [youtube_summary]: ") or "youtube_summary"
                command = ["/home/ssbrpi/Project/Fabric/fabric", resultYoutubeTranscript, "-sp", pattern_name]

                # input("HumanInTheLoop03:")
                result = run_command(command)
                if result != "error":
                    output_file = f"/home/ssbrpi/Project/Rpi/PersonalAssistant/Fabric/Data/FabricOutput/{youtubeTitle}_{pattern_name}.md"
                    write_output_to_file(result, output_file)

                    return

    elif user_cmd == "file":
        pattern_name = input("Enter the pattern_name for -sp [test]: ") or "test"
        output_file = f"/home/ssbrpi/Project/Rpi/PersonalAssistant/Fabric/Data/{timestamp}-{pattern_name}.md"
        # read input from file _input.txt
        input_file = "/home/ssbrpi/Project/Rpi/PersonalAssistant/Fabric/Data/_input.txt"
        with open(input_file, "r") as f:
            input_file_data = f.read().strip()
            print(f"Using input from file: {input_file_data}")
            command = ["/home/ssbrpi/Project/Fabric/fabric", input_file_data, "-sp", pattern_name]
            result = run_command(command)
            if result != "error":
                write_output_to_file(result, output_file)
            return

    elif user_cmd == "helpPattern":
        fabricPatternLists_file = "/home/ssbrpi/Project/Rpi/PersonalAssistant/Fabric/Data/_fabricPatternsList.md"
        with open(fabricPatternLists_file, "r") as f:
            fabricPatternsList_data = f.read().strip()
            print(f"Available fabric patterns:\n{fabricPatternsList_data}")
        return

    elif user_cmd == "help":
        print("Available commands:")
        print("help: Show this help message")
        print("txt: Feed text input to fabric")
        print("youtube: Feed YouTube URL to fabric")
        print("file: Feed input from a file to fabric")
        print("helpPattern: Show list of fabric patterns")
        return

    else:
        print("Invalid command. Please use 'help' to see available commands.")
        return



if __name__ == "__main__":
    main()
    print("Script executed successfully.")
