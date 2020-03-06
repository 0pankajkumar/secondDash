from flask import Blueprint, render_template

module1_blueprint = Blueprint('module1', __name__,
                        template_folder='templates',
                        static_folder='static')
@module1_blueprint.route("/signin")
def signin():
    return render_template("signin/index.html")
    # return "module 1 churning"
