from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import re
import mysql.connector as sql
from datetime import datetime
from os import abort
from website.credentials import user_config, database_config, host_config, password_config

routes = Blueprint('routes', __name__)

#----------------------------------HOME PAGE----------------------------------
@routes.route('/')
def index(): 
    global admin_access, sadmin_access, user_access
    admin_access = False
    sadmin_access = False
    user_access = False
    session['connected'] = False
    session['id'] = -1
    directory = '/static/library.jpg'
    return render_template('home_page.html', image = directory ,pageTitle = "Welcome!")


@routes.route('/', methods = ['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        role = str(request.form.get('Role'))
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor() 
        if(role == 'Student' or role == 'Teacher'):
            query = ("SELECT user_id FROM user WHERE (login_id = '{}' AND passwd = '{}' AND job = '{}' AND user_status = 'Approved');".format(email, password, role))
            cursor.execute(query)
            aux = cursor.fetchall()
            cursor.close()
            connection.close()
            if(len(aux) == 0):
                flash('Invalid email address or password or you are still not approved', category = 'error')
            else:
                session['id'] = aux[0][0]
                session['connected'] = True
                return redirect('/user')
        elif(role == 'School Administrator'):
            query = ("SELECT scadmin_id FROM school_admin WHERE (login_id = '{}' AND passwd = '{}' AND scadmin_status = 'Approved');".format(email, password))
            cursor.execute(query)
            aux = cursor.fetchall()
            cursor.close()
            connection.close()
            if(len(aux) == 0):
                flash('Invalid email address or password or you are still not approved', category = 'error')
            else:
                session['id'] = aux[0][0]
                session['connected'] = True
                return redirect('/schooladmin')
        elif(role == 'Administrator'):
            query = ("SELECT admin_id FROM administrator WHERE (login_id = '{}' AND passwd = '{}');".format(email, password))
            cursor.execute(query)
            aux = cursor.fetchall()
            cursor.close()
            connection.close()
            if(len(aux) == 0):
                flash('Invalid email address or password', category = 'error')
            else:
                session['id'] = aux[0][0]
                session['connected'] = True
                return redirect('/admin')
        cursor.close()
        connection.close()
        return redirect('/')
    '''except Exception as e:
        print("AN ERROR OCCURED")
        flash(str(e), "danger")
        abort()'''
    
    return render_template('home_page.html')
#----------------------------------HOME PAGE----------------------------------


#----------------------------------LOG OUT----------------------------------
@routes.route('/logout', methods = ['GET', 'POST'])
def logout():
    global admin_access, sadmin_access
    try:
        if(session.get("connected") == True):
            session['connected'] = False
            session['id'] = -1  
            admin_access = False
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return redirect('/')      
#----------------------------------LOG OUT----------------------------------



#----------------------------------SIGN UP----------------------------------
@routes.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    try:
        #---------Database connection------------
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor() 
        query = ('SELECT school_name FROM school;')
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
            query = ("SELECT school_id FROM school WHERE school_name = '{}'".format(school))
            cursor.execute(query)
            school_id = cursor.fetchall() 
            #------------Taking the school_id from the school the user selected------------   
        
            #-----------Duplicate email address check--------------------
            v_user = False
            v_school_admin = False
            if (role == 'Student' or role == 'Teacher'):
                query = ("SELECT * FROM user WHERE login_id = '{}';".format(email))
                cursor.execute(query)
                if (len(cursor.fetchall()) == 0):
                    v_user = True
            else:
                query = ("SELECT * FROM school_admin WHERE login_id = '{}';".format(email))
                cursor.execute(query)
                if (len(cursor.fetchall()) == 0):
                    v_school_admin = True
            #-----------Duplicate email address check--------------------

            #-----------Checking the birth_date-----------
            v_birth_date = False 
            format_string = "%Y-%m-%d"
            if(role == 'Student' and datetime.strptime(dob, format_string) >= datetime.strptime('2018-01-01', format_string)):
                v_birth_date = True 
            elif((role == 'Teacher' or role == 'School Administrator') and datetime.strptime(dob, format_string) >= datetime.strptime('2000-01-01', format_string)):
                v_birth_date = True
            #-----------Checking the birth_date-----------

            #python checks here
            if not (re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email)):
                flash('Invalid email address', category = 'error')
            elif (v_birth_date == True):
                flash('Invalid date', category = 'error')
            elif (v_user == False and v_school_admin == False):
                flash('This email is already occupied', category = 'error')
            elif len(firstName) < 2 or len(lastName) < 2:
                flash('First and last names must be greater than 1 characters.', category = 'error')
            elif password1 != password2:
                flash('Passwords don\'t match.', category='error')
            elif not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password1):
                flash('Password is too weak! Use a password of at least 8 characters. Must be restricted to uppercase, lowercase letters, numbers, any special character.', category = 'error')
            else:
                if(role == 'Student' or role == 'Teacher'):
                    query = ("""INSERT INTO user (login_id, passwd, first_name, last_name, sex, birth_date, school_id, job, books_borrowed, user_status) 
                            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', {}, '{}', 0, 'Waiting');""".format(email, password2, firstName, lastName, sex, str(dob), int(school_id[0][0]), role))
                else:
                    query = ("""INSERT INTO school_admin (login_id, passwd, first_name, last_name, sex, birth_date, scadmin_status, school_id)
                            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', 'Waiting', {});""".format(email, password2, firstName, lastName, sex, str(dob), int(school_id[0][0])))
                cursor.execute(query)
                connection.commit()
                cursor.close()
                connection.close()
                flash('Account created successfully!', category='success')
                return redirect('/')
            cursor.close()
            connection.close()
            return redirect('/sign-up')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template("sign_up.html", school = schools)
