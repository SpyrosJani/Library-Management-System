from flask import Blueprint, render_template, request, flash, redirect, url_for
import re
import mysql.connector as sql
from werkzeug.security import generate_password_hash, check_password_hash #sha256
from flask_login import login_user, login_required, logout_user, current_user

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    try:
        backround_image_url = '../static_images/library.jpg'
        return render_template("base.html", backround_image_url = backround_image_url, pageTitle = "Welcome!")
    except Exception as e:
        print(e)
        return render_template("landing.html", pageTitle = "Welcome!")

@routes.route('/home', methods = ['GET', 'POST'])
def home():
    return render_template('home.html')



@routes.route('/login', methods = ['GET', 'POST'])
def login():
    global is_admin
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        #if email != db['mysql_host'] or password != db['mysql_password']:
            #flash('Incorrect password', 'danger')
            #return #redirect



    return render_template("login.html")

@routes.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@routes.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    connection = sql.connect(host = 'localhost', database = 'librarydbms', user = 'root') 
    cursor = connection.cursor() 
    query1 = ('SELECT school.school_name FROM school')
    cursor.execute(query1)
    school = cursor.fetchall()

    for i in school:
        print (i)
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        cursor.close()
        connection.close()
        #python checks here
        if not (re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email)):
            flash ('Invalid email address', category = 'error')
        elif len(firstName) < 2 or len(lastName) < 2:
            flash('First and last names must be greater than 1 characters.', category = 'error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password1):
            flash('Password is too weak! Use a password of at least 8 characters. Must be restricted to uppercase, lowercase letters, numbers, any special character.', category = 'error')
        else:
            connection = sql.connect(host = 'localhost', database = 'librarydbms', user = 'root') 
            cursor = connection.cursor() 
            query2 = ("INSERT INTO user (login_id, passwd, first_name, last_name, birth_date, school_name, job, books_borrowed, user_status) VALUES ('{}', '{}', '{}', '{}', '{}', 'School A', 'Student', 0, 'Waiting');").format()
            cursor.execute(query2)
            connection.commit()
            cursor.close()
            connection.close()
            flash('Account created successfully!', category='success')
            return redirect(url_for('home'))
        
    return render_template("sign_up.html", school = school)