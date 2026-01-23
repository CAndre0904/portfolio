from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, IntegerField, DateField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, number_range

selectMonths = [
    [1, 'January'],
    [2, 'February'],
    [3, 'March'],
    [4, 'April'],
    [5, 'May'],
    [6, 'June'],
    [7, 'July'],
    [8, 'August'],
    [9, 'September'],
    [10, 'October'],
    [11, 'November'],
    [12, 'December']
]

class ExpenseForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    amount = DecimalField(places=2, validators=[DataRequired(), number_range(min=0)])
    payment_day = IntegerField(validators=[DataRequired(), number_range(min=1, max=31)])
    start_month = SelectField(choices=selectMonths, validators=[DataRequired()])
    start_year = IntegerField(validators=[DataRequired()])
    last_month = SelectField(choices=selectMonths)
    last_year = IntegerField()
    submit = SubmitField()
