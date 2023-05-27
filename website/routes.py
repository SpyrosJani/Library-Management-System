from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import re
import mysql.connector as sql
from datetime import datetime
from os import abort
import time
import yaml
from yaml.loader import SafeLoader

routes = Blueprint('routes', __name__)

with open('data.yaml', 'r') as file:
    config = yaml.load(file, Loader = SafeLoader)

host = config['host']
user = config['user']
password = config['password']
database = config['database']

#----------------------------------HOME PAGE----------------------------------
@routes.route('/')
def index():
    global admin_access, sadmin_access
    admin_access = False
    sadmin_access = False
    session['connected'] = False
    session['id'] = -1
    directory = '/static_images/library.jpg'
    return render_template('home_page.html', image = directory ,pageTitle = "Welcome!")


@routes.route('/', methods = ['GET', 'POST'])
def login():
    try:
        if (request.method == 'POST'):
            email = request.form.get('email')
            password = request.form.get('password')
            role = str(request.form.get('Role'))
            connection = sql.connect(host = host, database = database, user = user, password = password) 
            cursor = connection.cursor() 
            if(role == 'Student' or role == 'Teacher'):
                query = ("SELECT user.user_id FROM user WHERE (login_id = '{}' AND passwd = '{}' AND job = '{}');".format(email, password, role))
                cursor.execute(query)
                aux = cursor.fetchall()
                if(len(aux) == 0):
                    flash('Invalid email address or password', category = 'error')
                else:
                    id = aux[0][0]
                    return redirect('/user')
            elif(role == 'School Administrator'):
                query = ("SELECT school_admin.scadmin_id FROM school_admin WHERE (login_id = '{}' AND passwd = '{}');".format(email, password))
                cursor.execute(query)
                aux = cursor.fetchall()
                if(len(aux) == 0):
                    flash('Invalid email address or password', category = 'error')
                else:
                    id = aux[0][0]
                    return redirect('/schooladmin')
            elif(role == 'Administrator'):
                query = ("SELECT administrator.admin_id FROM administrator WHERE (login_id = '{}' AND passwd = '{}');".format(email, password))
                cursor.execute(query)
                aux = cursor.fetchall()
                if(len(aux) == 0):
                    flash('Invalid email address or password', category = 'error')
                else:
                    id = aux[0][0]
                    return redirect('/admin')
            cursor.close()
            connection.close()
    except Exception as e:
        print("AN ERROR OCCURED")
        flash(str(e), "danger")
        abort()
    return render_template('home_page.html')
#----------------------------------HOME PAGE----------------------------------


#----------------------------------LOG OUT----------------------------------
@routes.route('/logout', methods = ['GET', 'POST'])
def logout():
    try:
        if (request.method == 'POST'):
            if(id != -1):
                id = -1 
                return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('home_page.html')    
    
#----------------------------------LOG OUT----------------------------------



#----------------------------------SIGN UP----------------------------------
@routes.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    try:
        #---------Database connection------------
        connection = sql.connect(host = 'localhost', database = 'librarydbms', user = 'root', password = 'password') 
        cursor = connection.cursor() 
        query = ('SELECT school.school_name FROM school')
        cursor.execute(query)
        #---------Database connection------------
        #--------Populating schools dropdown box with data--------
        schools = cursor.fetchall()
        schools = [' '.join(t) for t in schools]
        #--------Populating schools dropdown box with data--------       

        #Id submit is pressed (adding a new account)
        if (request.method == 'POST'):
            #------------Variables we need------------
            email = request.form.get('email')
            firstName = request.form.get('firstName')
            lastName = request.form.get('lastName')
            sex = request.form.get('Gender')
            dob = str(request.form.get('dob'))
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            school = request.form.get('School')
            role = request.form.get('Role')
            #------------Variables we need------------

            #------------Taking the school_id from the school the user selected------------
            query = ("SELECT school.school_id FROM school WHERE school.school_name = '{}'".format(school))
            cursor.execute(query)
            school_id = cursor.fetchall() 
            #------------Taking the school_id from the school the user selected------------   
        
            #-----------Duplicate email address check--------------------
            v_user = False
            v_school_admin = True
            if role == 'Student' or role == 'Teacher':
                query = ("SELECT * FROM user WHERE user.login_id = '{}'".format(email))
                cursor.execute(query)
                if (len(cursor.fetchall()) == 0):
                    v_user = True
            else:
                query = ("SELECT * FROM school_admin WHERE school_admin.scadmin_id = '{}'".format(email))
                cursor.execute(query)
                if (len(cursor.fetchall()) == 0):
                    v_school_admin = True
            #-----------Duplicate email address check--------------------

            #-----------Checking the birth_date-----------
            v_birth_date = True 
            format_string = "%Y-%m-%d"
            if(role == 'Student' and datetime.strptime(dob, format_string) >= datetime.strptime('2018-01-01', format_string)):
                v_birth_date = False 
            elif((role == 'Teacher' or role == 'School Administrator') and datetime.strptime(dob, format_string) >= datetime.strptime('2000-01-01', format_string)):
                v_birth_date = False
            #-----------Checking the birth_date-----------

            #python checks here
            if not (re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email)):
                flash('Invalid email address', category = 'error')
            elif v_birth_date == False:
                flash('Invalid date', category = 'error')
            elif v_user == False:
                flash('There is already a user with this email address registered', category = 'error')
            elif v_school_admin == False:
                flash('There is already a school administrator with this email address registered', category = 'error')
            elif len(firstName) < 2 or len(lastName) < 2:
                flash('First and last names must be greater than 1 characters.', category = 'error')
            elif password1 != password2:
                flash('Passwords don\'t match.', category='error')
            elif not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password1):
                flash('Password is too weak! Use a password of at least 8 characters. Must be restricted to uppercase, lowercase letters, numbers, any special character.', category = 'error')
            else:
                query = ("""INSERT INTO user (login_id, passwd, first_name, last_name, birth_date, school_id, job, books_borrowed, user_status) 
                        VALUES ('{}', '{}', '{}', '{}', '{}', {}, '{}', 0, 'Waiting');""".format(email, password2, firstName, lastName, str(dob), int(school_id[0][0]), role))
                cursor.execute(query)
                connection.commit()
                flash('Account created successfully!', category='success')
                return redirect('/home')
            
            cursor.close()
            connection.close()
    except Exception as e:
        flash(str(e), "danger")
        abort()
        
    return render_template("sign_up.html", school = schools)
