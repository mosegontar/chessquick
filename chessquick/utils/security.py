from bs4 import BeautifulSoup
from itsdangerous import URLSafeTimedSerializer
from .. import app

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

def sanitize_comments(message):
    soup = BeautifulSoup(message, 'html.parser')
    for tag in soup.findAll(True):
        if tag not in app.config['WHITELIST']:
            tag.extract()
    return soup.renderContents().decode('utf-8')