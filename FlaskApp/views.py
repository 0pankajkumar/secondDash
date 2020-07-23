from flask import Flask, render_template

# app = Flask(__name__, static_url_path='',
# 				  static_folder='static',
# 				  template_folder='templates')

from FlaskApp import FlaskApp as app
@app.route("/")
def hello():
    return "Working fine hel O"
