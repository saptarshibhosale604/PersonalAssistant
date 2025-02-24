
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def communicate():
    response = requests.get("http://service_a:5000")  # Using service name
    return f"Service B received: {response.text}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