#----------------------------------SIGN UP----------------------------------



#---------------------USER TEMPLATES-------------------------
@routes.route('/user', methods = ['GET', 'POST'])
def user(): 
    global user_access
    user_access = True
    try:
        connection = sql.connect(host = host_config, user = user_config, database = database_config, password = password_config)
        cursor = connection.cursor()
        query = ("SELECT * FROM user WHERE user_id = {};".format(int(session.get("id"))))
        cursor.execute(query)
        aux = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(aux) == 0:
            user_access = False
            return redirect('/')
    except Exception as e:
        flash(str(e), 'danger')
        abort()

    return render_template('user_firstpage.html')

@routes.route('/user/booksearch', methods = ['GET', 'POST'])
def user_booklist():
    global user_access, books
    if (user_access):
        print("Post request given")
        connection = sql.connect(host = host_config, user = user_config, password = password_config, database = database_config)
        cursor = connection.cursor()
        which_title = request.form.get('title')
        which_author_name = request.form.get('author')
        which_category = request.form.get('category')
        user_id = int(session['id'])
        query = ('SELECT school_id FROM user WHERE user_id = {};'.format(user_id))
        cursor.execute(query)
        aux = cursor.fetchall()
        school_id = int(aux[0][0])
        print(school_id)
        if which_title == None:
            which_title = ''
        if which_author_name == None:
            which_author_name = ''
        if which_category == None:
            which_category = ''
        cursor.callproc('search_book', [which_title, which_author_name, which_category, school_id])

        if (cursor.rowcount == -1):
            books = []
            print("##########################################")
        else:
            for result in cursor.stored_results():
                books = result.fetchall()
                print(books)
        
        cursor.close()
        connection.close()
    else:
        redirect('/')
        
    return render_template('user_booksearch.html', books = books)

    '''except Exception as e:
        flash(str(e), 'danger')
        abort()'''

@routes.route('/user/booksearch/review')
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
    global admin_access
    admin_access = True
    try:
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ("SELECT * FROM administrator WHERE admin_id = {};".format(int(session.get("id"))))
        cursor.execute(query)
        aux = cursor.fetchall()
        cursor.close()
        connection.close()
        if(len(aux) == 0):
            admin_access = False
            return redirect("/")
    except Exception as e:
        flash(str(e), "danger")
        abort() 
    return render_template('admin_firstpage.html')


#------------------Admin->School List------------------
@routes.route('/admin/schoollist', methods=['GET', 'POST'])
def admin_schoollist(): 
    global admin_access
    try:
        if(admin_access):
            which_school = request.form.get('search_school')
            if(which_school == None):
                which_school = ''
            #---------Database connection------------
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor() 
            query = ("""SELECT school_name, city, addrss, phone_number, email, school_id 
                        FROM school
                        WHERE ('{}' = '' OR school_name LIKE '%{}%')
                        ORDER BY school_name;""".format(which_school, which_school))
            cursor.execute(query)
            #---------Database connection------------
            #--------Populating schools table with data--------
            school = cursor.fetchall()
            #--------Populating schools  with data--------       
            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_schoolList.html', school = school)