#----------------------------------SIGN UP----------------------------------



#---------------------USER TEMPLATES-------------------------
@routes.route('/user')
def user(): 
    return render_template('user_firstpage.html')

@routes.route('/user/booksearch')
def user_booksearch():
    connection = sql.connect(host = host, user = user, password = password, database = database)
    cursor = connection.cursor()
    query = "SELECT * FROM book"
    cursor.execute(query)
    book_list = cursor.fetchall()
    cursor.close()

    return render_template('user_booksearch.html', book_list = book_list)

@routes.route('/user/booksearch/review')
def review(): 
    return render_template('review_form.html')

@routes.route('/user/borrowings')
def books():
    return render_template('user_borrowings.html')

@routes.route('/user/profile_student')
def profile_student():
    return render_template('user_profile_student.html')

@routes.route('/user/profile_teacher')
def profile_teacher():
    return render_template('user_profile_teacher.html')

@routes.route('/user/reviews')
def user_reviews():
    return render_template('user_reviews.html')
#-----------------USER TEMPLATES-------------------------------------


#-----------------ADMIN TEMPLATES-----------------------------------
@routes.route('/admin')
def admin(): 
    return render_template('admin_firstpage.html')


#------------------Admin->School List------------------
@routes.route('/admin/schoollist', methods=['GET', 'POST'])
def admin_schoollist(): 
    try:
        #---------Database connection------------
        connection = sql.connect(host = 'localhost', database = 'librarydbms', user = 'root') 
        cursor = connection.cursor() 
        query = ('SELECT school.school_name, school.city, school.addrss, school.phone_number, school.email, school.school_id FROM school;')
        cursor.execute(query)
        #---------Database connection------------
        #--------Populating schools table with data--------
        school = cursor.fetchall()
        #--------Populating schools  with data--------       
        cursor.close()
        connection.close()
    except Exception as e:
        flash(str(e), "danger")
        abort()   
    return render_template('admin_schoolList.html', school = school)
#------------------Admin->School List------------------

#------------------Admin->School List->Delete Button------------------
@routes.route('/admin_schoollist_delete', methods=['GET', 'POST'])
def admin_schoollist_deleting(): 
    try:
        if(request.method == 'POST'):
            buttonId = request.form['delete_button']
            #---------Database connection------------
            connection = sql.connect(host = 'localhost', database = 'librarydbms', user = 'root') 
            cursor = connection.cursor() 
            query = ('DELETE FROM school WHERE school.school_id = {};'.format(int(buttonId)))
            cursor.execute(query)
            connection.commit()
            #---------Database connection------------
            time.sleep(1)
            return redirect('/admin/schoollist')      
    except Exception as e:
        flash(str(e), "danger")
        abort()   
    return render_template('admin_schoolList.html')
#------------------Admin->School List->Delete Button------------------

