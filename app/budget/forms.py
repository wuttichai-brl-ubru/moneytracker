from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime

_now = datetime.utcnow()

MONTHS = [
    (1,'January'),  (2,'February'), (3,'March'),     (4,'April'),
    (5,'May'),      (6,'June'),     (7,'July'),      (8,'August'),
    (9,'September'),(10,'October'), (11,'November'), (12,'December'),
]
YEARS = [(y, str(y)) for y in range(_now.year - 1, _now.year + 3)]

class BudgetForm(FlaskForm):
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    amount      = DecimalField('Budget Amount (THB)', places=2,
                    validators=[DataRequired(), NumberRange(min=1)])
    month       = SelectField('Month', choices=MONTHS, coerce=int, default=_now.month)
    year        = SelectField('Year',  choices=YEARS,  coerce=int, default=_now.year)
    submit      = SubmitField('Save')