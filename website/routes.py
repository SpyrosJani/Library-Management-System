from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import re
import mysql.connector as sql
from datetime import datetime
from os import abort

global id 
id  = -1
routes = Blueprint('routes', __name__)


#----------------------------------HOME PAGE----------------------------------
@routes.route('/')
def index():
    directory = '/static_images/library.jpg'
    return render_template('home_page.html', image = directory ,pageTitle = "Welcome!")


@routes.route('/', methods = ['GET', 'POST'])
def login():
    try:
        if (request.method == 'POST'):
            email = request.form.get('email')
            password = request.form.get('password')
            role = str(request.form.get('Role'))
            connection = sql.connect(host = 'localhost', database = 'librarydbms', user = 'root') 
            cursor = connection.cursor() 
            if(role == 'Student' or role == 'Teacher'):
                query = ("SELECT user.user_id FROM user WHERE (login_id = '{}' AND passwd = '{}' AND job = '{}');".format(email, password, role))
                cursor.execute(query)
                aux = cursor.fetchall()
                if(len(aux) == 0):
                    flash('Invalid email address or password', category = 'error')
                else:
                    id = aux[0][0]
                    return redirect('/sign-up')
            elif(role == 'School Administrator'):
                query = ("SELECT school_admin.scadmin_id FROM school_admin WHERE (login_id = '{}' AND passwd = '{}');".format(email, password))
                cursor.execute(query)
                if(len(cursor.fetchall()) == 0):
                    flash('Invalid email address or password', category = 'error')
                else:
                    id = aux[0][0]
                    return redirect('/sign-up')
            elif(role == 'Administrator'):
                query = ("SELECT administrator.admin_id FROM administrator WHERE (login_id = '{}' AND passwd = '{}');".format(email, password))
                cursor.execute(query)
                if(len(cursor.fetchall()) == 0):
                    flash('Invalid email address or password', category = 'error')
                else:
                    id = aux[0][0]
                    return redirect('/sign-up')
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
        if(id != -1):
            id = -1 
    except Exception as e:
        flash(str(e), "danger")
        abort()
        
    return redirect('/home')
#----------------------------------LOG OUT----------------------------------



#----------------------------------SIGN UP----------------------------------
@routes.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    try:
        #---------Database connection------------
        connection = sql.connect(host = 'localhost', database = 'librarydbms', user = 'root') 
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

            print("THE ELEMENTS ARE", school_id[0][0], dob)

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

@routes.route('/user/booklist')
def user_booklist():
    return render_template('user_booklist.html')

@routes.route('/user/booklist/review')
def review(): 
    return render_template('review_form.html')

@routes.route('/user/books')
def books():
    return render_template('user_books.html')

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

@routes.route('/admin/schoollist')
def admin_schoollist(): 
    return render_template('admin_schoolList.html')

@routes.route('/admin/pending')
def admin_pending(): 
    return render_template('admin_pending.html')

@routes.route('/admin/schoollist/add')
def admin_addschool():
    return render_template('admin_addschool.html')
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
