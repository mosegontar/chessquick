from flask import render_template
from flask_mail import Message
from chessquick import mail, app
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

def verify_email(recipients, confirm_url):
    subject = 'Chessquick: verify your email'
    sender = app.config['ADMINS'][0]
    recipients = [recipients]
    with app.app_context():
        text = render_template('email/activate_email.txt', confirm_url = confirm_url)
        html = render_template('email/activate_email.html', confirm_url = confirm_url)
    send_email(subject, 
               sender, 
               recipients, 
               text,
               html)
