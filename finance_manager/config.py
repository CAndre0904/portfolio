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

    # Declaring a constructor
    def __init__(self, email, firstname, lastname, phone, password):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = password
        self.role = "end_user"
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


# IMPORT BLUEPRINTS
from finance_manager.accounts.views import accounts_bp, ph

# REGISTER BLUEPRINTS
app.register_blueprint(accounts_bp)

