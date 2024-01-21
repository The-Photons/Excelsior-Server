# IMPORTS
import base64
import secrets
from hashlib import pbkdf2_hmac
from getpass import getpass

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from werkzeug.security import generate_password_hash

from encrypted_file_server.server import create_app, db
from encrypted_file_server.server.src.models import User


# HELPER FUNCTIONS
def gen_aes_key(pwd: str, the_salt: str):
    return pbkdf2_hmac(
        hash_name="sha256",
        password=pwd.encode(),
        salt=the_salt.encode(),
        iterations=120000
    )


# MAIN FUNCTIONS
def run():
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

        # Generate encryption parameters
        iv = secrets.token_hex(8)
        salt = secrets.token_hex(8)

        user_key = gen_aes_key(password1, salt)
        encryption_key = secrets.token_bytes(32)  # 256 bit

        cipher = AES.new(user_key, AES.MODE_CBC, iv.encode())
        encrypted_encryption_key = cipher.encrypt(pad(encryption_key, 16))

        # Create a new user with the data
        new_user = User(
            username=username,
            password=generate_password_hash(password1),
            iv=iv,
            salt=salt,
            encrypted_key=base64.b64encode(encrypted_encryption_key).decode()
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

    print(f"Added {username} to the database!")


if __name__ == "__main__":
    run()
