# TECH USED
- Raspberry pi
- Docker containers
- Langchain framework
- Python
- SQL lite

# Features
- LLM model
    - Chatgpt, with tools
    - Google Gemini, with tools
    - Mistral AI, with tools
    - Local LLM, no tools
- can specify which tools to be interrupted and which tools dont need human in the loop
- context remembering
- Multi line user input
- The modes are saved in ROM


# CLI // WORKING
cli
refreshDir && pythonCli 

docker build -t personal_assistant . 

sudo docker rm ollamaLocal -f && \
sudo docker run -d --rm -v ollama:/root/.ollama -v /home/ssbrpi/ProjectRpi:/root/ProjectRpi/ -p 11434:11434 --name ollamaLocal personal_assistant && \
sudo docker exec -it ollamaLocal sh -c '. /root/.profile; exec sh -l'


docker rm ollamaLocal -f
docker run -d --rm -v ollama:/root/.ollama -v /home/ssbrpi/ProjectRpi:/root/ProjectRpi/ -p 11434:11434 --name ollamaLocal personal_assistant
docker exec -it ollamaLocal /bin/sh

docker exec -it ollamaLocal python /App/UI/cli.py

. /root/.profile # for applying the alias
refresh
python /App/UI/cli.py

. /root/.profile # for applying the alias
refresh && python /App/UI/cli.py
<!-- refresh && python /App/Langchain/agent02.py -->
<!-- refresh && python /App/Langchain/agent.py -->

what is the weather in PUN?

cat /root/ProjectRpi/Rpi/PersonalAssistant/Log/log.log

/App # pip install --upgrade langchain

docker run -d --rm -v ollama:/root/.ollama -v /home/ssbrpi/ProjectRpi:/root/ProjectRpi/ -p 11434:11434 --name ollamaLocal personal_assistant

docker exec -it ollamaLocal /bin/sh . /root/.profile
# WEB APP // WORKING
docker build -t personal_assistant .
docker rm ollamaLocal -f
docker run -d --rm -v ollama:/root/.ollama -v /home/ssbrpi/Project:/root/Project/ -p 11434:11434 -p 5001:5001 --name ollamaLocal personal_assistant
docker exec -it ollamaLocal python /App/UI/WebApp/app.py
 

# TESTING
refreshDir && cd . && python test04.py

docker build -t personal_assistant .
docker rm ollamaLocal -f
docker run -d --rm -v ollama:/root/.ollama -v /home/ssbrpi/Project:/root/Project/ -p 11434:11434 --name ollamaLocal personal_assistant
docker exec -it ollamaLocal python /App/Fabric/script.py ai

docker exec -it ollamaLocal python /App/Fabric/script.py hii there
docker exec -it ollamaLocal python /App/Fabric/script.py pattern hii 

docker exec -it ollamaLocal /bin/sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=no ssbrpi@172.17.0.1 pwd
/bin/sh: 3: ssh: not found

# SSH 
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/GitAuthentication/PersonalAssistant_01/id_rsa

# INSIDE DOCKER CMDS
## sshpass
ssh -o BatchMode=yes -o StrictHostKeyChecking=no ssbrpi@172.17.0.1 pwd

ssh ssbrpi@172.17.0.1 pwd -p 'admin' // can't put password

ssh ssbrpi@172.17.0.1 java -version

ssh ssbrpi@172.17.0.1 "java -version; pwd; echo 'hiii'"


create a sample csv file of customers
create a sample csv file of customers table with 3 fields and 3 rows
create a csv file for mobile phones with 10 rows and 4 columns

<!-- result: {'success': False, 'message': "Execution error: name 'workingDirectoryRpi' is not defined"} -->
'/tmp/pyspark_jobs/pyspark_script.py'

apt update && apt install -y sshpass
sshpass -p 'admin' ssh -o StrictHostKeyChecking=no ssbrpi@172.17.0.1 pwd // this is working

