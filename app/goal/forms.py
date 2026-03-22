from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length

class GoalForm(FlaskForm):
    icon          = StringField('Icon (Emoji)', default='🎯',
                      validators=[DataRequired(), Length(1, 10)])
    name          = StringField('Goal Name',
                      validators=[DataRequired(), Length(1, 150)])
    target_amount = DecimalField('Target Amount (THB)', places=2,
                      validators=[DataRequired(), NumberRange(min=1)])
    saved_amount  = DecimalField('Already Saved (THB)', places=2,
                      validators=[Optional(), NumberRange(min=0)], default=0)
    deadline      = DateField('Deadline (Optional)', validators=[Optional()])
    note          = TextAreaField('Note', render_kw={'rows': 2},
                      validators=[Optional(), Length(max=255)])
    submit        = SubmitField('Save')