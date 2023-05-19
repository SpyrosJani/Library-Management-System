from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FileField, EmailField, DateField
from wtforms.validators import DataRequired, Email

class add_book_form (FlaskForm):
    book_title = StringField('Title', validators=[DataRequired(message="Title is a required field.")])
    
    summary = StringField('Summary', validators=[DataRequired(message="Summary is a required field.")])
    
    ISBN = StringField('ISBN', validators=[DataRequired(message="ISBN is a required field.")])
    
    publisher = StringField('Publisher', validators=[DataRequired(message="Publisher is a required field.")])
    
    no_pages = StringField('Number of Pages')
    
    available = IntegerField('Number of books available', validators=[DataRequired(message="Number of books is a required field.")])
    
    language = StringField('Language', validators=[DataRequired(message="Language is a required key.")])
    
    img = FileField('Book Cover Image', validators=[DataRequired(message="Book cover is a required field.")])
    
    submit = SubmitField('Add Book')

class add_school_form (FlaskForm):
    school_name = StringField('School Name', validators=[DataRequired(message="School Name is a required field.")])
    
    city = StringField('City', validators=[DataRequired(message="City is a required field.")])
    
    phone_number = StringField('Phone Number', validators=[DataRequired(message="Phone No is a required field.")])
    
    email = EmailField('School Email', validators=[DataRequired(message="Email is a required field.")])

    address = StringField('School Address', validators=[DataRequired(message="School is a required field.")])

    submit = SubmitField('Add School')

class add_review_form (FlaskForm):
    ISBN_rev = StringField('Book ISBN', validators=[DataRequired(message="Book ISBN is a required field.")])

    text = StringField('Text', validators=[DataRequired(message="Text is a required field.")])

    likert = IntegerField('Result', validators=[DataRequired(message="Likert scale is a required field")])

    submit = SubmitField('Submit Review')

class sign_up_form(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message="First Name is a required field.")])

    last_name = StringField('Last Name', validators=[DataRequired(message="Last Name is a required field.")])

    email = StringField('Email', validators=[DataRequired(message="Email is a required field.")])

    password = StringField('Password', validators=[DataRequired(message="Password is a required field.")])

    birth_date = DateField('Birth Date', validators=[DataRequired(message="Birth Date is a required field.")])

    school = StringField('School', validators=[DataRequired(message="School is a required field.")])



class search_form (FlaskForm):
    query = StringField("Search Query", validators=[DataRequired()])

    submit = SubmitField('Search')