sshpass -p 'admin' ssh -o StrictHostKeyChecking=no ssbrpi@172.17.0.1 /home/ssbrpi/Project/Fabric/fabric --version // this is taking so much time, and not outputing any output

# install
apk add openssh

# APPEND // AFTER APPENDING REMOVE THIS 
- requirement.txt
pip3 install beautifulsoup4

- Dockerfile
playwright install-deps  
# Install Rust (stable)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y // done
ENV PATH="/root/.cargo/bin:${PATH}" // done

pip install -U duckduckgo-search // done

- Install ssh client (Debian/Ubuntu)
apt update && apt install -y openssh-client

# TEMP


k
vcgencmd pmic_read_adc EXT5V_V
vcgencmd measure_clock arm
vcgencmd measure_temp
vcgencmd measure_volts core
watch


/home/ssbrpi/ProjectRpi/Rpi/PersonalAssistant/PySpark

docker build -t personal_assistant . 

sudo docker rm ollamaLocal -f && \
sudo docker run -d --rm -v ollama:/root/.ollama -v /home/ssbrpi/ProjectRpi:/root/ProjectRpi/ -p 11434:11434 --name ollamaLocal personal_assistant && \
sudo docker exec -it ollamaLocal sh -c '. /root/.profile; exec sh -l'

sudo docker exec -it ollamaLocal sh -c '. /root/ProjectRpi/Rpi/PersonalAssistant/Bashrc/.profile; exec sh -l'

sudo docker exec -it ollamaLocal /bin/sh  

. /root/.profile # for applying the alias
refresh && python /App/UI/cli.py

pip install --upgrade langchain

docker exec -it ollamaLocal /bin/sh . /root/.profile // not wokring
docker exec -it ollamaLocal /bin/sh 
. /root/.profile 
refresh
python /App/UI/cli.py

docker build -t personal_assistant .  && /
docker rm ollamaLocal -f && \
docker run -d --rm -v ollama:/root/.ollama -v /home/ssbrpi/Project:/root/Project/ -p 11434:11434 --name ollamaLocal personal_assistant && \
docker exec -it ollamaLocal /bin/sh 

# Make session
- open my-session
nvim -S my-session.vim 
nvim -S
- // Not workin
:source my-session.vim 
- Create my-session
:mksession my-session.vim 
:mksession
- Overwrite my-session
:mksession! my-session.vim 
mksession!
- Save current files and quit nvim
:qa
- put current line to cmd line
:<C-r><C-l> 

# Windows
## not working
python .\ui\cli.py  
python .\toolsAskGPT.py (Get-Clipboard)
python .\toolsAskGPT.py (Get-Content  -Raw)
## working
python -m UI.cli


## Virtual env, venv
ssbrpi06@raspberrypi:~/PersonalAssistant $ python3 -m venv venv
ssbrpi06@raspberrypi:~/PersonalAssistant $ source venv/bin/activate
source venv/bin/activate
python -m UI.cli
export OPENAI_API_KEY="sk-proj-your-actual-api-key-here"
export OPENAI_API_KEY=""
pip install langchain langchain_community langchain_ollama langchain_openai langchain_google_genai langchain_huggingface langchain_mistralai

# Cloud API keys used by model modes
export GOOGLE_API_KEY="your-google-key"
export MISTRAL_API_KEY="your-mistral-key"


# lm studio:
- google / gemma-4-e4b gemma4 7.9B
Gemma4, effective 4B version. Supports image input, reasoning, and tool calling.
- Qwen3.5 9B Q4 6.5gb
- https://lmstudio.ai/models/google/gemma-4-e4b 6.3gb
- https://huggingface.co/lmstudio-community/Qwen3.5-4B-GGUF 3.3gb

