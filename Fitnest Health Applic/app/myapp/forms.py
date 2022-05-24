"""This module holds the code of all WTForms used in the app

The standarn convention of defining a WTForm here is:

```python
class MyForm(FlaskForm):
    # Fields here
```

More detailed WTForm documentations can be found [here](https://wtforms.readthedocs.io/en/3.0.x/).

"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo
from wtforms import ValidationError

from myapp.models import User


class SignupForm(FlaskForm):
    """WTForm for signup page

    Attributes:
        email: Email user is using to sign up the account
        username: username field
        password: password field
        password2: confirmation password field
        submit: Submit field
    """
    email = StringField('EMAIL', validators = [DataRequired(), Email(message = 'invalid email')])
    username = StringField('USERNAME', validators = [DataRequired()])
    password = PasswordField('PASSWORD', validators = [DataRequired(), EqualTo('password2', message = 'Passwords must match')])
    password2 = PasswordField("CONFIRM PASSWORD", validators = [DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, field):
        """Make sure the email hasn't been registered"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')


class LoginForm(FlaskForm):
    """WTForm for login page

    Attributes:
        username: For user to put his/her registered username
        password: Password field
        remember_me: Remember whether the user ticked "remember me"
        submit: Submit field
    """
    username = StringField('USERNAME', validators=[DataRequired()])
    password = PasswordField('PASSWORD')
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class NextButton(FlaskForm):
    """WTForm for just a next submit field button

    Attributes:
        nextCard: Submit button to go to next
    """
    nextCard = SubmitField('Next')


class ObjectiveForm(FlaskForm):
    A = SubmitField('A')
    B = SubmitField('B')
    C = SubmitField('C')
    D = SubmitField('D')


class UploadMarkdownForm(FlaskForm):
    """WTForm for allowing user to upload a markdown file

    Attributes:
        file: Markdown file field to select markdown file to upload
        upload: Submit button to confirm upload
    """
    file = FileField('Select .md or .txt file:', validators=[FileRequired(), FileAllowed(['md','txt'])])
    upload = SubmitField('Upload')


class SearchForm(FlaskForm):
    """WTForm for a search field with submit button

    Attributes:
        text: Search text
        button: Submit button to confirm search
    """
    text = StringField('Text', validators=[])
    button = SubmitField('Search')



class JournalForm(FlaskForm):
    '''WTForm for upload file to journal page and later converting to pdf

    Attributes:
        name: journal name
        journal: journal file
        submit: Submit field to add card
    '''
    name = StringField('name', validators={DataRequired()})
    journals = FileField('file', validators={DataRequired()})
    submit = SubmitField('submit')

    
class JournalShareForm(FlaskForm):
    """WTForm for user to select which friend to share journal
    Attributes:
        dropdown: Dropdown to select friend's username
        share: Submit button to share
    """
    dropdown = SelectField('Dropdown', coerce=int)
    share = SubmitField('Share')

class AddWorkoutForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    muscle_group = SelectField('muscle', choices=[('back', 'Back'), ('chest', 'Chest'), ('legs', 'Legs'), ('arms', 'Arms')])
    duration_hour = IntegerField('hour', validators=[DataRequired()])
    duration_minute = IntegerField('minute', validators=[DataRequired()])
    sets = IntegerField('sets', validators=[DataRequired()])
    reps = IntegerField('reps', validators=[DataRequired()])
    description = TextAreaField('reps', validators=[])
