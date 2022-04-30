import os
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_pagedown import PageDown

# gives current directory of this file
basedir = os.path.abspath(os.path.dirname(__file__))

# instance of the Flask class
myapp_obj = flask.Flask(__name__)
myapp_obj.config.from_mapping(
    SECRET_KEY = 'you-cannot-guess',
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS = False
)
myapp_obj.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'sketchy'

# Install bootstrap extension
bootstrap = Bootstrap(myapp_obj)

# Install Sqlalchemy
db = SQLAlchemy(myapp_obj)

# Install LoginManager
login = LoginManager(myapp_obj)
login.login_view = 'login'
pagedown = PageDown(myapp_obj)


pagedown = PageDown(myapp_obj)

from myapp import routes, models