# Gemini models (tested 2026-10-05 via Testing/testGemini.py)
- Run: `python Testing/testGemini.py` (needs GOOGLE_API_KEY, set in ~/.bashrc)
## Working (9)
- gemini-3.5-flash-lite          1.0s  fastest
- gemini-3.1-flash-lite          1.2s
- gemini-3-flash-preview         1.4s
- gemini-3.1-flash-lite-preview  1.6s
- gemini-flash-lite-latest       1.9s
- gemini-robotics-er-2-preview   1.9s
- gemini-3.6-flash               2.9s  current default in agent.py / LLM/llm.py
- gemini-flash-latest            5.0s
- gemini-3.5-flash              12.5s  sometimes 503 (high demand)
## Not working (32)
- 503 high demand, retry later: gemini-3.7-flash, gemini-3.8-flash
- 429 quota exceeded: gemini-pro-latest, gemini-3.1-pro-preview(-customtools), *-image models, gemini-omni-*, gemini-2.5-computer-use-preview, gemini-2.5-pro-preview-tts
- 404 retired / not found: all 2.5 / 2.0 / 1.5 models, gemini-3-pro(-preview), gemini-3-flash, gemini-3.5-pro, gemini-1.5-pro-latest
- Empty reply (audio models, not for text chat): *-tts, gemini-3.5-transcribe
- Note: thinking models need max_tokens >= ~1024, or they return an empty reply
## Comparison & recommendation (plan -> review -> execute)
- Test: tool calling (single / 3 parallel / reasoning) -> all 9 working models passed
- Test: system prompt "plan first, no tools until 'execute'", task = backup finance.csv with timestamp, keep 5 newest, cron Sun 9pm

| Model | Plan time | Tools before execute? | Plan quality | Execution |
|---|---|---|---|---|
| gemini-3.6-flash | 10.0s | no | best: full script + test step + no-duplicate cron; 1 bash bug (empty else) | ran plan in 1 shell call |
| gemini-3.5-flash-lite | 2.4s | no | good: full script + test step + risks; cron appended without dedupe | ran plan in 1 shell call |
| gemini-3.1-flash-lite | 2.1s | no | vague: no exact script, /home/<user> placeholder | only ran mkdir |
| gemini-3-flash-preview | 6.3s | no | exact command per step | followed step-by-step (4 calls), but made up /home/pi path |
| gemini-flash-latest | - | - | 503 high demand | - |

- Use cases
    - gemini-3.6-flash: default; planning + complex tool tasks
    - gemini-3.5-flash-lite: fast mode; quick Q&A, simple tools (~1-2s)
    - gemini-3.1-flash-lite: avoid, plans too vague to review
    - *-preview / *-latest / robotics-er: avoid, get retired / silently change / specialised (robotics, 131k context)
    - gemini-3.5-flash: avoid, slow (10-23s) + 503s
