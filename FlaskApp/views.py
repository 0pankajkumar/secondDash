from FlaskApp import app
from FlaskApp.FlaskApp.modules import amodule

@app.route("/")
def hello():
    return "Working fine hel O"

@app.route("/amodule")
def hello():
    return amodule()
