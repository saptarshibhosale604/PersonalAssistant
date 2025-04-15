FROM python:3.9

WORKDIR /App

COPY requirements.txt .
#Use of cache
RUN pip install -r requirements.txt
#NO use of cache
#RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

ENV PYTHONPATH="/App"

# CMD ["python", "UI/cli.py"]  # This will run cli.py as a module

# This is working
CMD ["python", "-m", "UI.cli"] 
