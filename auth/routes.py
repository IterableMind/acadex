from flask import render_template, url_for, flash
from . import auth_bp
from .forms import LoginForm


# Mock Data
user = {
    'usermail': 'oyarojared278@gmail.com',
    'password': 'code'
}

# The login route serves as a single entry point for teachers, parents, and admins.
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == user['usermail'] and form.password.data == 'code':
            return '<h2>Logged in Successfully</h2>'
        flash('Invalid usermail or password!', 'danger')
    return render_template(
        'login.html', 
        form=form, 
        title='Login'
      )


@auth_bp.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    return render_template('recover_password.html')