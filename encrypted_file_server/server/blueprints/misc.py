# IMPORTS
from flask import Blueprint

from encrypted_file_server import __version__

# BLUEPRINT DEFINITION
misc = Blueprint("misc", __name__)


# ROUTES
@misc.route("/ping", methods=["GET"])
def ping():
    return {"status": "ok", "content": "pong"}


@misc.route("/version", methods=["GET"])
def get_version():
    return {"status": "ok", "version": __version__}
