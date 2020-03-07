from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

# For google login
from google.oauth2 import id_token
from google.auth.transport import requests

from FlaskApp.old_secondDash.user import User
# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["dolphinDB"]
# DB links for ApprovedUsers collection
collection2 = database["ApprovedUsers"]
# From new dup
collection4 = database["jobPostingWiseDB"]


app = Flask(__name__, template_folder='client/build',
                    static_folder='client/build')


'''
--------------------------------------
$$$$
$   $
$$$$
$ $
$  $
$   $
--------------------------------------
'''

@app.route("/index")
@login_required
def index():
    # return render_template("loginPage.html")
    return "successfully signin"


@app.route("/signin")
def signin():
    return render_template("loginPage.html")
    # return "sign in churning"


@app.route("/login")
def login():
	# Find out what URL to hit for Google login
	google_provider_cfg = get_google_provider_cfg()
	authorization_endpoint = google_provider_cfg["authorization_endpoint"]

	# Use library to construct the request for login and provide
	# scopes that let you retrieve user's profile from Google
	request_uri = client.prepare_request_uri(
		authorization_endpoint,
		redirect_uri=request.base_url + "/callback",
		scope=["openid", "email"],
	)
	return redirect(request_uri)


@app.route("/login/callback")
def callback():
	# Get authorization code Google sent back to you
	code = request.args.get("code")

	# Find out what URL to hit to get tokens that allow you to ask for
	# things on behalf of a user
	google_provider_cfg = get_google_provider_cfg()
	token_endpoint = google_provider_cfg["token_endpoint"]

	# Prepare and send request to get tokens! Yay tokens!
	token_url, headers, body = client.prepare_token_request(
		token_endpoint,
		authorization_response=request.url,
		redirect_url=request.base_url,
		code=code,
	)
	token_response = requests.post(
		token_url,
		headers=headers,
		data=body,
		auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
	)

	# Parse the tokens!
	client.parse_request_body_response(json.dumps(token_response.json()))

	# Now that we have tokens (yay) let's find and hit URL
	# from Google that gives you user's profile information,
	# including their Google Profile Image and Email
	userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
	uri, headers, body = client.add_token(userinfo_endpoint)
	userinfo_response = requests.get(uri, headers=headers, data=body)

	# We want to make sure their email is verified.
	# The user authenticated with Google, authorized our
	# app, and now we've verified their email through Google!
	if userinfo_response.json().get("email_verified"):
		unique_id = userinfo_response.json()["sub"]
		users_email = userinfo_response.json()["email"]
	else:
		return "User email not available or not verified by Google.", 400

	# Create a user in our db with the information provided
	# by Google
	

	# Create a user in our db with the information provided
	# by Google
	user = User(
		id_=users_email
	)

	# Doesn't exist? Add to database of suspicious people
	if not User.get(users_email):
		User.suspicious(users_email)
		print("User doesn't exist")

	# Begin user session by logging the user in
	login_user(user)

	# Send user back to homepage
	return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for("index"))


def get_google_provider_cfg():
	return requests.get(GOOGLE_DISCOVERY_URL).json()
