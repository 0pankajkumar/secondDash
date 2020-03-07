from flask import Flask, render_template

app = Flask(__name__, template_folder='templates',
                    static_folder='static')

@app.route("/signin")
def signin():
    # return render_template("signin/index.html")
    return "sign in churning"

