from flask import Flask, render_template

from signin.signin import signin_blueprint

application = Flask(__name__, template_folder='templates',
                    static_folder='static')

application.register_blueprint(signin_blueprint)
