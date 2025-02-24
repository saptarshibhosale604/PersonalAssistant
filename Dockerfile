# Use an official Python runtime as a parent image
FROM python

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
#COPY requirements.txt .

# Copy the application code
COPY . /app

# Install the dependencies
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt


# Run the command to start the application when the container launches
CMD ["python3", "app.py"]
