# IMPORTS
from flask import Blueprint, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

from encrypted_file_server.server.src.models import User

# BLUEPRINT DEFINITION
auth = Blueprint("auth", __name__, url_prefix="/auth")


# ROUTES
# Main authentication routes
@auth.route("/login", methods=["POST"])
def login():
    # Get some parameters from the URL parameters
    url_params = request.args
    actually_login = url_params.get("actually-login", True)

    try:
        actually_login = bool(actually_login)
    except ValueError:
        actually_login = True

    # Get the required things from the request form
    username = request.form.get("username")
    password = request.form.get("password", "")

    # Try and get the user
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"status": "fail", "message": "Invalid username"}
    elif not check_password_hash(user.password, password):
        return {"status": "fail", "message": "Wrong password"}
    else:
        if actually_login:
            login_user(user, remember=False)
            return {"status": "ok", "message": f"Logged in as {user.username}"}
        else:
            return {"status": "ok", "message": f"Credentials valid for {user.username}"}


@auth.route("/logout", methods=["GET"])
@login_required
def logout():
    username = current_user.username
    logout_user()
    return {"status": "ok", "message": f"Logged out {username}"}


# Miscellaneous routes
@auth.route("/get-encryption-params", methods=["GET"])
@login_required
def get_encryption_parameters():
    return {
        "status": "ok",
        "iv": current_user.iv,
        "salt": current_user.salt,
        "encrypted_key": current_user.encrypted_key
    }
