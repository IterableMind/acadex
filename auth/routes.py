from flask import render_template, url_for
from . import auth_bp

# The login route serves as a single entry point for teachers, parents, and admins.
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', title='Login')
