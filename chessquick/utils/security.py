from itsdangerous import URLSafeTimedSerializer
from .. import app

# generate timed random url for email verification
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

def next_is_valid(endpoint):
    """Make sure requested redirect endpoint is valid"""
    return endpoint in app.view_functions