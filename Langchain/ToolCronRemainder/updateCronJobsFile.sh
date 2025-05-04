#!/bin/bash

# Copy the cron file into the container
cp /root/Project/Rpi/PersonalAssistant/Langchain/ToolCronRemainder/Data/myCronJobs /etc/cron.d/mycron

# Give execution rights on the cron job
chmod 0644 /etc/cron.d/mycron

# Apply the cron job to the root user's crontab
crontab /etc/cron.d/mycron
