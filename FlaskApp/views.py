from flask import render_template, url_for, flash, redirect
from FlaskApp import papp

@papp.route("/")
@papp.route("/home")
def home():
    return "Modularixation is not that bad, trust me"