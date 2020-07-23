from FlaskApp import app
from FlaskApp.FlaskApp.modules.amodule import insidemodule

@app.route("/")
def hello():
    return "Working fine hel O"

@app.route("/amodule")
def amodule():
    return amodule()
