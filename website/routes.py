from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import re
import mysql.connector as sql
from datetime import datetime, timedelta
import os
import threading, time
import base64
from statistics import mean
import subprocess
from website.credentials import host_config, password_config, database_config, user_config
import yaml

routes = Blueprint('routes', __name__)
global checked, checkedr, avail, availr
checked = -1
checkedr = -1
avail = -1
availr = -1

#----------------------------------HOME PAGE/LOG IN----------------------------------
@routes.route('/')
def index(): 
    session['admin_access'] = False
    session['sadmin_access'] = False
    session['user_access'] = False
    session['connected'] = False
    session['id'] = -1
    directory = '/static/library.jpg'
    return render_template('home_page.html', image = directory ,pageTitle = "Welcome!")


@routes.route('/', methods = ['GET', 'POST'])
def login():
    try:
        if (request.method == 'POST'):
            login = request.form.get('login')
            password = request.form.get('password')
            role = str(request.form.get('Role'))
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor() 
            if(role == 'Student' or role == 'Teacher'):
                query = ("SELECT user_id FROM user WHERE (login_id = '{}' AND passwd = '{}' AND job = '{}' AND user_status = 'Approved');".format(login, password, role))
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
                query = ("SELECT scadmin_id FROM school_admin WHERE (login_id = '{}' AND passwd = '{}' AND scadmin_status = 'Approved');".format(login, password))
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
                query = ("SELECT admin_id FROM administrator WHERE (login_id = '{}' AND passwd = '{}');".format(login, password))
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
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('home_page.html')
#----------------------------------HOME PAGE/LOG IN----------------------------------


#----------------------------------LOG OUT----------------------------------
@routes.route('/logout', methods = ['GET', 'POST'])
def logout():
    try:
        if(session.get("connected") == True):
            session['connected'] = False
            session['id'] = -1  
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
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
            email = request.form.get('sign_login')
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
            if (v_birth_date == True):
                flash('Invalid date', category = 'error')
            elif (v_user == False and v_school_admin == False):
                flash('This email is already occupied', category = 'error')
            elif len(firstName) < 2 or len(lastName) < 2:
                flash('First and last names must be greater than 1 characters.', category = 'error')
            elif (password1 != password2):
                flash('Passwords don\'t match.', category='error')
            elif not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password1):
                flash('Password is too weak! Use a password of at least 8 characters. Must be restricted to uppercase, lowercase letters, numbers, any special character.', category = 'error')
            else:
                if(role == 'Student' or role == 'Teacher'):
                    query = ("""INSERT INTO user (login_id, passwd, first_name, last_name, birth_date, school_id, job, books_borrowed, user_status, sex) 
                            VALUES ('{}', '{}', '{}', '{}', '{}', {}, '{}', 0, 'Waiting', '{}');""".format(email, password2, firstName, lastName, str(dob), int(school_id[0][0]), role, sex))
                else:
                    query = ("""INSERT INTO school_admin (login_id, passwd, first_name, last_name, sex, birth_date, scadmin_status, school_id)
                            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', 'Waiting', {});""".format(email, password2, firstName, lastName, sex, str(dob), int(school_id[0][0])))
                cursor.execute(query)
                connection.commit()
                cursor.close()
                connection.close()
                flash('Account created successfully!Please wait to be approved', category='success')
                return redirect('/')
            cursor.close()
            connection.close()
            return redirect('/sign-up')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template("sign_up.html", school = schools)
#----------------------------------SIGN UP----------------------------------



#---------------------USER TEMPLATES-------------------------
#----------------------------User first page------------------------------------
@routes.route('/user', methods = ['GET', 'POST'])
def user(): 
    try:
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ("SELECT * FROM user WHERE user_id = {};".format(int(session.get("id"))))
        cursor.execute(query)
        aux = cursor.fetchall()
        cursor.close()
        connection.close()
        session['user_access'] = True
        if len(aux) == 0:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')

    return render_template('user_firstpage.html')
#----------------------------User first page------------------------------------

