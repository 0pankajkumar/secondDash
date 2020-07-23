
# Configuration
GOOGLE_CLIENT_ID = open('/etc/googleauth/googleauthid',
						'r').readlines()[0].strip()
GOOGLE_CLIENT_SECRET = open(
	'/etc/googleauth/googleauthsecret', 'r').readlines()[0].strip()
# GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
# GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
	"https://accounts.google.com/.well-known/openid-configuration"
)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
	return User.get(user_id)




def get_google_provider_cfg():
	return requests.get(GOOGLE_DISCOVERY_URL).json()
