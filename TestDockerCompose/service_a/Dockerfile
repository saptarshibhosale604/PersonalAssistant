
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app1.py .

CMD ["python", "app1.py"]
