#Install docker in Rpi 5
#sudo apt install docker.io

# FROM ollama/ollama
# FROM alpine/ollama

# Ref /home/ssbrpi/ProjectRpi/Rpi/VibeTerminal/README.md
FROM alpine/ollama:0.23.2 


# Install Python and pip
RUN apk update && \
    apk add --no-cache \
        python3 \
        py3-pip

# Make "python" point to python3
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Verify installation
RUN python --version && pip3 --version

# Install Python 3.9 and pip

# RUN apt-get update && \
#     apt-get install -y software-properties-common && \
#     add-apt-repository ppa:deadsnakes/ppa && \
#     apt-get update && \
#     apt-get install -y python3.9 python3.9-venv python3.9-distutils python3.9-dev python3-pip && \
#     ln -sf /usr/bin/python3.9 /usr/bin/python 
#
# RUN python -m ensurepip --upgrade
    # ln -sf /usr/bin/python3.9 /usr/bin/python && \
    # ln -sf /usr/bin/pip3 /usr/bin/pip

    # apt-get install -y python3.9-venv python3.9-distutils \


# Install Python 3.8 and pip
# RUN apt-get update && \
#     apt-get install -y software-properties-common && \
#     add-apt-repository ppa:deadsnakes/ppa && \
#     apt-get update && \
#     apt-get install -y python3.8 python3.8-venv python3.8-distutils python3.8-dev python3-pip && \
#     ln -sf /usr/bin/python3.8 /usr/bin/python && \
#     ln -sf /usr/bin/pip3 /usr/bin/pip


# Save this image
# docker build -t ollama-python3 .

# docker build -t ollama-python39 .
# docker build -t alpine-ollama-python39 .
# docker build -t ollama-python38 .
# docker build -t ollama-python39 .                                                             
# docker run -it --rm ollama-python39 /bin/sh
