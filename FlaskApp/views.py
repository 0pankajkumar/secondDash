from FlaskApp import app

# Imports modules
from FlaskApp.FlaskApp.modules.user import User
from FlaskApp.FlaskApp.modules.update import updateMongo

# Clearing caches
@app.after_request
def after_request(response):
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	response.headers["Expires"] = 0
	response.headers["Pragma"] = "no-cache"
	return response

@app.route('/privacy', methods=['GET'])
def privacy():
	return render_template("privacyPolicy.html")


@app.route("/")
def hello():
    return "Working fine hel O"

@app.route("/amodule")
def amodulefunction():
    return insidemodule()