#------------------Admin->School List------------------

#------------------Admin->School List->Delete Button------------------
@routes.route('/admin_schoollist_delete', methods=['GET', 'POST'])
def admin_schoollist_deleting(): 
    global admin_access
    try:
        if(admin_access):
            if(request.method == 'POST'):
                buttonId = request.form['delete_button']
                #---------Database connection------------
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor() 
                query = ('DELETE FROM school WHERE school_id = {};'.format(int(buttonId)))
                cursor.execute(query)
                connection.commit()
                cursor.close()
                connection.close()
                #---------Database connection------------
                return redirect('/admin/schoollist')
        else:
            return redirect('/')      
    except Exception as e:
        flash(str(e), "danger")
        abort()   
    return render_template('admin_schoolList.html')
#------------------Admin->School List->Delete Button------------------

#------------------Admin->School List->Update Button------------------
@routes.route('/admin_schoollist_update', methods=['GET', 'POST'])
def admin_schoollist_updating(): 
    global admin_access
    try:
        if(admin_access):
            if(request.method == 'POST'):
                #Taking the object from javascript event, this will be a list with one element  in python
                update = request.form.getlist('update_button')
                #Connection issues
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor() 
                #Splitting the data in the one element into a python list, now i have the data in a list
                update = update[0].split(",")
                #update[5] is now the id
                query = ("SELECT * FROM school WHERE ((school_name = '{}' OR phone_number = '{}' OR email = '{}' OR addrss = '{}') AND school_id != {});".format(update[0], update[3], update[4], update[2], int(update[5])))
                cursor.execute(query)
                aux = cursor.fetchall()
                if(len(aux) != 0):
                    flash('One of the updated elements exists in another school. Please try again', category='error')
                else:
                    query = ("""UPDATE school
                                SET school_name = '{}', city = '{}', phone_number = '{}', email = '{}', addrss = '{}'
                                WHERE school_id = {};""".format(update[0], update[1], update[3], update[4], update[2], int(update[5])))
                    cursor.execute(query)
                    connection.commit()
                cursor.close()
                connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_schoolList.html')
#------------------Admin->School List->Update Button------------------



#------------------Admin->See approved School Admins------------------
@routes.route('/admin/show_admins', methods=['GET', 'POST'])
def admin_pending_see(): 
    global admin_access
    try:
        if(admin_access):
            which_admin = request.form.get('search_approved_admin')
            if(which_admin == None):
                which_admin = ''
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor() 
            query = ("""SELECT school_admin.first_name, school_admin.last_name, school.school_name
                        FROM school_admin
                        LEFT JOIN school ON school_admin.school_id = school.school_id
                        WHERE (school_admin.scadmin_status = 'Approved' AND 
                                ('{}' = '' OR school_admin.first_name LIKE '%{}%' OR school_admin.last_name LIKE '%{}%'))
                        ORDER BY school_admin.first_name, school_admin.last_name;""".format(which_admin, which_admin, which_admin))
            cursor.execute(query)
            school_admin = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect("/")
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_aproved_pending.html', school_admin = school_admin)
#------------------Admin->See approved School Admins------------------

#------------------Admin->Pending School Admin------------------
@routes.route('/admin/pending', methods=['GET', 'POST'])
def admin_pending(): 
    global admin_access
    try:
        if(admin_access):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor() 
            query = ("""SELECT school_admin.first_name, school_admin.last_name, school.school_name, school_admin.scadmin_id
                        FROM school_admin
                        LEFT JOIN school ON school_admin.school_id = school.school_id
                        WHERE school_admin.scadmin_status = 'Waiting'
                        ORDER BY school_admin.first_name, school_admin.last_name;""")
            cursor.execute(query)
            school_admin = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_pending.html', school_admin = school_admin)
#------------------Admin->Pending School Admin------------------

