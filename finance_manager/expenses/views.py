from flask import Blueprint, render_template, flash, url_for, redirect, request
from finance_manager.config import db, Expense
from finance_manager.expenses.forms import ExpenseForm
from sqlalchemy import desc
from flask_login import current_user, login_required
from cryptography.fernet import Fernet
from hashlib import scrypt
import base64

expenses_bp = Blueprint('expenses', __name__, template_folder='templates')

months = {
            'January': 1,
            'February': 2,
            'March': 3,
            'April': 4,
            'May': 5,
            'June': 6,
            'July': 7,
            'August': 8,
            'September': 9,
            'October': 10,
            'November': 11,
            'December': 12
        }

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

    # Calculating the total expenses for this month
    total = 0
    for expense in all_expenses:
        total = total + expense.amount

    # Rendering the expenses page and passing the methods through
    return render_template('expenses/expenses.html', expenses=all_expenses, decrypt_title=decrypt_title, monthly_total = total)


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

        months = {
            'January': 1,
            'February': 2,
            'March': 3,
            'April': 4,
            'May': 5,
            'June': 6,
            'July': 7,
            'August': 8,
            'September': 9,
            'October': 10,
            'November': 11,
            'December': 12
        }



        # Declaring the expense
        new_expense = Expense(userid=current_user.get_id(), title=encrypted_title,
                              amount=form.amount.data, payment_day=form.payment_day.data,
                              start_month=form.start_month.data, start_year=form.start_year.data,
                              last_month=form.last_month.data, last_year=form.last_year.data)
        # Adding the expense to the database
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense created', category='success')
        return redirect(url_for('expenses.expenses'))
    return render_template('expenses/create.html', form=form)

@expenses_bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # Only the author can update the expense
    if current_user.id != (Expense.query.filter_by(id=id).first()).userid:
        flash('You do not have authorisation to update this expense.', category="primary")
        return redirect(url_for('index'))
    # Finding the expense
    expense_to_update = Expense.query.filter_by(id=id).first()
    if not expense_to_update:
        return redirect(url_for('index'))
    form = ExpenseForm()
    # Declaring the key for encrypting the updated expense
    key = scrypt(password=str(current_user.password).encode(), salt=str(current_user.salt).encode(), n=2048, r=8, p=1, dklen=32)
    encoded_key = base64.b64encode(key)
    cipher = Fernet(encoded_key)
    if form.validate_on_submit():
        # Encrypting the updated data
        title_bs = form.title.data.encode()
        encrypted_title = cipher.encrypt(title_bs)
        # Updating the expense
        expense_to_update.update(title=encrypted_title,
                              amount=form.amount.data, payment_day=form.payment_day.data,
                              start_month=form.start_month.data, start_year=form.start_year.data,
                              last_month=form.last_month.data, last_year=form.last_year.data)
        flash('Expense updated', category='success')
        return redirect(url_for('expenses.expenses'))
    # Decoding the data to be viewed
    # Setting the form's fields to be the already existing data
    form.title.data = (cipher.decrypt(expense_to_update.title)).decode()
    form.amount.data = expense_to_update.amount
    form.payment_day.data = expense_to_update.payment_day
    form.start_month.data = expense_to_update.start_month
    form.start_year.data = expense_to_update.start_year
    form.last_month.data = expense_to_update.last_month
    form.last_year.data = expense_to_update.last_year


    return render_template('expenses/update.html', form=form)

@expenses_bp.route('/<int:id>/delete')
@login_required
def delete(id):
    # Only the author can delete the expense
    if current_user.id != (Expense.query.filter_by(id=id).first()).userid:
        flash('You do not have authorisation to delete this expense.', category="primary")
        return redirect(url_for('expenses.expenses'))
    # Deleting the expense
    Expense.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Expense deleted', category='success')
    return redirect(url_for('expenses.expenses'))