- Preferred: gemini-3.6-flash (mode-llm globalGemini01, now the default in UI/config.py); fallback gemini-3.5-flash-lite (mode-llm globalGemini02)
- Groq modes added: globalGroq01 -> openai/gpt-oss-120b, globalGroq02 -> qwen/qwen3.8-27b (requires GROQ_API_KEY, uses https://api.groq.com/openai/v1 OpenAI-compatible endpoint)
- OpenRouter modes added: globalOpenRouter01 -> nvidia/nemotron-3-ultra:free, globalOpenRouter02 -> nvidia/nemotron-3.5-lightning:free (requires OPENROUTER_API_KEY, uses https://openrouter.ai/api/v1 OpenAI-compatible endpoint)
- Caveat: even 3.6-flash wrote a bash syntax error, 3-flash-preview made up a path -> always review plan + keep HITL approval

# DONE
- mode multi input true is not working
- remove tool calling for local llm
- Need to start logging
- work on mode context no for local llm
- remember last help options
- global mode not working for webapp
- help function is not working here
- work on context of local llm
- work on streaming input from global llm
- work on streaming input form local llm
- A, Improve, refresh .profile auto load with the docker exec
- A, BUG, if the agent want to go again in the second time for searching the answer it's giving this error:
    - print(token.content_blocks[0]["text"], end="", flush=True)
    - Cause may be this time its not content_block[0] 
    - Eg. which are the top 5 smallest file / directory in my current working directory except current working directory?
- B, BUG, list of tools != number of human approvals
    - ValueError: Number of human decisions (1) does not match number of hanging tool ca
- B, BUG, randomly tocket.content_blocks[0] dont have text value in it
    - print(token.content_blocks[0]["text"], end="", flush=True) ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^ KeyError: 'text'
    - Print the whole block with pprint 
- C, Improve, The log printing like this, logging.print this prints timestamp in the console pring 
    2025-12-05 05:49:12,491 - DEBUG - Initialized assistant.py
    2025-12-05 05:49:12,492 - INFO - WelcomeUser()
    - I want only text visible in print, no timestamp values
- C, Improve, log saving with timestamp + log
- C, Improve, log saving with output
- B, Improve, Turn on / off tools in mode cli
    - Tools manager
- A, <leader>sts error
    -    Error  11:51:29 msg_show.emsg E5108: Error executing lua: vim/_editor.lua:0: nvim_exec2(), line 1: Vim(wall):E141: No file name for buffer 670
    stack traceback:
	[C]: in function 'nvim_exec2'
	vim/_editor.lua: in function 'cmd'
	/home/ssbrpi/Dotfiles/Nvim/init.lua:660: in function </home/ssbrpi/Dotfiles/Nvim/init.lua:657>
- B, Improve, gp, git push
- B, Improve, gp, add git authentication
    - crate a sh file with git authentication cmds
- B, Imorve, mode reset : reset modes to default
- A, bug, streaming is not wokring in local-4b and stream mode on

# TODO 
- a, bug, understand the current project and summarise it in summary.md
    is not working with globalGemini02 try with 01, its just not giving any output
    might be token variable DEFAULT-MAX-TOKEN
- a, bug, toolShell giving error if calls multiple cmds
    - temp fix: run one cmd at a time in user input
- B, improve, plan-first mode (agent plans, waits for "execute") in agent.py system prompt
- A, improve, clean the code
- B, improve, change the mode-vars from true, false to on, off
- A, bug, mode context no not working
- A, Bug, with qwen3.5:4b as llm model agent is not giving any output
    - create a smallest code to check this llm model, agent
- B, Improve, start next thread from the userInput mode
- B, Bug, Sandbox not working as expected
- B, BUG, gemini llm integration is not working
- C, Improve, The role set for the local llm is hullucinating toooo much, 
    - Need some prompt engg
    - {"role": "system", "content": "You are an assistance like a JARVIS from Iron Man. Your name is RPI. Your master name is SSB"},
- B, Immprove, Completer + mode_config_initialization
- B, Improve, UserContext
- C, Bug, OUTPUT_FILE = f"{date_str}_output.csv" not able to output the ifle in this format
    - Cause file name is declared in the .py script which is generated by llm 
- B, Improve, Multiple cli instances are reading the same mode file
    - So not able to have 1 instance with mode llm local AND other with mode llm global
- B, Improve, Need context on the file/ dir name when calling the toolShell
- TODO B backup the current finance.csv file as <timestamp>_finance.csv.bak
- B, Bug, Sandbox not working as expected
- B, Bug, Logs, Windows, sometime logs are not being saved, due to emojies i guess. giving error while saving the logs
- A, improve /plan and /implement mode
    - change the TOOL_INTERRUPT_POLICY = {} vars to TRUE
    - it should only work for specific /plan + model combination
    - Also /plan => add JUST PLAN, DO NOT IMPLEMENT ANYTHING. += user input
- A, improve /os variable 
    - add  You are using POWERSHELL CMD. += user input
- B, improve, logs should include input output tokens, model used
- B, improve, /resume to resume any session/ thread with new / same model
- C, improve. /exit to exit
- B, improve, .env file/system
- B, bug, input("Is this approved or rejected?(Default: approved): ") also add rejected path
- B, improve, show tool arg in json beutifier
- A, bug, /update is not working, mode update is working after the OS mode addition