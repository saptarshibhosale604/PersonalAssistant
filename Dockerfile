FROM python:3.9

WORKDIR /App

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH="/App"

CMD ["python", "UI/cli.py"]  # This will run cli.py as a module
