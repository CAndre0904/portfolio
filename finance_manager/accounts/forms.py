from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, regexp, Email

class RegistrationForm(FlaskForm):
    # Declaring the form's attributes with their validators
    email = StringField(validators=[DataRequired(), Email(message="Invalid email address.")])
    firstname = StringField(validators=[DataRequired(), regexp('^[a-zA-Z\-]+$', message="Invalid first name.")])
    lastname = StringField(validators=[DataRequired(), regexp('^[a-zA-Z\-]+$', message="Invalid last name.")])
    phone = StringField(validators=[DataRequired(), regexp('02\d-\d{8}|011\d-\d{7}|01\d1-\d{7}|01\d{3}-\d{5}|01\d{3}-\d{6}', message="Invalid phone number.")])
    password = PasswordField(validators=[DataRequired(),
                                         Length(8, 15, message="Password must be between 8 and 15 characters long."),
                                         regexp('.*[a-zA-Z\d\!\@\£\$\%\^\&\*\(\)\)\+\=\/\\\?\,\.\<\>\{\}\'\"\#\€\`\~\;\:\-\_\.]',message='Password must contain both one uppercase letter, one lowercase letter, a number and a special character out of the following !@£$%^&*())+=/\?,.<>{}'"#€`~;:-_.")])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password', message="Both password fields must be the equal!\n")])
    submit = SubmitField()

class LoginForm(FlaskForm):
    # Declaring the form's attributes with their validators
    email = StringField(validators=[DataRequired()])
    password = StringField(validators=[DataRequired()])
    submit = SubmitField()
