# IMPORTS
from flask import Blueprint
from flask_login import login_required, current_user

# BLUEPRINT DEFINITION
file_ops = Blueprint("file_ops", __name__)


# ROUTES
@file_ops.route("/test-path", methods=["GET"])
@login_required
def testing_route():
    return f"Hello, {current_user.username}"
