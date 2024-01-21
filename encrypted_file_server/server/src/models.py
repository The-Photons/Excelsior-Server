# IMPORTS
from flask_login import UserMixin

from .. import db


# MODELS
class User(UserMixin, db.Model):
    """
    Model representing a user within the application.
    """

    # Main attributes
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    # Encryption attributes
    iv = db.Column(db.String(16), nullable=False)
    salt = db.Column(db.String(16), nullable=False)
    encrypted_key = db.Column(db.String(64), nullable=False)
