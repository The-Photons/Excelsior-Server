# IMPORTS
import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# CONSTANTS
DATABASE = "excelsior.db"

# SETUP
db = SQLAlchemy()


# APP FACTORY
def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "insecure-c112afeef1b534d236a7d3bdb75e6247ef7c9b2677a68b181f46b45"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{DATABASE}"
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    db.init_app(app)

    # Initialize login manager
    login_manager = LoginManager()
    # login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Define a user loader
    from .src.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Check if database exists
    if not os.path.isfile(os.path.join(app.instance_path, DATABASE)):
        from .src.models import User
        with app.app_context():
            db.create_all()

    # Check if all users' folders exists within the instance
    with app.app_context():
        users = User.query.all()
        for user in users:
            path = os.path.join(app.instance_path, user.username)
            if not os.path.isdir(path):
                os.mkdir(path)

    # Register blueprints
    from encrypted_file_server.server.blueprints.auth import auth as auth_bp
    from encrypted_file_server.server.blueprints.file_ops import file_ops as file_ops_bp
    from encrypted_file_server.server.blueprints.misc import misc as misc_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(file_ops_bp)
    app.register_blueprint(misc_bp)

    # Finally return the created app
    return app
