# FROM python:3.9

# WORKDIR /App

FROM ollama-python39 

# Set the working directory in the container
WORKDIR /App

# Copy the requirements file into the container
# COPY requirements.txt .

# Install the dependencies
# RUN pip install -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install requests
# Copy the rest of your application code into the container
# COPY . .


## ## For python app
COPY requirements.txt .
#Use of cache
RUN pip3.9 install -r requirements.txt
#NO use of cache
#RUN pip install --no-cache-dir -r requirements.txt 


## ## For Cron service
# Install necessary packages
RUN apt-get update && apt-get install -y cron

# Copy the cron file into the container
COPY Langchain/ToolCronRemainder/Data/myCronJobs /etc/cron.d/mycron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/mycron

# Apply the cron job to the root user's crontab
RUN crontab /etc/cron.d/mycron

# Create a directory for notification logs
RUN mkdir -p /var/log

# Initialize the file
RUN echo "Initialized notification log file" > /var/log/notify.log

# Change timezone to India
RUN ln -sf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime

COPY . .

ENV PYTHONPATH="/App"

# CMD ["python", "UI/cli.py"]  # This will run cli.py as a module

# This is working
# CMD ["python", "-m", "UI.cli"] 


CMD ["serve"]

# Command to run your application
# CMD ["python", "app.py"]
# CMD ["/bin/sh"]

#CMD ["python", "UI/cli.py"]  # This will run cli.py as a module
# Start the cron service in the foreground
#CMD ["cron", "-f"]
