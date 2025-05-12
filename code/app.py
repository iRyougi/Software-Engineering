from flask import Flask 

app = Flask( name ) 
@app.route("/")
def hello():
    return "Hello, World!"
