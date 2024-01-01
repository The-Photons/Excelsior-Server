from flask import Flask

app = Flask(__name__)

import encrypted_file_server.server.views
