from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models.user import User

class RegistrationForm(FlaskForm):
    fullname         = StringField('Full Name',          validators=[Optional(), Length(max=150)])
    username         = StringField('Username',           validators=[DataRequired(), Length(3, 80)])
    email            = StringField('Email',              validators=[DataRequired(), Email()])
    password         = PasswordField('Password',         validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit           = SubmitField('Create Account')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('This email is already registered.')

class LoginForm(FlaskForm):
    identity = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password',        validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit   = SubmitField('Log In')