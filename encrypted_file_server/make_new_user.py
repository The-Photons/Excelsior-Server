# IMPORTS
from getpass import getpass

from werkzeug.security import generate_password_hash

from encrypted_file_server.server import create_app, db
from encrypted_file_server.server.src.models import User

# MAIN CODE
app = create_app()
with app.app_context():

    # Get username first
    username = input("Enter username: ")

    if User.query.filter_by(username=username).first():
        print("User with requested username already exists")
        exit(1)

    # Then get password
    password1 = "1"
    password2 = "2"
    while password1 != password2:
        password1 = getpass("Enter password: ")
        password2 = getpass("Confirm password: ")

        if password1 != password2:
            print("Passwords do not match")

    # Create a new user with the form data. Hash the password so the plaintext version isn't saved
    new_user = User(username=username, password=generate_password_hash(password1))

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

print("Done!")
