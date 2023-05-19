from flask import Flask
from .routes import routes


app = Flask(__name__)
app.jinja_env.filters['zip']=zip
app.config['SECRET_KEY'] = 'lkjiofewjiopfwoi;f;w' #encrypt cookies and session data for website

app.register_blueprint(routes, url_prefix='/') #access the blueprints in each file with no prefix