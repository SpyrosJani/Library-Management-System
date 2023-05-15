from flask import Blueprint, render_template

#this file has URLs of our site

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")