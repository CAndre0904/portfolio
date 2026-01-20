from finance_manager.config import app
from flask import render_template, url_for, redirect
from flask_login import logout_user, login_required

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('home/index.html')

if __name__ == '__main__':
    # Running the app
    app.run()

