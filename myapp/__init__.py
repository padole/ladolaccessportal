import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail, Message

mail = Mail()
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app():
    from myapp.models import db, User, Admin # Import the db instance from SQLALCHEMY
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    app = Flask(__name__, template_folder=template_dir, instance_relative_config=True) # Load config from instance folder
    # app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # or your SMTP server
    # app.config['MAIL_PORT'] = 587
    # app.config['MAIL_USE_TLS'] = True
    # app.config['MAIL_USERNAME'] = 'inas4wealth@gmail.com'
    # app.config['MAIL_PASSWORD'] = 'dvtm yghs twqu rgpj'  # or your email password
    # app.config['MAIL_DEFAULT_SENDER'] = ('Ladol Access', 'inas4wealth@gmail.com')


    app.config['MAIL_SERVER'] = 'smtp.office365.com'  # or your SMTP server
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'meetings@ladol.com'
    app.config['MAIL_PASSWORD'] = 'Kah37418'  # or your email password
    app.config['MAIL_DEFAULT_SENDER'] = ('Ladol Access', 'meetings@ladol.com')
    app.config.from_pyfile('config.py')
    
    # app.config.from_object(config.TestConfig)# Load config from class
    mail.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'danger'
    migrate = Migrate(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) or Admin.query.get(int(user_id))

    return app

app=create_app()

from myapp import user_routes,myforms,admin_routes
