from flask import Blueprint, render_template

signinn_blueprint = Blueprint('signinn', __name__,
                        template_folder='templates',
                        static_folder='static')
@signinn_blueprint.route("/signin")
def signinn():
    return "signin/index.html"
    # return "module 1 churning"

