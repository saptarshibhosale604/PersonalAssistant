#!/usr/bin/env bash

# Start the ssh agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/GitAuthentication/PersonalAssistant_01/id_rsa

# Test connection
ssh -T git@github.com

