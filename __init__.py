from flask import Flask, render_template

app = Flask(__name__, template_folder='templates',
                    static_folder='static')

@app.route("/signin")
def signin():
    return render_template("loginPage.html")
    # return "sign in churning"

@app.route("/login")
def signin():
    # return render_template("signin/index.html")
    return "We have to make google login here"

