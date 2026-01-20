from datetime import datetime
from flask import Blueprint, render_template, flash, redirect, url_for, session, request, abort
from finance_manager.accounts.forms import RegistrationForm, LoginForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import login_user, login_required, current_user
from argon2 import PasswordHasher
import pyotp
from cryptography.fernet import Fernet
from hashlib import scrypt
import base64

# Declaring the password hasher
ph = PasswordHasher()
accounts_bp = Blueprint('accounts', __name__, template_folder='templates')

from finance_manager.config import User, db, app

@accounts_bp.route('/registration', methods=['GET', 'POST'])
def registration():

    # Checking if the user is authenticated as they would have already registered if they are
    if current_user.is_authenticated:
        flash('You have already registered.', category="primary")
        # Redirecting the user to their corresponding page
        if current_user.role == "db_admin":
            return redirect("http://127.0.0.1:5000/admin")
        else:
            return redirect("http://127.0.0.1:5000")
    # Declaring the form
    form = RegistrationForm()
    # Checking if the form is valid
    if form.validate_on_submit():
        # Checking if the email already exists
        if User.query.filter_by(email=form.email.data).first():
            # Alerting the user that the email already exists
            flash('Email already exists', category="danger")
            return render_template('accounts/registration.html', form=form)
        # Hashing the password
        password_hash = ph.hash(form.password.data)
        # Creating the user object to be added
        new_user = User(email=form.email.data, firstname=form.firstname.data, lastname=form.lastname.data, phone=form.phone.data, password=password_hash)
        # Adding the user to the database
        db.session.add(new_user)
        db.session.commit()
        flash('Account Created', category='success')
    # Rendering the registration page
    return render_template('accounts/registration.html', form=form)

@accounts_bp.route('/login', methods=['GET', 'POST'])
@Limiter.limit(self=Limiter(key_func=get_remote_address, app=app), limit_value='20 per minute')
def login():
    # Checking if the user is authenticated as they would have already logged in if they are
    if current_user.is_authenticated:
        flash('You have already logged in.', category="primary")
        # Redirecting the user to their corresponding page
        if current_user.role == "db_admin":
            return redirect("http://127.0.0.1:5000/admin")
        else:
            return redirect("http://127.0.0.1:5000")
    # Setting the authentication attempts to 0 if the user has not already attempted logging in
    if not session.get('authentication_attempts'):
        session['authentication_attempts'] = 0
    # Declaring the form
    form = LoginForm()
    if form.validate_on_submit():
        # Searching for the email
        if User.query.filter_by(email=form.email.data).first():
            # Declaring a user object for the email to compare the values
            userLogin = User.query.filter_by(email=form.email.data).first()
            # Checking if the password is correct and either the pin is correct or MFA is not yet enabled
            if userLogin.verify_password(form.password.data):


                    flash('Login Successful', category='success')
                    session['authentication_attempts'] = 0
                    login_user(userLogin)
                    # Redirecting the user to their corresponding page
                    if current_user.role=="db_admin":
                        return redirect("http://127.0.0.1:5000/admin")
                    else:
                        return redirect("http://127.0.0.1:5000")
            else:
                # If email is correct but password is incorrect an authentication attempt will be added
                session['authentication_attempts'] = session.get('authentication_attempts') + 1
                # If the user has had 3 attempts then they will be locked out
                if session.get('authentication_attempts') >= 3:
                    return render_template('accounts/login.html')
                else:
                    # Alerting the user as to how many attempts they have left
                    flash(('Invalid user details, ' + str(3 - session.get('authentication_attempts')) + ' attempts remaining'), category="danger")
        else:
            session['authentication_attempts'] = session.get('authentication_attempts') + 1
            # If the user has had 3 attempts then they will be locked out
            if session.get('authentication_attempts') >= 3:
                return render_template('accounts/login.html')

            else:
                # Alerting the user as to how many attempts they have left
                flash(('Invalid user details, ' + str(3 - session.get('authentication_attempts')) + ' attempts remaining'), category="danger")
    return render_template('accounts/login.html', form=form)

# Declaring a method to unlock the account after exceeding login attempts
@accounts_bp.route('/unlock')
def unlock():
    session['authentication_attempts'] = 0
    return redirect(url_for('accounts.login'))

