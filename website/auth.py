from flask import Blueprint, render_template, request, flash
from flask_mysqldb import MySQL
from website import create_app
import re
from werkzeug.security import generate_password_hash, check_password_hash #sha256

auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    global is_admin
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email != db['mysql_host'] or password != db['mysql_password']:
            flash('Incorrect password', 'danger')
            return #redirect



    return render_template("login.html")

@auth.route('/logout', methods = ['GET', 'POST'])
def logout():
    return render_template("logout.html")

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    global is_admin
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        #python checks here
        if not (re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email)):
            flash ('Invalid email address', category = 'error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 characters.', category = 'error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password1):
            flash('Password is too weak! Use a password of at least 8 characters. Must be restricted to uppercase, lowercase letters, numbers, any special character.', category = 'error')
        else:
            flash('Account created successfully!', category='success')
            
    return render_template("sign_up.html")