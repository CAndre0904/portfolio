from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, IntegerField, DateField
from wtforms.validators import DataRequired, number_range

class ExpenseForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    amount = DecimalField(places=2, validators=[DataRequired(), number_range(min=0)])
    start_date = DateField(validators=[DataRequired()])
    end_date = DateField()
    submit = SubmitField()