#------------------Admin->Peding School Admin->Approve Button------------------
@routes.route('/admin/pending_approve', methods=['GET', 'POST'])
def admin_pending_approve():
    global admin_access 
    #try:
    #if(admin_access):
    if(request.method == 'POST'):
        print("##########",)
        #Taking the object from javascript event
        approve = request.form['admin_schooladmin_approve_button']
        #Connection issues
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ("""UPDATE school_admin
                    SET scadmin_status = 'Approved', admin_id = {}
                    WHERE scadmin_id = {};""".format(int(session.get('id')), int(approve)))
        cursor.execute(query) 
        connection.commit()
        return redirect('/admin/pending') 
    #else:
    #        return redirect('/')
    '''except Exception as e:
        flash(str(e), "danger")
        abort()'''
    return render_template('admin_pending.html')
#------------------Admin->Peding School Admin->Approve Button------------------

#------------------Admin->Peding School Admin->Decline Button------------------
@routes.route('/admin/pending_decline', methods=['GET', 'POST'])
def admin_pending_decline(): 
    global admin_access
    try:
        if(admin_access):
            if(request.method == 'POST'):
                #Taking the object from javascript event, this will be a list with one element  in python
                decline = request.form['admin_schooladmin_decline_button']
                #Connection issues
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor() 
                query = ("""DELETE FROM school_admin
                            WHERE scadmin_id = {};""".format(int(decline)))
                cursor.execute(query)
                connection.commit()
                cursor.close()
                connection.close()
                return redirect('/admin/pending') 
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_pending.html')
#------------------Admin->Peding School Admin->Decline Button------------------


