from flask import Blueprint, render_template

signin_blueprint = Blueprint('signin', __name__,
                        template_folder='templates',
                        static_folder='static')
@signin_blueprint.route("/signin")
def signin():
    return render_template("signin/index.html")
    # return "module 1 churning"
