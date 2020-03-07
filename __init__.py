from flask import Flask, render_template

app = Flask(__name__, template_folder='build',
                    static_folder='build')

@app.route("/signin")
def signin():
    return render_template("loginPage.html")
    # return "sign in churning"

@app.route("/login")
def login():
    # return render_template("signin/index.html")
    return "We have to make google login here"

