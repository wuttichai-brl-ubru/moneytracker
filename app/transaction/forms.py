from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import DecimalField, SelectField, TextAreaField, SubmitField, StringField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange, Optional, Length
from datetime import datetime

class TransactionForm(FlaskForm):
    type        = SelectField('Type',
                    choices=[('income', 'Income 💚'), ('expense', 'Expense ❤️')],
                    validators=[DataRequired()])
    amount      = DecimalField('Amount (THB)', places=2,
                    validators=[DataRequired(), NumberRange(min=0.01)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', render_kw={'rows': 2})
    tag         = StringField('Tag', validators=[Optional(), Length(max=100)],
                    render_kw={'placeholder': '#travel #food #birthday'})
    date        = DateTimeLocalField('Date & Time', format='%Y-%m-%dT%H:%M',
                    validators=[DataRequired()], default=datetime.now)
    slip_image  = FileField('Attach Slip', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit      = SubmitField('Save')