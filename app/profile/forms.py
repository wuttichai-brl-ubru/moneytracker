from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo

class UpdateProfileForm(FlaskForm):
    fullname      = StringField('Full Name',      validators=[Optional(), Length(max=150)])
    username      = StringField('Username',       validators=[DataRequired(), Length(3, 80)])
    email         = StringField('Email',          validators=[DataRequired(), Email()])
    profile_image = FileField('Profile Picture',  validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit        = SubmitField('Save Changes')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password     = PasswordField('New Password',     validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                         validators=[DataRequired(), EqualTo('new_password')])
    submit           = SubmitField('Change Password')