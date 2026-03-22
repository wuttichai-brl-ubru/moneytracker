from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional

class UpdateProfileForm(FlaskForm):
    fullname      = StringField('Full Name',      validators=[Optional(), Length(max=150)])
    username      = StringField('Username',       validators=[DataRequired(), Length(3, 80)])
    email         = StringField('Email',          validators=[DataRequired(), Email()])
    profile_image = FileField('Profile Picture',  validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit        = SubmitField('Save Changes')