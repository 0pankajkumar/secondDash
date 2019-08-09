import os
from flask import Flask,redirect

app = Flask(__name__)

# @app.route('/')
# def hello():
#     return redirect("https://accounts.google.com/o/oauth2/auth?client_id=409502799386-6r7ba3thnc8nl7c0fllp88mggvrgth8s.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fdirecti.com%2Foauth2callback&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile", code=302)


@app.route('/', methods=['GET', 'POST'])
def hello():
	return "trt"
	
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)