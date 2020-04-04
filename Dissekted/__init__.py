from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_login import LoginManager

# Flask App setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'e470120549f25097e262c978acaf8278'

# SQL configs so I don't see the warnings in console
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Config to have website sending an email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'dissekted@gmail.com'
app.config['MAIL_PASSWORD'] = 'Dissekted220'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = "Dissekted Newsletter"

# Creating instances to be used in Application
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)

# Pass the function for logging in so @login_required knows where to send user to login, add bootstrap for message
login_manager.login_view= 'login'
login_manager.login_message_category = 'info'





# Import at the end to avoid circular imports
from Dissekted import routes