#------------------Admin->School List->Update Button------------------
@routes.route('/admin_schoollist_update', methods=['GET', 'POST'])
def admin_schoollist_updating(): 
    try:
        if(request.method == 'POST'):
            #Taking the object from javascript event, this will be a list with one element  in python
            update = request.form.getlist('update_button')
            #Connection issues
            connection = sql.connect(host = 'localhost', database = 'librarydbms', user = 'root') 
            cursor = connection.cursor() 
            #Splitting the data in the one element into a python list, now i have the data in a list
            update = update[0].split(",")
            #update[5] is now the id
            query = ("""UPDATE school
                        SET school_name = '{}', city = '{}', phone_number = '{}', email = '{}', addrss = '{}'
                        WHERE school_id = {};""".format(update[0], update[1], update[3], update[4], update[2], int(update[5])))
            cursor.execute(query)
            connection.commit()
            time.sleep(1)
            return redirect('/admin/schoollist') 
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_schoolList.html')
#------------------Admin->School List->Update Button------------------






@routes.route('/admin/pending')
def admin_pending(): 
    return render_template('admin_pending.html')


#----------------------Adding a school----------------------
@routes.route('/admin/schoollist/add', methods=['GET', 'POST'])
def admin_addschool():
    try:
        if (request.method == 'POST'):
            #---------Database connection------------
            connection = sql.connect(host = 'localhost', database = 'librarydbms', user = 'root') 
            cursor = connection.cursor() 
            #---------Database connection------------
            print("Post request given")
            #------------Variables we need------------
            school_name = request.form.get('school_name')
            address = request.form.get('address')
            city = request.form.get('city')
            email = request.form.get('email')
            phone_number = str(request.form.get('phone_number'))
            #------------Variables we need------------   
            #------------Doing the necessary checks and inserting--------------
            query = ("SELECT * FROM school WHERE (school.school_name = '{}' OR school.addrss = '{}' OR school.email = '{}' OR school.phone_number = '{}');".format(school_name, address, email, phone_number))
            cursor.execute(query)
            check = cursor.fetchall()
            if( len(check) > 0):
                flash('There is already a school with the same name, address, phone number or email. Please check and try again', category='error')
            else:
                query = ("""INSERT INTO school (school_name, city, phone_number, email, addrss, admin_id)
                            VALUES ('{}', '{}', '{}', '{}', '{}', 6);""".format(school_name, city, phone_number, email, address))
                cursor.execute(query)
                connection.commit()
                flash('School added successfully!', category='success')
                cursor.close()
                connection.close()
                return redirect('/admin/schoollist')
            #------------Doing the necessary checks and inserting--------------
    except Exception as e:
        flash(str(e), "danger")
        abort()   
    return render_template('admin_addschool.html')
#----------------------Adding a school----------------------
#----------------ADMIN TEMPLATES------------------------------------


#---------------SCHOOL ADMIN TEMPLATES------------------------------
@routes.route('/schooladmin')
def schooladmin():
    return render_template('schooladmin_firstpage.html')

@routes.route('/schooladmin/booklist')
def schooladmin_booklist(): 
    return render_template('schooladmin_booklist.html')

@routes.route('/schooladmin/booklist/add')
def schooladmin_addbook():
    return render_template('schooladmin_addbook.html')

@routes.route('/schooladmin/users')
def schooladmin_userslist():
    return render_template('schooladmin_userslist.html')

@routes.route('/schooladmin/users/pending')
def schooladmin_pendingusers():
    return render_template('schooladmin_pendingusers.html')

@routes.route('/schooladmin/borrowings/list')
def schooladmin_borrowlist():
    return render_template('schooladmin_borrowlist.html')

@routes.route('/schooladmin/borrowings/pending')
def schooladmin_pendingborrowings():
    return render_template('schooladmin_pendingborrowings.html')

@routes.route('/schooladmin/reservelist')
def schooladmin_reservelist():
    return render_template('schooladmin_reservelist.html')

@routes.route('/schooladmin/return/approve')
def schooladmin_approvereturn():
    return render_template('schooladmin_returnapprove.html')

@routes.route('/schooladmin/return/overdue')
def schooladmin_overduereturn():
    return render_template('schooladmin_returnoverdue.html')

@routes.route('/schooladmin/reviews/approve')
def schooladmin_approvereviews():
    return render_template('schooladmin_approvereview.html')

@routes.route('/schooladmin/reviews/peruser')
def schooladmin_reviewperuser():
    return render_template('schooladmin_reviewperuser.html')

@routes.route('/schooladmin/reviews/percategory')
def schooladmin_reviewpercategory():
    return render_template('schooladmin_reviewpercategory.html')
#-----------------SCHOOL ADMIN TEMPLATES-------------------------------
