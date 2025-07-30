# TECH USED
-Raspberry pi
-Docker containers
-Langchain framework
-Python
-SQL lite
- The agent is using local llm and calls the tools
	- But the model llama3.2:1b is not smart enough to use the tools
- The agent is working with google gemini llm with tools

# CLI // WORKING
docker build -t personal_assistant . 
docker rm ollamaLocal -f
docker run -d --rm -v ollama:/root/.ollama -v /home/ssbrpi/Project:/root/Project/ -p 11434:11434 --name ollamaLocal personal_assistant
docker exec -it ollamaLocal python /App/UI/cli.py

docker exec -it ollamaLocal /bin/sh


# WEB APP // WORKING
docker build -t personal_assistant .
docker rm ollamaLocal -f
docker run -d --rm -v ollama:/root/.ollama -v /home/ssbrpi/Project:/root/Project/ -p 11434:11434 -p 5001:5001 --name ollamaLocal personal_assistant
docker exec -it ollamaLocal python /App/UI/WebApp/app.py
 
docker exec -it ollamaLocal /bin/sh

# TESTING
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
ssh-add GitSSHAuthentication/key08

# INSIDE DOCKER CMDS
## sshpass
ssh -o BatchMode=yes -o StrictHostKeyChecking=no ssbrpi@172.17.0.1 pwd

ssh ssbrpi@172.17.0.1 pwd -p 'admin' // can't put password

apt update && apt install -y sshpass
sshpass -p 'admin' ssh -o StrictHostKeyChecking=no ssbrpi@172.17.0.1 pwd // this is working

sshpass -p 'admin' ssh -o StrictHostKeyChecking=no ssbrpi@172.17.0.1 /home/ssbrpi/Project/Fabric/fabric --version // this is taking so much time, and not outputing any output

## 
- for applying the alias
. /root/.profile


# APPEND // AFTER APPENDING REMOVE THIS 
- requirement.txt
pip3 install beautifulsoup4

- Dockerfile
playwright install-deps  

- Install ssh client (Debian/Ubuntu)
apt update && apt install -y openssh-client

# TEMP
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


# TODO 
- remove tool calling for local llm
- tool calling man in the loop not working, global mode, web app

- Need to start logging

done - work on mode context no for local llm
done - global mode not working for webapp
done - help function is not working here
Done - work on context of local llm
done - work on streaming input from global llm
done - work on streaming input form local llm
