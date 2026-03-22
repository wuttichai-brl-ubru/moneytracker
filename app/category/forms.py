from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class CategoryForm(FlaskForm):
    name   = StringField('Category Name', validators=[DataRequired(), Length(1, 100)])
    type   = SelectField('Type',
               choices=[('income', 'Income'), ('expense', 'Expense')],
               validators=[DataRequired()])
    icon   = StringField('Icon (Emoji)', validators=[DataRequired(), Length(1, 10)],
               default='💰')
    submit = SubmitField('Save')