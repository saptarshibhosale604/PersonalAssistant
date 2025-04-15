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

docker build -t personal_assistant .

docker run -it --rm -v /home/rpissb/Project:/root/Project/ personal_assistant /bin/sh 

python UI/cli.py

docker run -it --rm -v /home/ssblinux/ProjectLinux:/root/Project/ personal_assistant /bin/sh 

docker run -it --rm -v /home/ssblinux/ProjectLinux:/root/Project/ personal_assistant

