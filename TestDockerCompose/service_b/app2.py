
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def communicate():
    print("here i am before")
    response = requests.get("http://service_a:5000")  # Using service name
    return f"Service B received: {response.text}"

@app.route('/otherPage')
def other_page():
    return "This is the other page"

@app.route('/arg')
def Arg():
    var1 = request.args.get('var1', 'default_value_1')
    var2 = request.args.get('var2', 'default_value_2')
    return f"var1: {var1}, var2: {var2}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
