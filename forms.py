from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SelectField, IntegerField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                               Length, EqualTo, Optional)
from wtforms.fields.html5 import URLField, DateTimeLocalField, DateField


from models import User, Feature

def username_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that email already exists.')





#need a registration form
class RegisterForm(Form):
    """Registration form"""
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),

        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
            ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
        )


#Need to have a login form
class LoginForm(Form):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])



#feature form
class FeatureForm(Form):
    '''Feature form'''
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    client = SelectField('Client', choices=[('Client A', 'Client A'),('Client B', 'Client B'), ('Client C', 'Client C')], validators=[DataRequired()])
    priority = IntegerField('Client Priority', validators=[DataRequired()])
    target_date = DateField('Target Date', validators=[DataRequired()])
    ticket_url = URLField('Ticket URL', validators=[DataRequired()])
    product_area = SelectField('Product Area', choices=[('Policies', 'Policies'),('Billing', 'Billing'),('Claims', 'Claims'),('Reports','Reports')], validators=[DataRequired()])


