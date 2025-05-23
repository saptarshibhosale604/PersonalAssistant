// //

ls index.html
docker build -t personal_assistant .
docker rm ollamaLocal -f
docker run -d --rm -v ollama:/root/.ollama -v /home/rpissb/Project:/root/Project/ -p 11434:11434 -p 5001:5001 --name ollamaLocal personal_assistant
docker exec -it ollamaLocal python /App/UI/WebApp/app.py
 
docker exec -it ollamaLocal python /App/UI/WebApp/app.py

//

-Tech Used:
	+Raspberry pi
	+Docker containers
	+Langchain framework
	+Python
	+SQL lite
-Cmd list:
	alias dockerBuild='docker build -t personal_assistant .'
	alias dockerRun='docker run -it personal_assistant'
	docker run -it --rm personal_assistant /bin/sh
	docker run -it -v /home/ec2-user/Test:/Data --rm personal_assistant /bin/sh
	docker run -it -v /home/ec2-user/Project:/root/Project/ --rm personal_assistant /bin/sh

//
working
ls cli
docker build -t personal_assistant .
docker rm ollamaLocal -f
docker run -d --rm -v ollama:/root/.ollama -v /home/rpissb/Project:/root/Project/ -p 11434:11434 --name ollamaLocal personal_assistant
docker exec -it ollamaLocal python /App/UI/cli.py

// SSH 
eval "$(ssh-agent -s)"
ssh-add GitSSHAuthentication/key05

docker build -t personal_assistant .

docker run -it --rm -v /home/rpissb/Project:/root/Project/ personal_assistant /bin/sh 

python UI/cli.py

docker run -it --rm -v /home/ssblinux/ProjectLinux:/root/Project/ personal_assistant /bin/sh 

docker run -it --rm -v /home/ssblinux/ProjectLinux:/root/Project/ personal_assistant

docker run -it --rm -v /home/rpissb/Project:/root/Project/ -p 5001:5001 personal_assistant python /App/UI/WebApp/app.py

// Final

docker build -t personal_assistant .

docker run -it --rm -v /home/rpissb/Project:/root/Project/ personal_assistant


// working 02
docker build -t personal_assistant .

docker run -it --rm -v /home/rpissb/Project:/root/Project/ --entrypoint python personal_assistant /App/UI/cli.py

//
ls cli
docker build -t personal_assistant .
docker rm ollama07 -f
docker run -d --rm -v ollama:/root/.ollama -v /home/rpissb/Project:/root/Project/ -p 11434:11434 --name ollama07 personal_assistant
docker exec -it ollama07 python /App/UI/cli.py


//

ls test.py
docker build -t personal_assistant .
docker rm ollama07 -f
docker run -d --rm -v ollama:/root/.ollama -v /home/rpissb/Project:/root/Project/ -p 11434:11434 --name ollama07 personal_assistant
docker exec -it ollama07 python /App/test.py

//

ls agent.py
docker build -t personal_assistant .
docker rm ollama07 -f
docker run -d --rm -v ollama:/root/.ollama -v /home/rpissb/Project:/root/Project/ -p 11434:11434 --name ollama07 personal_assistant
docker exec -it ollama07 python /App/Langchain/agent.py
 
 
 //
ls custom
docker build -t personal_assistant .
docker rm ollama07 -f
docker run -d --rm -v ollama:/root/.ollama -v /home/rpissb/Project:/root/Project/ -p 11434:11434 --name ollama07 personal_assistant
docker exec -it ollama07 python /App/getFunctionsList.py

TODO
// work on mode context no for local llm
// global mode not working for webapp

Done // work on context of local llm
done // work on streaming input from global llm
done // work on streaming input form local llm