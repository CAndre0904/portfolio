import re
from functools import wraps
from flask import Flask, url_for, redirect, render_template, flash, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
import base64
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, UserMixin, current_user
from dotenv import load_dotenv
import pyotp
import logging
import os



# Loading the env file
load_dotenv()
app = Flask(__name__)

# Declaring the login manager
login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.login_message = 'Please log in first to access this page.'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

# SECRET KEY FOR FLASK FORMS
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# DATABASE CONFIGURATION
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_ECHO'] = bool(os.getenv('SQLALCHEMY_ECHO'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = bool(os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS'))

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_names)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# Declaring the database
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

# Database tables


class Expense(db.Model):
    __tablename__ = 'expenses'
    # Declaring the fields for the expenses table
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    user = db.relationship("User", back_populates="expenses")

    # Declaring the constructor
    def __init__(self, userid, title, amount, start_date, end_date):
        self.userid = userid
        self.created = datetime.now()
        self.title = title
        self.amount = amount
        self.start_date = start_date
        self.end_date = end_date

    # Declaring a method to update an expense
    def update(self, title, amount, due_date, end_date):
        self.created = datetime.now()
        self.title = title
        self.amount = amount
        self.start_date = due_date
        self.end_date = end_date
        db.session.commit()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)

    # Role information
    role = db.Column(db.String(100), nullable=False)

    # Salt for runtime encryption key
    salt = db.Column(db.String(100), nullable=False)

    # Login manager properties
    active = db.Column(db.Boolean, nullable=False, default=True)

    expenses = db.relationship("Expense", order_by=Expense.id, back_populates="user")

    # Declaring a constructor
    def __init__(self, email, firstname, lastname, phone, password):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = password
        self.role = "db_admin"
        self.salt = base64.b64encode(secrets.token_bytes(32)).decode()

    # Declaring a method to verify the hashed password
    def verify_password(self, submitted_password):
        # If the entered password is incorrect then ph.verify will return an error, so this must be caught
        try:
            password_verified = ph.verify(self.password, submitted_password)
        except:
            password_verified = False
        return password_verified

    # Declaring a method for loading the user into the login manager
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

# DATABASE ADMINISTRATOR
class MainIndexLink(MenuLink):
    def get_url(self):
        return url_for('index')

class UserView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('id','email','password','firstname','lastname','phone','role')

    # Only db admins can access the users table
    def is_accessible(self):
        return True
        if current_user.is_authenticated:
            return current_user.role == 'db_admin'
        return False

    def inaccessible_callback(self, name, **kwargs):
        # If the user is anonymous then they should be redirected back to the login page
        if current_user.is_anonymous:
            flash('Admin access is required for this page.', category="danger")
            return redirect(url_for('accounts.login'))


class ExpenseView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('id','userid','created','title','amount','start_date', 'end_date','user')

    # Only db admins can access the users table
    def is_accessible(self):
        return True
        if current_user.is_authenticated:
            return current_user.role == 'db_admin'
        return False

    def inaccessible_callback(self, name, **kwargs):
        # If the user is anonymous then they should be redirected back to the login page
        if current_user.is_anonymous:
            flash('Admin access is required for this page.', category="danger")
            return redirect(url_for('accounts.login'))




admin = Admin(app, name='DB Admin', template_mode='bootstrap4')
admin._menu = admin._menu[1:]
admin.add_link(MainIndexLink(name='Home Page'))
admin.add_view(UserView(User, db.session))
admin.add_view(ExpenseView(Expense, db.session))
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = bool(os.getenv('FLASK_ADMIN_FLUID_LAYOUT'))







# IMPORT BLUEPRINTS
from finance_manager.accounts.views import accounts_bp, ph
from finance_manager.expenses.views import expenses_bp

# REGISTER BLUEPRINTS
app.register_blueprint(accounts_bp)
app.register_blueprint(expenses_bp)