#----------------------------User books------------------------------------
@routes.route('/user/booksearch', methods = ['GET', 'POST'])
def user_booklist():
    global books
    try:
        if(session['user_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            cursor = connection.cursor()

            which_title = request.form.get('title')
            which_author_name = request.form.get('author')
            which_category = request.form.get('category')

            user_id = int(session['id'])
            query = ('SELECT school_id FROM user WHERE user_id = {};'.format(user_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            if which_title == None:
                which_title = ''
            if which_author_name == None:
                which_author_name = ''
            if which_category == None:
                which_category = ''

            cursor.callproc('search_book', [which_title, which_author_name, which_category, school_id])

            books = []
            for result in cursor.stored_results():
                books = result.fetchall()
            
            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('user_booksearch.html', books = books)
#----------------------------User books------------------------------------

#-----------------------------User borrow----------------------------------
@routes.route('/user/booksearch/borrow', methods = ['GET', 'POST'])
def user_borrow():
    try:
        if(session['user_access']):
            if(request.method == 'GET'):
                flash('Your borrowing request will be processed', category = 'warning')
            elif(request.method == 'POST'):
                ISBN = request.form.get('borrow_button')

                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
                cursor = connection.cursor()

                user_id = int(session.get("id")) 
                query = ('SELECT school_id FROM user WHERE user_id = {};'.format(user_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                school_id = int(aux[0][0])

                query = ('SELECT scadmin_id FROM school_admin WHERE school_id = {} LIMIT 1;'.format(school_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                scadmin_id = int(aux[0][0])

                query = ("""INSERT INTO borrowing (ISBN, user_id, borrowing_status, scadmin_id)
                            VALUES ('{}', {}, 'Waiting', {});""".format(ISBN, user_id, scadmin_id))
                cursor.execute(query)
                connection.commit()

                cursor.close()
                connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/user/booksearch')
#-----------------------------User borrow----------------------------------

#------------------------------------------------User reserve---------------------------------------------------------------
@routes.route('/user/booksearch/reserve_aux', methods = ['GET', 'POST'])
def user_reserve_aux():
    global gamietai_to_werkzeug
    try:
        if(session['user_access']):
            if (request.method == 'POST'):
                gamietai_to_werkzeug = request.form.get('reserve_button')
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/user/booksearch/reserve')

@routes.route('/user/booksearch/reserve', methods = ['GET', 'POST'])
def user_reserve():
    global gamietai_to_werkzeug
    try:
        if(session['user_access']):
            if(request.method == 'POST'):
                reserve_to_date = request.form.get('reserve_to_date')

                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
                cursor = connection.cursor()

                user_id = int(session.get("id")) 
                query = ('SELECT school_id FROM user WHERE user_id = {};'.format(user_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                school_id = int(aux[0][0])

                query = ('SELECT scadmin_id FROM school_admin WHERE school_id = {} LIMIT 1;'.format(school_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                scadmin_id = int(aux[0][0])

                query = ("""INSERT INTO reservation (ISBN, user_id, reservation_to_date, reservation_status, scadmin_id)
                            VALUES ('{}', {}, '{}', 'Waiting', {});""".format(gamietai_to_werkzeug, user_id, reserve_to_date, scadmin_id))
                cursor.execute(query)
                connection.commit()

                flash('Your reservation request will be processed', category = 'warning')

                cursor.close()
                connection.close()
                gamietai_to_werkzeug = None
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/user/booksearch')
#----------------------------------------User reserve---------------------------------------------------------------


#-----------------------------User book list->Details button and template---------------------------------    

@routes.route('/user/booksearch/details_aux', methods = ['GET', 'POST'])
def details_submit_isbn():
    global book1, image_source1, details_submit_isbn, authors1, keywords1, categories1
    try:
        if(session['user_access']):
            if(request.method == 'POST'):
                details_submit_isbn = str(request.form['details_button'])
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
                cursor = connection.cursor() 

                user_id = int(session.get("id")) 
                query = ('SELECT school_id FROM user WHERE user_id = {};'.format(user_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                school_id = int(aux[0][0])

                query = ("""SELECT author.first_name, author.last_name, author.ISBN 
                            FROM author 
                            INNER JOIN book ON author.ISBN = book.ISBN
                            WHERE author.ISBN = '{}' AND book.school_id = {};""".format(details_submit_isbn, school_id))
                cursor.execute(query)
                authors1 = cursor.fetchall()

                query = ("""SELECT keyword, keywords.ISBN 
                            FROM keywords
                            INNER JOIN book ON keywords.ISBN = book.ISBN
                            WHERE keywords.ISBN = '{}' AND book.school_id = {};""".format(details_submit_isbn, school_id))
                cursor.execute(query)
                keywords1 = cursor.fetchall()

                query = ("""SELECT category, category.ISBN 
                            FROM category
                            INNER JOIN book ON category.ISBN = book.ISBN
                            WHERE category.ISBN = '{}' AND book.school_id = {};""".format(details_submit_isbn, school_id))
                cursor.execute(query)
                categories1 = cursor.fetchall() 

                cursor.callproc('details', [details_submit_isbn, school_id])
                book1 = []   
                for result in cursor.stored_results(): 
                    book1 = result.fetchall()
                    image_source1 = ''
                    if (book1[0][10] != '' and type(book1[0][10])!= type(None)):
                        decoded_image = base64.b64decode(book1[0][10])
                        image_source1 = "data:image/jpeg;base64," + base64.b64encode(decoded_image).decode('utf-8')
                cursor.close()
                connection.close()
                details_submit_isbn = None
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/user/booksearch/details')

@routes.route('/user/booksearch/details', methods = ['GET', 'POST'])
def user_bookdetails():
    global book1, image_source1, authors1, keywords1, categories1
    try:
        if(session['user_access']):
            return render_template('user_details.html', book = book1, image_source = image_source1, authors = authors1, categories = categories1, keywords = keywords1)
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')  
#-----------------------------User book list->Details button and template---------------------------------    

#-----------------------------User book list->Review button and template---------------------------------
@routes.route('/submit_isbn', methods = ['GET','POST'])
def submit_isbn():
    global book_global_code
    try:
        if(session['user_access']):
            if request.method == 'POST':
                book_global_code = str(request.form['writereview_button'])
        else:
            return redirect('/')
        return redirect('/user/booksearch/review')
    
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/') 
   
@routes.route('/user/booksearch/review', methods = ['GET', 'POST'])
def review():
    global books, book_global_code
    try:
        if(session['user_access']):
            if request.method == 'POST':
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
                cursor = connection.cursor()
                user_id = int(session['id'])

                query = ('SELECT school_id FROM user WHERE user_id = {};'.format(user_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                school_id = int(aux[0][0])

                question1 = request.form.get('Book1')
                question2 = request.form.get('Book2')
                question3 = request.form.get('Book3')
                question4 = request.form.get('Book4')
                question5 = request.form.get('Book5')
                review = request.form.get('review')

                if review == '':
                    flash ('You need to write a review for this book.', category = 'error')
                    return redirect('/user/booksearch/review')
                
                query = ("SELECT job FROM user WHERE user_id = {}".format(user_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                role = str(aux[0][0])
                likert = question1 + question2 + question3 + question4 + question5

                print(book_global_code + "kosakodosakdosakdoak(*!(&(*@^!(*#!&))))")
                if role == 'Student':
                    query = ("INSERT INTO review (ISBN, user_id, txt, likert, review_status, school_id) VALUES ('{}', {}, '{}', '{}', 'Waiting', {})".format(book_global_code, user_id, review, likert, school_id))
                else:
                    query = ("INSERT INTO review (ISBN, user_id, txt, likert, review_status, school_id) VALUES ('{}', {}, '{}', '{}', 'Approved', {})".format(book_global_code, user_id, review, likert, school_id))  
                
                cursor.execute(query)
                connection.commit()

                if role == 'Student':
                    flash("Review registered successfully. Waiting for permission to post...", category = 'success')
                else:
                    flash("Review registered and posted successfully!", category = 'success')
                book_global_code = None
                return redirect('/user/booksearch')
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/') 
    return render_template('review_form.html')
#-----------------------------User book list->Review button and template---------------------------------

#--------------------------------user->My Books->Waiting Borrowings List--------------------------------
@routes.route('/user/books/borrowings/waiting', methods = ['GET', 'POST'])
def userooks_borrowingwaitings():
    try:
        if(session['user_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            cursor = connection.cursor()

            user_id = int(session.get("id"))

            query = ("""SELECT book.ISBN, book.book_title, author.first_name, author.last_name, borrowing_date
                        FROM borrowing
                        INNER JOIN book ON borrowing.ISBN = book.ISBN
                        INNER JOIN author ON author.ISBN = book.ISBN
                        WHERE (borrowing.user_id = {} AND borrowing_status = 'Waiting')
                        GROUP BY borrowing_id;""".format(user_id))
            cursor.execute(query)
            books_waiting = cursor.fetchall()

            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash("An error occured: " + str(e), category = 'error')
        return redirect('/')
    return render_template('user_books_borrowings_waiting.html', books_waiting = books_waiting)
#--------------------------------user->My Books->Waiting Borrowings List--------------------------------

#--------------------------------user->My Books->Waiting Reservations List--------------------------------
@routes.route('/user/books/reservations/waiting', methods = ['GET', 'POST'])
def userooks_reservationwaitings():
    try:
        if(session['user_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            cursor = connection.cursor()

            user_id = int(session.get("id"))

            query = ("""SELECT book.ISBN, book.book_title, author.first_name, author.last_name, reservation_date, reservation_id, reservation_to_date
                        FROM reservation
                        INNER JOIN book ON reservation.ISBN = book.ISBN
                        INNER JOIN author ON author.ISBN = book.ISBN
                        WHERE (reservation.user_id = {} AND (reservation_status = 'Waiting' OR reservation_status = 'Approved'))
                        GROUP BY reservation_id;""".format(user_id))
            cursor.execute(query)
            reservation_waiting = cursor.fetchall()

            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('user_books_reservations_waiting.html', reservation_waiting = reservation_waiting, queing = True)
#--------------------------------user->My Books->Waiting Reservations List--------------------------------

#--------------------------------user->My Books->Waiting Reservations List->Cancel Reservation Button--------------------------------
@routes.route('/user/books/reservations/waiting_cancel', methods = ['GET', 'POST'] )
def userooks_reservationwaitings_cancel():
    try:
        if(session['user_access']):
            if(request.method == 'GET'):
                flash('Reservation canceled', category = 'error')
            elif(request.method == 'POST'):    
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
                cursor = connection.cursor()

                cancel = int(request.form['cancel_reservation'])

                query = ("DELETE FROM reservation WHERE reservation_id = {};".format(cancel))
                cursor.execute(query)
                connection.commit()

                cursor.close()
                connection.close()
        else:
            return redirect('/')

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/user/books/reservations/waiting')
#--------------------------------user->My Books->Waiting Reservations List->Cancel Reservation Button--------------------------------

#--------------------------------user->My Books->Waiting Queue Reservations List--------------------------------
@routes.route('/user/books/reservations/waitingqueue', methods = ['GET', 'POST'])
def userooks_reservationwaitings_queue():
    try:
        if(session['user_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            cursor = connection.cursor()

            user_id = int(session.get("id"))

            query = ("""SELECT book.ISBN, book.book_title, author.first_name, author.last_name, reservation_date, reservation_id, reservation_to_date
                        FROM reservation
                        INNER JOIN book ON reservation.ISBN = book.ISBN
                        INNER JOIN author ON author.ISBN = book.ISBN
                        WHERE (reservation.user_id = {} AND reservation_status = 'Waiting Queue')
                        GROUP BY reservation_id;""".format(user_id))
            cursor.execute(query)
            reservation_waitingqueue = cursor.fetchall()

            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('user_books_reservations_waiting.html', reservation_waiting = reservation_waitingqueue, queing = False)
#--------------------------------user->My Books->Waiting Queue Reservations List--------------------------------

#--------------------------------user->My Books->Approved Borrowings List--------------------------------
@routes.route('/user/books/borrowings/approved', methods = ['GET', 'POST'])
def userooks_borrowingapprove():
    try:
        if(session['user_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            cursor = connection.cursor()

            user_id = int(session.get("id"))

            query = ("""SELECT book.ISBN, book.book_title, author.first_name, author.last_name, borrowing_date
                        FROM borrowing
                        INNER JOIN book ON borrowing.ISBN = book.ISBN
                        INNER JOIN author ON author.ISBN = book.ISBN
                        WHERE (borrowing.user_id = {} AND borrowing_status = 'Approved')
                        GROUP BY borrowing_id;""".format(user_id))
            cursor.execute(query)
            books_approved = cursor.fetchall()

            cursor.close()
            connection.close()
        else:
            return redirect('/')
        
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('user_books_borrowing_approve.html', books_approved = books_approved)
#--------------------------------user->My Books->Approved Borrowings List--------------------------------

#--------------------------------user profile view--------------------------------
@routes.route('/user/profile', methods = ['GET', 'POST'])
def profile():
    try:
        if(session['user_access']):
            user_id = int(session.get("id"))
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor() 
            query = ("""SELECT user.first_name, user.last_name, user.job, user.birth_date, school.school_name, user.login_id, user.user_id 
                        FROM user
                        INNER JOIN school ON user.school_id = school.school_id
                        WHERE user.user_id = {};""".format(user_id))
            cursor.execute(query)
            user = cursor.fetchall()

            if (user[0][2] == 'Student'):
                return render_template('user_profile_student.html', user = user)
            else:
                return render_template('user_profile_teacher.html', user = user)
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')

#--------------------------------user profile view--------------------------------

#--------------------------------user profile view->update button--------------------------------
@routes.route('/user/profile/update', methods = ['GET', 'POST'])
def profile_update():
    try:
        if(session['user_access']):
            if (request.method == 'POST'):
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor() 
                user_now= request.form.getlist('update_button')
                user_now = user_now[0].split(",")
                query = ("SELECT * FROM user WHERE login_id = '{}' AND user_id != {};".format(user_now[3], int(session.get("id"))))
                cursor.execute(query)
                aux = cursor.fetchall()
                if(len(aux) == 0):
                    query = ("""UPDATE user
                                SET first_name = '{}', last_name = '{}',  login_id = '{}' 
                                WHERE user_id = {};""".format(user_now[1], user_now[2], user_now[3], user_now[0]))
                    cursor.execute(query)
                    connection.commit()
                else:
                    flash('This login id is already being used', category='error')
                cursor.close()
                connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect("/user/profile")
#--------------------------------user profile view->update button--------------------------------

#--------------------------------user My reviews--------------------------------
@routes.route('/user/reviews', methods = ['GET', 'POST'])
def user_reviews():
    try:
        if(session['user_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            cursor = connection.cursor()

            user_id = int(session.get("id"))

            query = ("""SELECT book.ISBN, book.book_title, author.first_name, author.last_name, book.publisher, review_date, review_id
                        FROM review
                        INNER JOIN book ON review.ISBN = book.ISBN
                        INNER JOIN author ON author.ISBN = book.ISBN
                        WHERE (review.user_id = {} AND review_status = 'Approved')
                        GROUP BY review_id;""".format(user_id))
            cursor.execute(query)
            reviews = cursor.fetchall()

            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('user_reviews.html', reviews = reviews)
#--------------------------------user My reviews--------------------------------

#--------------------------------user->My reviews->Details Button-------------------------
@routes.route('/user/booksearch/reviewdetails_aux', methods = ['GET', 'POST'])
def user_myreviews_details_aux():
    global likert, review_text
    try:
        if(session['user_access']):
            if (request.method == 'POST'):
                reviewId = request.form['reviewdetails_button']
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
                cursor = connection.cursor()

                query = ("SELECT likert, txt FROM review WHERE review_id = {};".format(reviewId))
                cursor.execute(query)
                reviews = cursor.fetchall()
                reviews = reviews[0]
                likert = [int(x) for x in reviews[0]]
                review_text = reviews[1]

                cursor.close()
                connection.close()
        else:
            return redirect('/')

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/user/booksearch/reviewdetails')


@routes.route('/user/booksearch/reviewdetails', methods = ['GET', 'POST'])
def user_myreviews_details():
    global likert, review_text
    try:
        if(session['user_access']):
            return render_template('review_form_view.html', likert = likert, review_text = review_text)
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
#--------------------------------user->My reviews->Details Button-------------------------
#-----------------USER TEMPLATES-------------------------------------


#-----------------ADMIN TEMPLATES-----------------------------------
#---------------------Admin initialization--------------------------
@routes.route('/admin')
def admin(): 
    try:
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ("SELECT * FROM administrator WHERE admin_id = {};".format(int(session.get("id"))))
        cursor.execute(query)
        aux = cursor.fetchall()
        cursor.close()
        connection.close()
        session['admin_access'] = True
        if(len(aux) == 0):
            return redirect("/")
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/') 
    return render_template('admin_firstpage.html')
#---------------------Admin initialization--------------------------


#------------------Admin->School List------------------
@routes.route('/admin/schoollist', methods=['GET', 'POST'])
def admin_schoollist(): 
    try:
        if(session['admin_access']):
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
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('admin_schoolList.html', school = school)
#------------------Admin->School List------------------

#------------------Admin->School List->Delete Button------------------
@routes.route('/admin_schoollist_delete', methods=['GET', 'POST'])
def admin_schoollist_deleting(): 
    try:
        if(session['admin_access']):
            if(request.method == 'GET'):
                flash('School Deleted', category = 'error')
            elif(request.method == 'POST'):
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
        flash(str(e), category = 'error')
        return redirect('/')   
    return redirect('/admin/schoollist')
#------------------Admin->School List->Delete Button------------------

#------------------Admin->School List->Update Button------------------
@routes.route('/admin_schoollist_update', methods=['GET', 'POST'])
def admin_schoollist_updating(): 
    global auxiliary_flash
    try:    
        if(session['admin_access']):
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
                auxiliary_flash = cursor.fetchall()
                if(len(auxiliary_flash) != 0):
                    flash('One of the updated elements exists in another school. Please try again', category='error')
                else:
                    flash('School Updated', category = 'success')
                if(len(auxiliary_flash) == 0):
                    query = ("""UPDATE school
                                SET school_name = '{}', city = '{}', phone_number = '{}', email = '{}', addrss = '{}'
                                WHERE school_id = {};""".format(update[0], update[1], update[3], update[4], update[2], int(update[5])))
                    cursor.execute(query)
                    connection.commit()
                
                cursor.close()
                connection.close()
                return redirect('/admin/schoollist')
        else:
            return redirect('/')    
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/admin/schoollist')
#------------------Admin->School List->Update Button------------------



#------------------Admin->See approved School Admins------------------
@routes.route('/admin/show_admins', methods=['GET', 'POST'])
def admin_pending_see(): 
    try:
        if(session['admin_access']):
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
            return redirect('/')    
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('admin_aproved_pending.html', school_admin = school_admin)
#------------------Admin->See approved School Admins------------------

#------------------Admin->Pending School Admin------------------
@routes.route('/admin/pending', methods=['GET', 'POST'])
def admin_pending(): 
    try:
        if(session['admin_access']):
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
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('admin_pending.html', school_admin = school_admin)
#------------------Admin->Pending School Admin------------------

#------------------Admin->Peding School Admin->Approve Button------------------
@routes.route('/admin/pending_approve', methods=['GET', 'POST'])
def admin_pending_approve():
    try:
        if(session['admin_access']):
            if(request.method == 'GET'):
                flash('School Admin Approved', category = 'success')
            elif(request.method == 'POST'):
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
        else:
            return redirect('/') 
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/admin/pending') 
#------------------Admin->Peding School Admin->Approve Button------------------

#------------------Admin->Peding School Admin->Decline Button------------------
@routes.route('/admin/pending_decline', methods=['GET', 'POST'])
def admin_pending_decline(): 
    try:
        if(session['admin_access']):
            if(request.method == 'GET'):
                flash('School Admin Declined', category = 'error')
            elif(request.method == 'POST'):
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
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/admin/pending') 
#------------------Admin->Peding School Admin->Decline Button------------------


#----------------------Adding a school----------------------
@routes.route('/admin/schoollist/add', methods=['GET', 'POST'])
def admin_addschool():
    try:
        if(session['admin_access']):
            if (request.method == 'POST'):
                #---------Database connection------------
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor() 
                #---------Database connection------------
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
        flash(str(e), category = 'error')
        return redirect('/')   
    return render_template('admin_addschool.html')
#----------------------Adding a school----------------------

#-----------------------Admin Restore----------------------------
@routes.route('/admin/restore', methods = ['GET', 'POST'])
def restore():
    try:    
        if(session['admin_access']):
            DB_HOST = host_config
            DB_USER = user_config
            DB_NAME = database_config
            DB_PASSWORD = password_config
            FOLDERS = os.listdir('./database/backup')
            
            FOLDERS.sort()
            BACKUP_PATH = os.path.join('./database/backup/', FOLDERS[-1] + '/librarydbms.sql')

            DROP_PREV_BACKUP = f'mysql -u {DB_USER} -p{DB_PASSWORD} -e "DROP DATABASE IF EXISTS librarydbms_backup;"'
            subprocess.call(DROP_PREV_BACKUP, shell=True)

            CREATE_NEW_DB = f'mysql -u {DB_USER} -p{DB_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS librarydbms_backup;"'
            subprocess.call(CREATE_NEW_DB, shell=True)

            COMMAND = f"mysql -h {DB_HOST} -u {DB_USER} -p{DB_PASSWORD} librarydbms_backup < {BACKUP_PATH}"
            os.system(COMMAND)
            flash("Database restored successfully!", category = 'success')

            current_dir = os.path.dirname(os.path.abspath(__file__))
            yaml_file_path = os.path.join(current_dir, "../data.yaml")

            with open(yaml_file_path, 'r') as file:
                data = yaml.safe_load(file)
            
            data['database'] = 'librarydbms_backup'

            with open(yaml_file_path, 'w') as file:
                yaml.safe_dump(data, file)

            return redirect('/admin')
        else:
            return redirect('/')
    
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
#-----------------------Admin Restore----------------------------

#-----------------------Admin Create Backup----------------------------
@routes.route('/admin/backup', methods = ['GET', 'POST'])
def create_backup():
    try:
        if(session['admin_access']):
            DB_HOST = host_config
            DB_USER = user_config
            DB_NAME = database_config
            DB_PASSWORD = password_config
            BACKUP_PATH = './database/backup'

            # Getting current DateTime to create the separate backup folder like "20180817-123433".
            DATETIME = time.strftime('%Y%m%d-%H%M%S')
            TODAYBACKUPPATH = BACKUP_PATH + '/' + DATETIME
            
            try:
                os.stat(TODAYBACKUPPATH)
            except:
                os.makedirs(TODAYBACKUPPATH,exist_ok=True)

            dumpcmd = (
                    f'mysqldump --host={DB_HOST} --user={DB_USER} --password={DB_PASSWORD} '
                    f'{DB_NAME} > {os.path.join(TODAYBACKUPPATH, DB_NAME + ".sql")}'
                )
            subprocess.call(dumpcmd, shell=True)
            os.system(dumpcmd)
            flash('Backup created', category = 'success')
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('admin_firstpage.html')
#-----------------------Admin Create Backup----------------------------

#-----------------------Admin->question 1-----------------------
@routes.route('/admin/question_1', methods=['GET', 'POST'])
def admin_question_1():
    global question_1
    try:
        if(session['admin_access']):
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
            results = cursor.stored_results()
            question_1 = []
            for result in results:
                question_1 = result.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')   
    return render_template('admin_question_1.html', question_1 = question_1)
#-----------------------Admin->question 1-----------------------


#-----------------------Admin->question 2-----------------------
@routes.route('/admin/question_2', methods=['GET', 'POST'])
def admin_question_2():
    global question_2_1, question_2_2, categories
    try:
        if(session['admin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            query = ("SELECT DISTINCT category FROM category;")
            cursor.execute(query)
            categories = cursor.fetchall()
            categories = [' '.join(t) for t in categories]
            #----------------Filter input------------------
            which_category = request.form.get('search_category')
            if which_category is None or which_category == '':
                which_category = ''
            else:
                which_category = str(which_category)
            #----------------Filter input------------------
            cursor.callproc('question_3_1_2_1', [which_category,])
            results = cursor.stored_results()
            question_2_1 = []
            for result in results:
                question_2_1 = result.fetchall()

            cursor.callproc('question_3_1_2_2', [which_category,])
            results = cursor.stored_results()
            question_2_2 = []
            for result in results:
                question_2_2 = result.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/') 
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('admin_question_2.html', question_2_1 = question_2_1, question_2_2 = question_2_2, categories = categories)
#-----------------------Admin->question 2-----------------------

#-----------------------Admin->question 3-----------------------
@routes.route('/admin/question_3', methods=['GET', 'POST'])
def admin_question_3():
    global question_3
    try:
        if(session['admin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_3')
            results = cursor.stored_results()
            question_3 = []
            for result in results:
                question_3 = result.fetchall()
            print(question_3)
            cursor.close()
            connection.close()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('admin_question_3.html', question_3 = question_3)  
#-----------------------Admin->question 3-----------------------

#-----------------------Admin->question 4-----------------------
@routes.route('/admin/question_4', methods=['GET', 'POST'])
def admin_question_4():
    global question_4
    try:
        if(session['admin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_4')
            results = cursor.stored_results()
            question_4 = []
            for result in results:
                question_4 = result.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/') 
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('admin_question_4.html', question_4 = question_4)
#-----------------------Admin->question 4-----------------------


#-----------------------Admin->question 5-----------------------
@routes.route('/admin/question_5', methods=['GET', 'POST'])
def admin_question_5():
    global question_5
    try:
        if(session['admin_access']):
            which_year = request.form.get('search_year_same_books')
            if which_year is None or which_year == '':
                which_year = 0
            else:
                which_year = int(which_year)
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_5', [which_year,])
            results = cursor.stored_results()
            question_5 = []
            for result in results:
                question_5 = result.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('admin_question_5.html', question_5 = question_5)
#-----------------------Admin->question 5-----------------------


#-----------------------Admin->question 6-----------------------
@routes.route('/admin/question_6', methods=['GET', 'POST'])
def admin_question_6():
    global question_6
    try:
        if(session['admin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_6')
            results = cursor.stored_results()
            question_6 = []
            for result in results:
                question_6 = result.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/') 
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('admin_question_6.html', question_6 = question_6)
#-----------------------Admin->question 6-----------------------


#-----------------------Admin->question 7-----------------------
@routes.route('/admin/question_7', methods=['GET', 'POST'])
def admin_question_7():
    global question_7
    try:
        if(session['admin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()
            cursor.callproc('question_3_1_7')
            results = cursor.stored_results()
            question_7 = []
            for result in results:
                question_7 = result.fetchall()
            cursor.close()
            connection.close()
        else:
            return redirect('/') 
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('admin_question_7.html', question_7 = question_7)
#-----------------------Admin->question 7-----------------------


#----------------ADMIN TEMPLATES------------------------------------


#---------------SCHOOL ADMIN TEMPLATES------------------------------
#-----------------------School Admin first page-----------------------
@routes.route('/schooladmin')
def school_admin(): 
    try: 
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ("SELECT * FROM school_admin WHERE scadmin_id = {};".format(int(session.get("id"))))
        cursor.execute(query)
        aux = cursor.fetchall()
        cursor.close()
        connection.close()
        session['sadmin_access'] = True
        if(len(aux) == 0):
            return redirect("/")
    except Exception as e: 
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('schooladmin_firstpage.html') 
#-----------------------School Admin first page-----------------------

#-----------------------School Admin book list-----------------------
@routes.route('/schooladmin/booklist', methods = ['GET', 'POST'])
def schooladmin_booklist(): 
    try:
        if(session['sadmin_access']):
            which_book = request.form.get('search_book')
            which_author = request.form.get('search_author')
            which_availability = request.form.get('search_availability')
            which_category = request.form.get('search_category')

            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()

            scadmin_id = int(session.get("id"))
            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

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
            books = []    
            for result in cursor.stored_results(): 
                books = result.fetchall()

            cursor.close()
            connection.close()
            return render_template('schooladmin_booklist.html', books = books)
        else:
            return redirect('/') 

    except Exception as e: 
        flash(str(e), category = 'error')
        return redirect('/')
#-----------------------School Admin book list-----------------------

#-----------------------School Admin add book-----------------------
@routes.route('/schooladmin/booklist/add', methods=['GET', 'POST'])
def schooladmin_addbook():
    try:
        if(session['sadmin_access']):
            if (request.method == 'POST'):
                #---------Database connection------------
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor() 
                #---------Database connection------------
                title = request.form.get('title')
                ISBN = str(request.form.get('ISBN'))
                publisher = request.form.get('publisher')
                no_pages = int(request.form.get('page_number'))
                summary = str(request.form.get('summary'))
                language = request.form.get('language')

                author_first = request.form.get('author_first')
                author_first = author_first.split(', ')
                author_last = request.form.get('author_last')
                author_last = author_last.split(', ')
                listing = []
                for i in range(len(author_first)):
                    aux = (author_first[i], author_last[i])
                    listing.append(aux)
                
                keywords = request.form.get('keywords')
                keywords = keywords.split(', ')

                category = request.form.get('category')
                category = category.split(', ')

                image = request.files['cover']
                image_data = image.read()
                binary_data = base64.b64encode(image_data).decode('utf-8')

                scadmin_id = int(session.get("id")) 
                query = ("""SELECT school_id 
                            FROM school_admin
                            WHERE (school_admin.scadmin_id = {});"""
                        .format(scadmin_id))
                cursor.execute(query)
                school_id = cursor.fetchall()

                query = ("""SELECT * FROM book 
                            WHERE (book.ISBN = '{}');"""
                            .format(ISBN))
                cursor.execute(query)
                check = cursor.fetchall()
                if( len(check) > 0):
                    query = ("UPDATE book SET available = available + 1 WHERE book.ISBN = '{}';"
                            .format(ISBN))
                    cursor.execute(query)
                    connection.commit()
                    flash('Book already exists, throguh this action 1 more copy from this book was added', category='error')
                else:
                    query = ("""INSERT INTO book (book_title, ISBN, publisher, no_pages, summary, sprache, scadmin_id, school_id, available, img)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, %s); """)
                    cursor.execute(query, (title, ISBN, publisher, no_pages, summary, language, scadmin_id, int(school_id[0][0]), binary_data))
                    connection.commit()

                    for i in listing:
                        query = ("""INSERT INTO author (first_name, last_name, ISBN)
                                    VALUES ('{}', '{}', '{}'); """
                                .format(i[0], i[1], ISBN))
                        cursor.execute(query)
                        connection.commit()

                    for i in keywords:
                        query = ("""INSERT INTO keywords (keyword, ISBN)
                                    VALUES ('{}', '{}'); """
                                .format(i, ISBN))
                        cursor.execute(query)
                        connection.commit()

                    for i in category:
                        query = ("""INSERT INTO category (category, ISBN)
                                    VALUES ('{}', '{}'); """
                                .format(i, ISBN))
                        cursor.execute(query)
                        connection.commit()
                    flash('Book added successfully!', category='success')
                cursor.close()
                connection.close()
                return redirect('/schooladmin/booklist')
                #------------Doing the necessary checks and inserting--------------
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')  
    return render_template('schooladmin_addbook.html')
#-----------------------School Admin add book-----------------------

#-----------------------School Admin book->Delete button-----------------------
@routes.route('/schooladmin/booklist/delete', methods=['GET', 'POST'])
def schooladmin_booklist_deleting(): 
    try:
        if(session['sadmin_access']):
            if(request.method == 'GET'):
                flash('Book deleted', category = 'error')
            elif(request.method == 'POST'):
                buttonId = request.form['delete_button']

                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
                cursor = connection.cursor() 
                scadmin_id = int(session.get("id")) 

                query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                school_id = int(aux[0][0])

                query = ("DELETE FROM book WHERE (ISBN = '{}' AND school_id = {});".format(buttonId, school_id))
                cursor.execute(query)
                connection.commit()
                cursor.close()
                connection.close()

                return redirect('/schooladmin/booklist')
        else:
            return redirect('/') 
    
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/') 
    return redirect('/schooladmin/booklist')
#-----------------------School Admin book->Declete button-----------------------

#-----------------------School Admin book->Update button-----------------------
@routes.route('/schooladmin/booklist/update', methods=['GET', 'POST'])
def schooladmin_booklist_updating(): 
    try:
        if(session['sadmin_access']):
            if(request.method == 'GET'):
                flash('Book changes done', category='success')
            elif(request.method == 'POST'):
                #Taking the object from javascript event, this will be a list with one element  in python
                update = request.form.getlist('update_button')
                update = update[0].split(",")
                                
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor()

                scadmin_id = int(session.get("id"))
                query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                school_id = int(aux[0][0])

                query = ("""UPDATE book 
                            SET available = {}
                            WHERE (school_id = {} AND ISBN = '{}');"""
                        .format(int(update[1]), school_id, update[0]))
                cursor.execute(query)
                connection.commit()
                
                cursor.close()
                connection.close()

                return redirect('/schooladmin/booklist')
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/schooladmin/booklist')
#-----------------------School Admin book->Update button-----------------------

#-----------------------School Admin book->Details button-----------------------
@routes.route('/schooladmin/booklist/details', methods = ['GET', 'POST'])
def schooladmin_bookdetails():
    global book, image_source, authors, keywords, categories
    try:
        if(session['sadmin_access']):
            return render_template('schooladmin_details.html', book = book, image_source = image_source, authors = authors, keywords = keywords, categories = categories)
        else:
            return redirect('/') 
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    
@routes.route('/schooladmin/booklist/details_aux', methods = ['GET', 'POST'])
def schooladmin_bookdetails_aux():
    global book, image_source, authors, keywords, categories
    try:
        if(session['sadmin_access']):
            if (request.method == 'POST'):
                ISBN = request.form.get('details_button')

                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
                cursor = connection.cursor() 
                scadmin_id = int(session.get("id")) 

                query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                school_id = int(aux[0][0])
                
                query = ("""SELECT author.first_name, author.last_name, author.ISBN 
                        FROM author 
                        INNER JOIN book ON author.ISBN = book.ISBN
                        WHERE author.ISBN = '{}' AND book.school_id = {};""".format(ISBN, school_id))
                cursor.execute(query)
                authors = cursor.fetchall()

                query = ("""SELECT keyword, keywords.ISBN 
                            FROM keywords
                            INNER JOIN book ON keywords.ISBN = book.ISBN
                            WHERE keywords.ISBN = '{}' AND book.school_id = {};""".format(ISBN, school_id))
                cursor.execute(query)
                keywords = cursor.fetchall()

                query = ("""SELECT category, category.ISBN 
                            FROM category
                            INNER JOIN book ON category.ISBN = book.ISBN
                            WHERE category.ISBN = '{}' AND book.school_id = {};""".format(ISBN, school_id))
                cursor.execute(query)
                categories = cursor.fetchall() 


                scadmin_id = int(session.get("id")) 
                query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
                cursor.execute(query)
                aux = cursor.fetchall()
                school_id = int(aux[0][0])

                cursor.callproc('details', [ISBN, school_id])

                for result in cursor.stored_results(): 
                    book = result.fetchall()
                    image_source = ''
                    if (book[0][10] != ''):
                        decoded_image = base64.b64decode(book[0][10])
                        image_source = "data:image/jpeg;base64," + base64.b64encode(decoded_image).decode('utf-8')

                cursor.close()
                connection.close()
        else:
            return redirect('/')

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    
    return redirect('/schooladmin/booklist/details')  
      
#-----------------------School Admin book->Details button----------------------- 

#-----------------------School Admin users-----------------------
@routes.route('/schooladmin/users', methods = ['GET', 'POST'])
def schooladmin_userslist():  
    global users
    try:
        if(session['sadmin_access']):
            which_user = request.form.get('search_user')

            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()

            scadmin_id = int(session.get("id"))
            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            if (which_user == None): 
                which_user = ''
            cursor.callproc('userlist', [which_user, school_id, 'Approved'])
            users = []    
            for result in cursor.stored_results(): 
                users = result.fetchall()

            cursor.close()
            connection.close()
        else:
            return redirect('/')

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('schooladmin_userslist.html', users = users)
#-----------------------School Admin users-----------------------

#-----------------------School Admin users waiting-----------------------
@routes.route('/schooladmin/users/pending', methods = ['GET', 'POST'])
def schooladmin_pendingusers(): 
    try:
        if(session['sadmin_access']):
            which_user = request.form.get('search_user')
            
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()

            scadmin_id = int(session.get("id"))
            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            if (which_user == None): 
                which_user = ''
            cursor.callproc('userlist', [which_user, school_id, 'Waiting'])
            users = []    
            for result in cursor.stored_results(): 
                users = result.fetchall()

            cursor.close()
            connection.close()
        else:
            return redirect('/')
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('schooladmin_pendingusers.html', users = users)
#-----------------------School Admin users waiting-----------------------

#-----------------------School Admin users waiting->Approve button-----------------------
@routes.route('/schooladmin/users/approve', methods=['GET', 'POST'])
def schooladmin_approve_user():
    try:
        if(session['sadmin_access']):
            if(request.method == 'GET'):
                flash('User approved', category = 'success')
            elif(request.method == 'POST'):
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
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/schooladmin/users/pending') 
#-----------------------School Admin users waiting->Approve button-----------------------

#-----------------------School Admin users waiting->Decline button-----------------------
@routes.route('/schooladmin/users/decline', methods=['GET', 'POST'])
def schooladmin_decline_user():
    try:
        if(session['sadmin_access']):
            if(request.method == 'GET'):
                flash('User declined', category = 'error')
            elif(request.method == 'POST'):
                #Taking the object from javascript event
                decline = request.form['schooladmin_decline_user']
                #Connection issues
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor()
                query = ("""DELETE FROM user WHERE user_id = {};""".format(int(decline)))
                cursor.execute(query) 
                connection.commit()
                
                return redirect('/schooladmin/users/pending')
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/schooladmin/users/pending')
#-----------------------School Admin users waiting->Decline button-----------------------

#-----------------------School Admin users ->Deactivate button-----------------------
@routes.route('/schooladmin/users/deactivate', methods=['GET', 'POST'])
def schooladmin_deactivate_user():
    try:
        if(session['sadmin_access']):
            if(request.method == 'GET'):
                flash('User deactivated', category = 'error')
            elif(request.method == 'POST'):
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
        
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/schooladmin/users') 
#-----------------------School Admin users ->Deactivate button-----------------------

#-----------------------School Admin users ->Delete button-----------------------
@routes.route('/schooladmin/users/delete', methods=['GET', 'POST'])
def schooladmin_delete_user(): 
    try:
        if(session['sadmin_access']):
            if(request.method == 'GET'):
                flash('User deleted', category = 'error')
            elif(request.method == 'POST'):
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

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/schooladmin/users') 
#-----------------------School Admin users ->Delete button-----------------------

#-----------------------School Admin Approved Borrowings List-----------------------
@routes.route('/schooladmin/borrowings/list', methods=['GET', 'POST'])
def schooladmin_borrowlist():
    try:
        if(session['sadmin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()

            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(int(session.get("id"))))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            query = ("""SELECT book.ISBN, book.book_title, author.first_name, author.last_name, user.first_name, user.last_name, borrowing.borrowing_date, borrowing.borrowing_id
                    FROM book 
                    INNER JOIN author ON book.ISBN = author.ISBN
                    INNER JOIN borrowing ON borrowing.ISBN = book.ISBN
                    INNER JOIN user ON user.user_id = borrowing.user_id 
                    WHERE borrowing.borrowing_status = 'Approved' AND book.school_id = {}
                    GROUP BY borrowing_id;""".format(school_id))
            cursor.execute(query)
            aux = cursor.fetchall()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('schooladmin_borrowlist.html', aux = aux)
#-----------------------School Admin Approved Borrowings List-----------------------

#-----------------------School Admin Approved Borrowings List->Return button-----------------------
@routes.route('/schooladmin/borrowings/list_return', methods=['GET', 'POST'])
def schooladmin_borrowlist_return():
    try:
        if(session['sadmin_access']):
            if(request.method == 'GET'):
                flash('Book returned!', category='success')
            elif(request.method == 'POST'):
                returning = request.form['borrow_return']
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor()
                #Select the given borrowing
                query = ("SELECT * FROM borrowing WHERE borrowing_id = {};".format(int(returning)))
                cursor.execute(query)
                borrowing = cursor.fetchall()
                borrowing = borrowing[0]

                #Select the school from which this borrowing was done
                query = ("SELECT school_id FROM school_admin WHERE scadmin_id = {};".format(int(borrowing[5])))
                cursor.execute(query)
                schoolid = cursor.fetchall()
                schoolid = str(schoolid[0][0])

                #Select the user that did this borrowing
                query = ("""SELECT * FROM user WHERE user_id =  {};""".format(int(borrowing[2])))
                cursor.execute(query)
                user = cursor.fetchall()
                user = user[0]

                cursor.callproc('returnable', (int(returning), int(user[0]), str(borrowing[1]), schoolid))
                connection.commit()

                cursor.close()
                connection.close()
                return redirect('/schooladmin/borrowings/list')
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/schooladmin/borrowings/list')
#-----------------------School Admin Approved Borrowings List->Return button-----------------------

#-----------------------School Admin Completed Borrowings List-----------------------
@routes.route('/schooladmin/borrowings/completed', methods=['GET', 'POST'])
def schooladmin_borrowlist_completed():
    try:
        if(session['sadmin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()

            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(int(session.get("id"))))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            query = ("""SELECT DISTINCT book.ISBN, book.book_title, author.first_name, author.last_name, user.first_name, user.last_name, borrowing.borrowing_date
                    FROM book 
                    INNER JOIN author ON book.ISBN = author.ISBN
                    INNER JOIN borrowing ON borrowing.ISBN = book.ISBN
                    INNER JOIN user ON user.user_id = borrowing.user_id 
                    WHERE borrowing.borrowing_status = 'Completed' AND book.school_id = {}
                    GROUP BY borrowing_id;""".format(school_id))
            cursor.execute(query)
            aux = cursor.fetchall()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('schooladmin_borrowcomplete.html', aux = aux)
#-----------------------School Admin Completed Borrowings List-----------------------

#-----------------------School Admin Waiting Borrowings List-----------------------
@routes.route('/schooladmin/borrowings/pending', methods=['GET', 'POST'])
def schooladmin_pendingborrowings():
    try:
        if(session['sadmin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()

            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(int(session.get("id"))))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            query = ("""SELECT book.ISBN, book.book_title, author.first_name, author.last_name, user.first_name, user.last_name, borrowing.borrowing_id, borrowing.borrowing_date
                    FROM book 
                    INNER JOIN author ON book.ISBN = author.ISBN
                    INNER JOIN borrowing ON borrowing.ISBN = book.ISBN
                    INNER JOIN user ON user.user_id = borrowing.user_id 
                    WHERE borrowing.borrowing_status = 'Waiting' AND book.school_id = {}
                    GROUP BY borrowing_id;""".format(school_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            
        return render_template('schooladmin_pendingborrowings.html', aux = aux)
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('schooladmin_pendingborrowings.html', aux = aux)
#-----------------------School Admin Waiting Borrowings List-----------------------


#-----------------------School Admin Waiting Borrowings List->Proceed-----------------------
@routes.route('/schooladmin/borrowings/pending_proceed', methods=['GET', 'POST'])
def schooladmin_pendingborrowings_approve():
    global checked, avail
    try:
        if(session['sadmin_access']):          
            if(request.method == 'POST'):
                approve = request.form['schooladmin_proceed_borrowing']
                
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor()
                #Select the given borrowing
                query = ("SELECT * FROM borrowing WHERE borrowing_id = {};".format(int(approve)))
                cursor.execute(query)
                borrowing = cursor.fetchall()
                borrowing = borrowing[0]

                #Select the school from which this borrowing was done
                query = ("SELECT school_id FROM school_admin WHERE scadmin_id = {};".format(int(borrowing[5])))
                cursor.execute(query)
                schoolid = cursor.fetchall()
                schoolid = str(schoolid[0][0])

                #Select the user that did this borrowing
                query = ("""SELECT * FROM user WHERE user_id =  {};""".format(int(borrowing[2])))
                cursor.execute(query)
                user = cursor.fetchall()
                user = user[0]

                checked = None
                avail = None
                cursor.callproc('borrowing_approve', (int(approve), int(user[0]), user[8], str(borrowing[1]), schoolid, checked, avail))
                connection.commit()
                result = cursor.stored_results()

                listing = []
                for i in result:
                    listing.append(i.fetchall()[0][0])
                if len(listing) != 0:
                    checked = listing[0]
                    avail = listing[1]
                    
                    if(checked == 1):
                        if(avail > 0):
                            flash('Borrowing done!', category='success')
                        else:
                            flash('No books available, user is automatically in a priority queue', category='error')
                    else:
                        flash('User does not compromise with the limitations', category='error')

                cursor.close()
                connection.close()
                return redirect('/schooladmin/borrowings/pending')
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')

    return redirect('/schooladmin/borrowings/pending')
#-----------------------School Admin Waiting Borrowings List->Proceed-----------------------

#-----------------------School Admin reservation List-----------------------
@routes.route('/schooladmin/reservelist', methods = ['GET', 'POST'])
def schooladmin_reservelist():
    try:
        if(session['sadmin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()

            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(int(session.get("id"))))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            query = ("""SELECT book.ISBN, book.book_title, author.first_name, author.last_name, user.first_name, user.last_name, reservation.reservation_date, reservation.reservation_to_date, reservation.reservation_id
                        FROM book
                        INNER JOIN author ON book.ISBN = author.ISBN
                        INNER JOIN reservation ON reservation.ISBN = book.ISBN
                        INNER JOIN user ON user.user_id = reservation.user_id
                        WHERE (reservation.reservation_status = 'Waiting' AND book.school_id = {})
                        GROUP BY reservation_id;""".format(school_id))
            
            cursor.execute(query)
            reservations = cursor.fetchall()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('schooladmin_reservelist.html', reservations = reservations)
#-----------------------School Admin reservation List-----------------------

#-----------------------School Admin reservation List->Proceed-----------------------
@routes.route('/schooladmin/reservelist/proceed', methods = ['GET', 'POST'])
def schooladmin_reserve_proceed():
    global checkedr, availr
    try:
        if(session['sadmin_access']):
            if (request.method == 'POST'):
                proceed_button = request.form['proceed_button']

                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
                cursor = connection.cursor()

                #find the school_id
                query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(int(session.get("id"))))
                cursor.execute(query)
                aux = cursor.fetchall()
                school_id = int(aux[0][0])

                #find the reservation id
                query = ("SELECT * FROM reservation WHERE reservation.reservation_id = {};".format(int(proceed_button)))
                cursor.execute(query)
                aux = cursor.fetchall()
                reservation = aux[0] 

                #find the userId
                query = ("SELECT user_id FROM reservation WHERE reservation.reservation_id = {};".format(int(proceed_button)))
                cursor.execute(query)
                userId = int(cursor.fetchall()[0][0])

                #find the ISBN
                query = ("SELECT ISBN FROM reservation WHERE reservation.reservation_id = {};".format(int(proceed_button)))
                cursor.execute(query)
                ISBN = str(cursor.fetchall()[0][0])

                #find the role
                query = ("""SELECT job 
                            FROM user
                            WHERE user.user_id = {};""".format(userId))
                cursor.execute(query)
                job = cursor.fetchall()[0][0]

                checkedr = None
                avail = None
                result = cursor.callproc('reservation_approve', (userId, ISBN, job, school_id, int(reservation[0]), checked, avail))
                connection.commit()
                result = cursor.stored_results()
                
                listing = []
                for i in result:
                    listing.append(i.fetchall()[0][0])
                checkedr = listing[0]
                availr = listing[1]
                
                if(checkedr == 1):
                    if(availr > 0):
                        flash('Reservation Approved!', category='success')
                    else:
                        flash("""No books available right now, user is automatically in a 
                                priority queue and further commits will be done at the borrowing date""", category='error')
                else:
                    flash('User does not compromise with the limitations', category='error')

                cursor.close()
                connection.close()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/schooladmin/reservelist')
#-----------------------School Admin reservation List->Proceed-----------------------


#-----------------------School Admin Overdue Returns-----------------------
@routes.route('/schooladmin/return/overdue', methods = ['GET', 'POST'])
def schooladmin_overduereturn():
    global aux
    try:
        if(session['sadmin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()

            first_name = request.form.get('search_firstname')
            last_name = request.form.get('search_lastname')
            if (first_name == None):
                first_name = ''
            if (last_name == None):
                last_name = ''
            delay = request.form.get('search_delay')
            if (delay == None or delay == ''):
                delay = -1
            else:
                delay = int(delay)

            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(int(session.get("id"))))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            query = ("""SELECT book.ISBN, book.book_title, author.first_name, author.last_name, user.first_name, user.last_name, borrowing.borrowing_date
                        FROM book 
                        INNER JOIN author ON book.ISBN = author.ISBN
                        INNER JOIN borrowing ON borrowing.ISBN = book.ISBN
                        INNER JOIN user ON user.user_id = borrowing.user_id 
                        WHERE ((borrowing.borrowing_status = 'Approved') AND (book.school_id = {}) AND
                                ('{}' = '' OR user.first_name = '{}') AND ('{}' = '' OR user.last_name = '{}') AND 
                                ({} = -1 OR DATEDIFF(CURRENT_TIMESTAMP, CAST(borrowing_date AS DATETIME)) = {}) AND
                                (DATEDIFF(CURRENT_TIMESTAMP, CAST(borrowing_date AS DATETIME))) > 7);""".format(school_id, first_name, first_name, last_name, last_name, delay, delay))
            cursor.execute(query)
            aux = cursor.fetchall()

            list = []
            for i in aux:
                helper = []
                for j in range(0, 7):
                    helper.append(i[j])
                list.append(helper)

            for i in list:
                i[6] = str(i[6]+timedelta(days = 7))
            cursor.close()
            connection.close()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')

    return render_template('schooladmin_returnoverdue.html', aux = list)
#-----------------------School Admin Overdue Returns-----------------------

#-----------------------School Admin Reviews-----------------------
@routes.route('/schooladmin/reviews/approve', methods = ['POST', 'GET'])
def schooladmin_approvereviews():
    try:
        if(session['sadmin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
            cursor = connection.cursor()

            scadmin_id = int(session.get("id"))
            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            query = ("""SELECT review.ISBN, book.book_title, author.first_name, author.last_name, user.first_name, user.last_name, review.txt, review.review_id
                        FROM review
                        INNER JOIN book ON review.ISBN = book.ISBN
                        INNER JOIN author ON review.ISBN = author.ISBN 
                        INNER JOIN user ON review.user_id = user.user_id 
                        WHERE ((review.review_status = 'Waiting') AND (user.school_id = {}))
                        GROUP BY review_id;""".format(school_id))
            cursor.execute(query)
            reviews = cursor.fetchall()

            cursor.close()
            connection.close()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('schooladmin_approvereview.html', reviews = reviews)
#-----------------------School Admin Reviews-----------------------

#-----------------------School Admin Reviews->Approve-----------------------
@routes.route('/schooladmin/reviews/approve_button', methods = ['POST', 'GET'])
def schooladmin_approve_button():
    try:
        if(session['sadmin_access']):
            if (request.method == 'GET'):
                flash('Review Approved', category = 'success')
            elif (request.method == 'POST'):
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
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect ('/schooladmin/reviews/approve')
#-----------------------School Admin Reviews->Approve-----------------------

#-----------------------School Admin Reviews->Decline-----------------------
@routes.route('/schooladmin/reviews/decline_button', methods = ['POST', 'GET'])
def schooladmin_decline_button():
    try:
        if(session['sadmin_access']):
            if (request.method == 'GET'):
                flash('Review Declined', category = 'error')
            elif (request.method == 'POST'):
                review_id = request.form.get('schooladmin_decline_review')
                connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
                cursor = connection.cursor()
                query = ("""DELETE FROM review
                            WHERE review_id = {};""".format(int(review_id)))
                cursor.execute(query)
                connection.commit()

                return redirect('/schooladmin/reviews/approve')
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return redirect('/schooladmin/reviews/approve')
#-----------------------School Admin Reviews->Decline-----------------------

#-----------------------School Admin Reviews per user-----------------------
@routes.route('/schooladmin/reviews/peruser', methods = ['GET', 'POST'])
def schooladmin_reviewperuser():
    try:
        if(session['sadmin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            cursor = connection.cursor()

            first_name = request.form.get('search_firstname')
            last_name = request.form.get('search_lastname')
            if (first_name == None):
                first_name = ''
            if (last_name == None):
                last_name = ''

            scadmin_id = int(session.get("id"))
            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            query = ("""SELECT user.first_name, user.last_name, review.likert
                        FROM review
                        INNER JOIN user ON review.user_id = user.user_id
                        INNER JOIN book ON review.ISBN = book.ISBN
                        WHERE ((book.school_id = {}) AND (review.review_status = 'Approved') AND
                                ('{}' = '' OR user.first_name = '{}') AND ('{}' = '' OR user.last_name = '{}'))
                        ORDER BY user.first_name, user.last_name;""".format(int(school_id), first_name, first_name, last_name, last_name))
            cursor.execute(query)
            reviews = cursor.fetchall()

            sum = []
            avg = []
            users_first = []
            users_last = []
            if(reviews != []):
                flag_first = reviews[0][0]
                flag_last = reviews[0][1]
                users_first.append(flag_first)
                users_last.append(flag_last)
                for review in reviews:
                    if (review[0] == flag_first and review[1] == flag_last):
                        sum.append(int(review[2][-1]))
                    else: 
                        flag_first = review[0]
                        flag_last = review[1]
                        users_first.append(flag_first)
                        users_last.append(flag_last)
                        avg.append(mean(sum))
                        sum.clear()
                        sum.append(int(review[2][-1]))
                avg.append(mean(sum))
                sum.clear()
                sum.append(int(review[2][-1]))

            cursor.close()
            connection.close()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('schooladmin_reviewperuser.html', users_first = users_first, users_last = users_last, avg = avg)
#-----------------------School Admin Reviews per user-----------------------

#-----------------------School Admin Reviews per category-----------------------
@routes.route('/schooladmin/reviews/percategory', methods = ['GET', 'POST'])
def schooladmin_reviewpercategory():
    try:
        if(session['sadmin_access']):
            connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config)
            cursor = connection.cursor()

            which_category = request.form.get('search_category')
            if (which_category == None):
                which_category = ''
            scadmin_id = int(session.get("id"))
            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(scadmin_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])

            query = ("""SELECT category.category, review.likert
                        FROM review
                        INNER JOIN category ON review.ISBN = category.ISBN
                        INNER JOIN book ON review.ISBN = book.ISBN
                        WHERE ((book.school_id = {}) AND (review.review_status = 'Approved') AND 
                                ('{}' = '' OR category.category LIKE '%{}%'))
                        ORDER BY category.category;""".format(int(school_id), which_category, which_category))
            cursor.execute(query)
            reviews = cursor.fetchall()

            sum = []
            avg = []
            categories = []
            if(reviews != []):
                flag = reviews[0][0]
                categories.append(flag)
                for review in reviews:
                    if (review[0] == flag):
                        sum.append(int(review[1][-1]))
                    else: 
                        flag = review[0]
                        categories.append(flag)
                        avg.append(mean(sum))
                        sum.clear()
                        sum.append(int(review[1][-1]))
                avg.append(mean(sum))
                sum.clear()
                sum.append(int(review[1][-1]))

            cursor.close()
            connection.close()
        else:
            return redirect('/') 

    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    return render_template('schooladmin_reviewpercategory.html', categories = categories, avg = avg)
#-----------------------School Admin Reviews per category-----------------------
#-----------------SCHOOL ADMIN TEMPLATES-------------------------------

def queuer_init():
    while(True):
        queuer()
        time.sleep(30)
        
def queuer():
    try:
        connection = sql.connect(host = host_config, database = database_config, user = user_config, password = password_config) 
        cursor = connection.cursor()
        query = ("""SELECT * FROM reservation WHERE (reservation_status = 'Waiting Queue' AND reservation_to_date <= CAST(CURRENT_TIMESTAMP AS DATE))
                ORDER BY reservation_to_date DESC, reservation_date DESC;""")
        cursor.execute(query)
        priority = cursor.fetchall()
        for i in priority:
            query = ('UPDATE reservation SET reservation_to_date = CAST(CURRENT_TIMESTAMP AS DATE) WHERE reservation_id = {}'.format(i[0]))
            cursor.execute(query)
            connection.commit()

            query = ('SELECT school_id FROM school_admin WHERE scadmin_id = {};'.format(i[6]))
            cursor.execute(query)
            aux = cursor.fetchall()
            school_id = int(aux[0][0])
            
            query = ("SELECT * FROM book WHERE ISBN = '{}' AND school_id = {}".format(i[1], school_id))
            cursor.execute(query)
            aux = cursor.fetchall()
            aux = aux[0]
            
            if(aux[6] > 0):
                query = ("SELECT job FROM user WHERE user.user_id = {};".format(i[2]))
                cursor.execute(query)
                job = cursor.fetchall()[0][0]

                cursor.callproc('reservation_approve', (i[2], aux[0], job, school_id, i[0]))
                connection.commit()
    except Exception as e:
        flash(str(e), category = 'error')
        return redirect('/')
    
scheduler_thread = threading.Thread(target=queuer_init)
scheduler_thread.start()
