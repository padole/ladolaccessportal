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
    app.instance_path = os.path.join(os.path.dirname(__file__), '..', 'instance')

    # Database configuration
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        # Load config from instance/config.py if DATABASE_URL is not set
        try:
            app.config.from_pyfile('config.py')
        except FileNotFoundError:
            # If config.py not found, use default or environment variables
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///default.db')
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



   


    
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
