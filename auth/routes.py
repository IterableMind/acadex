from flask import render_template, url_for, flash, redirect
from . import auth_bp
from ..admin import admin_bp
from .forms import LoginForm


# Mock Data
user = {
    'usermail': 'oyarojared278@gmail.com',
    'password': 'code',
    'role': 'admin'
}


# The login route serves as a single entry point for teachers, parents, and admins.
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == user['usermail'] and form.password.data == 'code':
            if user['role'] == 'admin':
                return redirect(url_for('admin_bp.dashboard'))
            elif user['role'] == 'teacher':
                return redirect(url_for('teachr_bp.dashboard'))
            else:
                return 'No role is assigned to this user!'
        flash('Invalid usermail or password!', 'danger')
    return render_template(
        'login.html', 
        form=form, 
        title='Login'
      )


@auth_bp.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    return render_template('recover_password.html')