from flask import Flask
from flask_mysqldb import MySQL
from . import auth
from website import views
import yaml

def create_app():
    app = Flask(__name__)
    app.jinja_env.filters['zip']=zip
    app.config['SECRET_KEY'] = 'lkjiofewjiopfwoi;f;w' #encrypt cookies and session data for website
    #configuration of database

    info = yaml.load(open('db.yaml'))
    app.config['MYSQL_HOST'] = info['mysql_host']
    app.config['MYSQL_USER'] = info['mysql_user']
    app.config['MYSQL_PASSWORD'] = info['mysql_password']
    app.config['MYSQL_DB'] = info['mysql_db']

    db = MySQL(app)

    app.register_blueprint(views, url_prefix='/') 
    app.register_blueprint(auth, url_prefix='/') #access the blueprints in each file with no prefix

    return app
