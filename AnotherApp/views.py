from FlaskApp import app
@app.route("/another")
def hello():
    return "Rocking another"
