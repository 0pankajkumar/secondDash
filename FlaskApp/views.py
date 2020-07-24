from flask import render_template, url_for, flash, redirect
from FlaskApp.FlaskApp import app

@app.route("/")
@app.route("/home")
def home():
    return "Modularixation is not that bad, trust me"