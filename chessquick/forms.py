from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, ValidationError
from chessquick.models import Users, Matches, Rounds

class Unique(object):
    """Check that the model.field instance is unique. If not, raise error."""

    def __init__(self, model, field, message=u'This element already exists.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        """On call to Unique object, run check"""
        
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)


class UserPassEmailForm(FlaskForm):
    """UserPassEmail Form"""

    username = StringField('Username', validators=[DataRequired(),
        Unique(
            Users,
            Users.username,
            message=u'There is already an account with that username.')])

    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    remember_me = BooleanField('remember_me', default=False)
    
