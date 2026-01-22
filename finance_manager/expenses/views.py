from flask import Blueprint, render_template, flash, url_for, redirect, request
from finance_manager.config import db, Expense
from finance_manager.expenses.forms import ExpenseForm
from sqlalchemy import desc
from flask_login import current_user, login_required
from cryptography.fernet import Fernet
from hashlib import scrypt
import base64

expenses_bp = Blueprint('expenses', __name__, template_folder='templates')


@expenses_bp.route('/expenses')
@login_required
def expenses():

    # Methods for decrypting must be declared to pass onto the HTML as an expense cannot be decrypted until its author has been found
    def decrypt_title(expense):
        key = scrypt(password=str(expense.user.password).encode(), salt=str(expense.user.salt).encode(), n=2048, r=8, p=1, dklen=32)
        encoded_key = base64.b64encode(key)
        cipher = Fernet(encoded_key)
        return (cipher.decrypt(expense.title)).decode()

    # Retrieving all the posts
    all_expenses = Expense.query.order_by(desc('id')).all()
    # Rendering the expenses page and passing the methods through
    return render_template('expenses/expenses.html', expenses=all_expenses, decrypt_title=decrypt_title)




@expenses_bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    # Declaring the form
    form = ExpenseForm()
    if form.validate_on_submit():
        # Declaring values used for encrypting the title of the expense
        key = scrypt(password=str(current_user.password).encode(), salt=str(current_user.salt).encode(), n=2048, r=8, p=1, dklen=32)
        encoded_key = base64.b64encode(key)
        cipher = Fernet(encoded_key)
        title_bs = form.title.data.encode()
        encrypted_title = cipher.encrypt(title_bs)
        # Declaring the expense
        new_expense = Expense(userid=current_user.get_id(), title=encrypted_title, amount=form.amount.data, start_date=form.start_date.data, end_date=form.end_date.data)
        # Adding the expense to the database
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense created', category='success')
        return redirect(url_for('expenses.expenses'))
    return render_template('expenses/create.html', form=form)