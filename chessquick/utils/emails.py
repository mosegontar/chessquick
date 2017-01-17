import os

from flask import render_template
from flask_mail import Message
from sendgrid.helpers.mail import *

from chessquick import mail, app, sendgrid
from .decorators import async

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)

def sendgrid_email(recipients, subject, body):

    from_email = Email("chessquickapp@gmail.com")
    subject = subject
    to_email = Email(recipients)
    content = Content("text/plain", body)
    mail = Mail(from_email, subject, to_email, content)
    response = sendgrid.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


def verify_email(recipients, confirm_url):
    """Send email with confirmation url to verify address"""

    subject = 'Chessquick: verify your email'
    sender = app.config['ADMINS'][0]
    recipients = recipients
    with app.app_context():
        text = render_template('email/activate_email.txt', confirm_url = confirm_url)
        html = render_template('email/activate_email.html', confirm_url = confirm_url)
    sendgrid_email(recipients, subject, text)


def notify_opponent(player, game_url, recipients, message=''):
    """Send email to notify opponent"""
    
    subject = 'Chessquick: your move!'
    recipients = recipients
    if not player or player == 'Guest':
        player = 'Yor opponent'
    with app.app_context():
        text = render_template('email/notify_opponent.txt', game_url=game_url, player=player, message=message)
        html = render_template('email/notify_opponent.html', game_url=game_url, player=player, message=message)
    sendgrid_email(recipients, subject, text)

def process_email(current_player, current_match, url, user, post):

    # Don't process email if API key not available
    if not os.environ.get('SENDGRID_API_KEY'):
        return

    # Determine if opponent has notify turned on. If so, get and send email notice.
    email = None
    if current_player == 'w' and current_match.black_notify:
        email = current_match.black_player.email
    if current_player == 'b' and current_match.white_notify:
        email = current_match.white_player.email

    message = None
    if email:
        playername = 'Guest' if not user.is_authenticated else user.username
        if post:
            message = post.contents
        notify_opponent(playername, url, email, message)
