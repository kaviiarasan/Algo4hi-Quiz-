import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "quiz-competition-secret-key-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///quiz_competition.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
os.makedirs(upload_dir, exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Please log in to access this page.'

# Add chr function to Jinja2 globals
app.jinja_env.globals['chr'] = chr

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models to ensure they're registered
    import models

    # Create tables
    db.create_all()

    # Create admin user if it doesn't exist
    from models import Admin
    from werkzeug.security import generate_password_hash

    # Create the Algo admin user if it doesn't exist
    admin = Admin.query.filter_by(username='Algo admin').first()
    if not admin:
        admin = Admin(
            username='Algo admin',
            email='kaviiarasan.sv@gktech.ai',
            password_hash=generate_password_hash('algogkt@123')
        )
        db.session.add(admin)
        db.session.commit()
        print("Algo admin user created with email: kaviiarasan.sv@gktech.ai")

# Import routes
from routes import *
from admin_routes import *