#----------------------Adding a school----------------------
@routes.route('/admin/schoollist/add', methods=['GET', 'POST'])
def admin_addschool():
    global admin_access
    try:
        if(admin_access):
            if (request.method == 'POST'):
                #---------Database connection------------
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
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
                                VALUES ('{}', '{}', '{}', '{}', '{}', {});""".format(school_name, city, phone_number, email, address, int(session.get("id"))))
                    cursor.execute(query)
                    connection.commit()
                    flash('School added successfully!', category='success')
                    cursor.close()
                    connection.close()
                    return redirect('/admin/schoollist')
                #------------Doing the necessary checks and inserting--------------
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()   
    return render_template('admin_addschool.html')
#----------------------Adding a school----------------------

#-----------------------Admin->question 1-----------------------
@routes.route('/admin/question_1', methods=['GET', 'POST'])
def admin_question_1():
    global admin_access, question_1
    try:
        if(admin_access):
            #----------------Filter input------------------
            which_year = request.form.get('search_year')
            if which_year is None or which_year == '':
                which_year = 0
            else:
                which_year = int(which_year)
            which_month = request.form.get('search_month')
            if which_month is None or which_month == '':
                which_month = 0
            else:
                which_month = int(which_month)
            #----------------Filter input------------------
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_1', [which_year, which_month,])
            if(cursor.rowcount == -1):
                question_1 = []
            else:
                question_1 = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()   
    return render_template('admin_question_1.html', question_1 = question_1)
#-----------------------Admin->question 1-----------------------


#-----------------------Admin->question 2-----------------------
@routes.route('/admin/question_2', methods=['GET', 'POST'])
def admin_question_2():
    global admin_access, question_2_1, question_2_2, categories
    try:
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ("SELECT DISTINCT category FROM category;")
        cursor.execute(query)
        categories = cursor.fetchall()
        categories = [' '.join(t) for t in categories]
        if(admin_access):
            #----------------Filter input------------------
            which_category = request.form.get('search_category')
            if which_category is None or which_category == '':
                which_category = ''
            else:
                which_category = str(which_category)
            #----------------Filter input------------------
            cursor.callproc('question_3_1_2_1', [which_category,])
            if(cursor.rowcount == -1):
                question_2_1 = []
            else:
                question_2_1 = cursor.fetchall()
            cursor.callproc('question_3_1_2_2', [which_category,])
            if(cursor.rowcount == -1):
                question_2_2 = []
            else:
                question_2_2 = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            cursor.close()
            connection.close()
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_question_2.html', question_2_1 = question_2_1, question_2_2 = question_2_2, categories = categories)
#-----------------------Admin->question 2-----------------------

#-----------------------Admin->question 3-----------------------
@routes.route('/admin/question_3', methods=['GET', 'POST'])
def admin_question_3():
    global admin_access, question_3
    try:
        if(admin_access):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_3')
            if (cursor.rowcount == -1):
                question_3 = []
            else:
                question_3 = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_question_3.html', question_3 = question_3)  
#-----------------------Admin->question 3-----------------------

#-----------------------Admin->question 4-----------------------
@routes.route('/admin/question_4', methods=['GET', 'POST'])
def admin_question_4():
    global admin_access, question_4
    try:
        if(admin_access):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_4')
            if (cursor.rowcount == -1):
                question_4 = []
            else:
                question_4 = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_question_4.html', question_4 = question_4)
#-----------------------Admin->question 4-----------------------


#-----------------------Admin->question 5-----------------------
@routes.route('/admin/question_5', methods=['GET', 'POST'])
def admin_question_5():
    global admin_access, question_5
    try:
        if(admin_access):
            which_year = request.form.get('search_year_same_books')
            if which_year is None or which_year == '':
                which_year = 0
            else:
                which_year = int(which_year)
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_5', [which_year,])
            if (cursor.rowcount == -1):
                question_5 = []
            else:
                question_5 = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_question_5.html', question_5 = question_5)
#-----------------------Admin->question 5-----------------------


#-----------------------Admin->question 6-----------------------
@routes.route('/admin/question_6', methods=['GET', 'POST'])
def admin_question_6():
    global admin_access, question_6
    try:
        if(admin_access):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_6')
            if (cursor.rowcount == -1):
                question_6 = []
            else:
                question_6 = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_question_6.html', question_6 = question_6)
#-----------------------Admin->question 6-----------------------


#-----------------------Admin->question 7-----------------------
@routes.route('/admin/question_7', methods=['GET', 'POST'])
def admin_question_7():
    global admin_access, question_7
    try:
        if(admin_access):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_7')
            if (cursor.rowcount == -1):
                question_7 = []
            else:
                question_7 = cursor.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), "danger")
        abort()
    return render_template('admin_question_7.html', question_7 = question_7)
#-----------------------Admin->question 7-----------------------


#----------------ADMIN TEMPLATES------------------------------------


#---------------SCHOOL ADMIN TEMPLATES------------------------------
@routes.route('/schooladmin')
def school_admin(): 
    global sadmin_access 
    sadmin_access = True
    try: 
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ("SELECT * FROM school_admin WHERE scadmin_id = {};".format(int(session.get("id"))))
        cursor.execute(query)
        aux = cursor.fetchall()
        cursor.close()
        connection.close()
        if(len(aux) == 0):
            sadmin_access = False
            return redirect("/")
    except Exception as e: 
        flash(str(e), "danger")
        abort()
    return render_template('schooladmin_firstpage.html') 

@routes.route('/schooladmin/booklist', methods = ['GET', 'POST'])
def schooladmin_booklist():
    global sadmin_access 
    #try:
    if(sadmin_access): 
        which_book = request.form.get('search_book')
        which_author = request.form.get('search_author')
        which_availability = request.form.get('search_availability')
        which_category = request.form.get('search_category')
        scadmin_id = int(session.get("id"))
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
        cursor.execute(query)
        aux = cursor.fetchall()
        school_id = int(aux[0][0])
        print(which_book)
        print(which_author)
        print(which_availability)
        print(which_category)
        if (which_book == None): 
            which_book = ''
        if (which_author == None): 
            which_author = ''
        if (which_availability == None or which_availability == ''): 
            which_availability = -1
        else:
            which_availability = int(which_availability)
        if (which_category == None): 
            which_category = ''
        cursor.callproc('booklist', [which_book, which_author, which_category, which_availability, school_id])
        if (cursor.rowcount == -1):
            books = []    
        else:
            for result in cursor.stored_results(): 
                books = result.fetchall()
                print(books)

        cursor.close()
        connection.close()
    else: 
        redirect('/')
    '''except Exception as e: 
        flash(str(e), "danger")
        abort()'''
    return render_template('schooladmin_booklist.html', books = books)

@routes.route('/schooladmin/booklist/add', methods=['GET', 'POST'])
def schooladmin_addbook():
    global sadmin_access
    #try:
    if(sadmin_access):
        if (request.method == 'POST'):
            #---------Database connection------------
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor() 
            #---------Database connection------------
            print("Post request given")
            #------------Variables we need------------
            title = request.form.get('title')
            ISBN = int(request.form.get('ISBN'))
            author_first = request.form.get('author_first')
            author_last = request.form.get('author_last')
            publisher = request.form.get('publisher')
            no_pages = int(request.form.get('page_number'))
            summary = str(request.form.get('summary'))
            language = request.form.get('language')
            keywords = request.form.get('keywords') 
            category = request.form.get('category')
            scadmin_id = int(session.get("id"))
            #------------Variables we need------------   
            #------------Doing the necessary checks and inserting--------------
            query = ("""SELECT school_id 
                        FROM school_admin
                        WHERE (school_admin.scadmin_id = {}) ;"""
                    .format(scadmin_id))
            cursor.execute(query)
            school_id = cursor.fetchall()

            print(school_id)
            query = ("""SELECT * FROM book 
                        WHERE (book.ISBN = {});"""
                        .format(ISBN))
            cursor.execute(query)
            check = cursor.fetchall()
            if( len(check) > 0):
                query = ("UPDATE book SET available = available + 1 WHERE book.ISBN = {}"
                         .format(ISBN))
                cursor.execute(query)
                connection.commit()
            else:
                query = ("""INSERT INTO book (book_title, ISBN, publisher, no_pages, summary, sprache, scadmin_id, school_id, available)
                            VALUES ('{}', {}, '{}', {}, '{}', '{}', {}, {}, 1); """
                            .format(title, ISBN, publisher, no_pages, summary, language, scadmin_id, int(school_id[0][0])))
                cursor.execute(query)
                connection.commit()
                query = ("""INSERT INTO author (first_name, last_name, ISBN)
                            VALUES ('{}', '{}', {}); """
                        .format(author_first, author_last, ISBN))
                cursor.execute(query)
                connection.commit()
                query = ("""INSERT INTO keywords (keyword, ISBN)
                            VALUES ('{}', {}); """
                        .format(keywords, ISBN))
                cursor.execute(query)
                connection.commit()
                query = ("""INSERT INTO category (category, ISBN)
                            VALUES ('{}', {}); """
                        .format(category, ISBN))
                cursor.execute(query)
                connection.commit()
                print("#######################################################################")
            flash('Book added successfully!', category='success')
            cursor.close()
            connection.close()
            return redirect('/schooladmin/booklist')
            #------------Doing the necessary checks and inserting--------------
    else:
        return redirect('/')
    '''except Exception as e:
        flash(str(e), "danger")
        abort()   '''
    return render_template('schooladmin_addbook.html')

@routes.route('/schooladmin/booklist/delete', methods=['GET', 'POST'])
def schooladmin_booklist_deleting(): 
    global sadmin_access
    #try:
    if(sadmin_access):
        if(request.method == 'POST'):
            buttonId = request.form['delete_button']
            #---------Database connection------------
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            scadmin_id = int(session.get("id")) 
            cursor = connection.cursor() 
            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])
            query = ('DELETE FROM book WHERE (ISBN = {} AND school_id = {});'.format(int(buttonId), school_id))
            cursor.execute(query)
            connection.commit()
            cursor.close()
            connection.close()
            #---------Database connection------------
            return redirect('/schooladmin/booklist')
    else:
        return redirect('/')      
    '''except Exception as e:
        flash(str(e), "danger")
        abort() '''
    return render_template('schooladmin_bookList.html')


@routes.route('/schooladmin/booklist/update', methods=['GET', 'POST'])
def schooladmin_booklist_updating(): 
    global sadmin_access
    #try:
    if(sadmin_access):
        if(request.method == 'POST'):
            #Taking the object from javascript event, this will be a list with one element  in python
            update = request.form.getlist('update_button')
            update = update[0].split(",")
            print(update)
            scadmin_id = int(session.get("id"))             
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])
            query = ("""UPDATE book 
                        SET available = {}
                        WHERE (school_id = {} AND ISBN = {});"""
                    .format(int(update[1]), school_id, int(update[0])))
            cursor.execute(query)
            connection.commit()
            cursor.close()
            connection.close()
    else:
        return redirect('/')
    '''except Exception as e:
        flash(str(e), "danger")
        abort() '''
    return render_template('schooladmin_booklist.html')

flag = True

@routes.route('/schooladmin/booklist/details', methods = ['GET', 'POST'])
def schooladmin_bookdetails():
    global sadmin_access
    global helper
    if (sadmin_access):
        print("Entering Loop")
        if (request.method == 'POST'): 
            ISBN = request.form.get('details_button')
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            scadmin_id = int(session.get("id")) 
            cursor = connection.cursor() 
            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])
            cursor.callproc('details', [ISBN, school_id])
            if (cursor.rowcount == -1):
                book = []   
            else:
                for result in cursor.stored_results(): 
                    book = result.fetchall()
                    helper = book
                    print('#################################', book)
            cursor.close()
            connection.close()
            return render_template('schooladmin_details.html', book = book)
    else: 
        return redirect('/')
    book = helper
    return render_template('schooladmin_details.html', book = book)    


@routes.route('/schooladmin/users', methods = ['GET', 'POST'])
def schooladmin_userslist():  
    global sadmin_access 
    if (sadmin_access): 
        which_user = request.form.get('search_user')
        scadmin_id = int(session.get("id"))
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
        cursor.execute(query)
        aux = cursor.fetchall()
        school_id = int(aux[0][0])
        if (which_user == None): 
            which_user = ''
        cursor.callproc('userlist', [which_user, school_id, 'Approved'])
        if (cursor.rowcount == -1):
            users = []    
        else:
            for result in cursor.stored_results(): 
                users = result.fetchall()
                print(users)

        cursor.close()
        connection.close()
    else: 
        redirect('/')
    return render_template('schooladmin_userslist.html', users = users)

@routes.route('/schooladmin/users/pending')
def schooladmin_pendingusers():
    global sadmin_access 
    if (sadmin_access): 
        which_user = request.form.get('search_user')
        scadmin_id = int(session.get("id"))
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
        cursor.execute(query)
        aux = cursor.fetchall()
        school_id = int(aux[0][0])
        if (which_user == None): 
            which_user = ''
        cursor.callproc('userlist', [which_user, school_id, 'Waiting'])
        if (cursor.rowcount == -1):
            users = []    
        else:
            for result in cursor.stored_results(): 
                users = result.fetchall()
                print(users)

        cursor.close()
        connection.close()
    else: 
        redirect('/')
    return render_template('schooladmin_pendingusers.html', users = users)

@routes.route('/schooladmin/users/approve', methods=['GET', 'POST'])
def schooladmin_approve_user():
    global sadmin_access 
    #try:
    if(sadmin_access):
        if(request.method == 'POST'):
            print("##########",)
            #Taking the object from javascript event
            approve = request.form['schooladmin_approve_user']
            #Connection issues
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            query = ("""UPDATE user
                        SET user_status = 'Approved'
                        WHERE user_id = {};""".format(int(approve)))
            cursor.execute(query) 
            connection.commit()
            return redirect('/schooladmin/users/pending') 
    else:
        return redirect('/')
        '''except Exception as e:
            flash(str(e), "danger")
            abort()'''
    return render_template('schooladmin_pendingusers.html')

@routes.route('/schooladmin/users/decline', methods=['GET', 'POST'])
def schooladmin_decline_user():
    global sadmin_access 
    #try:
    if(sadmin_access):
        if(request.method == 'POST'):
            print("##########",)
            #Taking the object from javascript event
            decline = request.form['schooladmin_decline_user']
            #Connection issues
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            query = ("""UPDATE user
                        SET user_status = 'Declined'
                        WHERE user_id = {};""".format(int(decline)))
            cursor.execute(query) 
            connection.commit()
            return redirect('/schooladmin/users/pending') 
    else:
            return redirect('/')
    '''except Exception as e:
        flash(str(e), "danger")
        abort()'''
    return render_template('schooladmin_pendingusers.html')

@routes.route('/schooladmin/users/deactivate', methods=['GET', 'POST'])
def schooladmin_deactivate_user():
    global sadmin_access 
    #try:
    if(sadmin_access):
        if(request.method == 'POST'):
            print("##########",)
            #Taking the object from javascript event
            deactivate = request.form['schooladmin_deactivate_user']
            #Connection issues
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            query = ("""UPDATE user
                        SET user_status = 'Waiting'
                        WHERE user_id = {};""".format(int(deactivate)))
            cursor.execute(query) 
            connection.commit()
            return redirect('/schooladmin/users') 
    else:
            return redirect('/')
    '''except Exception as e:
        flash(str(e), "danger")
        abort()'''
    return render_template('schooladmin_userslist.html')

@routes.route('/schooladmin/users/delete', methods=['GET', 'POST'])
def schooladmin_delete_user():
    global sadmin_access 
    #try:
    if(sadmin_access):
        if(request.method == 'POST'):
            print("##########",)
            #Taking the object from javascript event
            delete = request.form['schooladmin_delete_user']
            #Connection issues
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            query = ("""DELETE
                        FROM user
                        WHERE user_id = {};""".format(int(delete)))
            cursor.execute(query) 
            connection.commit()
            return redirect('/schooladmin/users') 
    else:
            return redirect('/')
    '''except Exception as e:
        flash(str(e), "danger")
        abort()'''
    return render_template('schooladmin_userslist.html')

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

@routes.route('/schooladmin/reviews/approve', methods = ['POST', 'GET'])
def schooladmin_approvereviews():
    global sadmin_access
    if (sadmin_access):
        scadmin_id = int(session.get("id"))
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
        cursor.execute(query)
        aux = cursor.fetchall()
        school_id = int(aux[0][0])
        query = ("""SELECT review.ISBN, book.book_title, author.first_name, author.last_name, user.first_name, user.last_name, review.txt, review.review_id
                    FROM review
                    INNER JOIN book ON review.ISBN = book.ISBN
                    INNER JOIN author ON review.ISBN = author.ISBN 
                    INNER JOIN user ON review.user_id = user.user_id 
                    WHERE ((review.review_status = 'Waiting') AND (user.school_id = {}));""".format(school_id))
        cursor.execute(query)
        reviews = cursor.fetchall()
        cursor.close()
        connection.close()
    else: 
        redirect('/')
    return render_template('schooladmin_approvereview.html', reviews = reviews)

@routes.route('/schooladmin/reviews/approve_button', methods = ['POST', 'GET'])
def schooladmin_approve_button():
    global sadmin_access
    if (sadmin_access):
        if (request.method == 'POST'):
            review_id = request.form.get('schooladmin_approve_review')
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            cursor = connection.cursor()
            query = ("""UPDATE review
                        SET review_status = 'Approved'
                        WHERE review_id = {};""".format(int(review_id)))
            cursor.execute(query)
            connection.commit()
            return redirect ('/schooladmin/reviews/approve')
    else: 
        redirect('/')
    return render_template('schooladmin_approvereview.html')

@routes.route('/schooladmin/reviews/decline_button', methods = ['POST', 'GET'])
def schooladmin_decline_button():
    global sadmin_access
    if (sadmin_access):
        if (request.method == 'POST'):
            review_id = request.form.get('schooladmin_decline_review')
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            cursor = connection.cursor()
            query = ("""UPDATE review
                        SET review_status = 'Declined'
                        WHERE review_id = {};""".format(int(review_id)))
            cursor.execute(query)
            connection.commit()
            return redirect ('/schooladmin/reviews/approve')
    else: 
        redirect('/')
    return render_template('schooladmin_approvereview.html')

@routes.route('/schooladmin/reviews/peruser')
def schooladmin_reviewperuser():
    global sadmin_access
    if (sadmin_access):
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
        cursor = connection.cursor()
        scadmin_id = int(session.get("id"))
        query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
        cursor.execute(query)
        aux = cursor.fetchall()
        school_id = int(aux[0][0])
        query = ("""SELECT user.first_name, user.last_name, review.likert
                    FROM review
                    INNER JOIN user ON review.user_id = user.user_id
                    INNER JOIN book ON review.ISBN = book.ISBN
                    WHERE ((book.school_id = {}) AND (review.review_status = 'Approved'));""".format(int(school_id)))
        cursor.execute(query)
        reviews = cursor.fetchall()
        cursor.close()
        connection.close()
    return render_template('schooladmin_reviewperuser.html', reviews = reviews)

@routes.route('/schooladmin/reviews/percategory')
def schooladmin_reviewpercategory():
    global sadmin_access
    if (sadmin_access):
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
        cursor = connection.cursor()
        scadmin_id = int(session.get("id"))
        query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
        cursor.execute(query)
        aux = cursor.fetchall()
        school_id = int(aux[0][0])
        query = ("""SELECT category.category, review.likert
                    FROM review
                    INNER JOIN category ON review.ISBN = category.ISBN
                    INNER JOIN book ON review.ISBN = book.ISBN
                    WHERE ((book.school_id = {}) AND (review.review_status = 'Approved'));""".format(int(school_id)))
        cursor.execute(query)
        reviews = cursor.fetchall()
        cursor.close()
        connection.close()
    return render_template('schooladmin_reviewpercategory.html', reviews = reviews)
#-----------------SCHOOL ADMIN TEMPLATES-------------------------------