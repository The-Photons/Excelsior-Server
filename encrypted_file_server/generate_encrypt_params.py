# IMPORTS
import base64
import random
import secrets
import string
from hashlib import pbkdf2_hmac

import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


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
    iv = secrets.token_hex(8)
    salt = secrets.token_hex(8)
    test_str = "".join(random.choices(population=string.ascii_uppercase, k=64))

    password = input("Enter password: ")
    user_key = gen_aes_key(password, salt)

    encryption_key = secrets.token_bytes(32)  # 256 bit

    cipher = AES.new(user_key, AES.MODE_CBC, iv.encode())
    encrypted_test_string = cipher.encrypt(pad(test_str.encode(), 16))
    encrypted_encryption_key = cipher.encrypt(pad(encryption_key, 16))

    with open("encrypt_params.json", "w") as f:
        json.dump({
            "iv": iv,
            "salt": salt,
            "test_str": base64.b64encode(encrypted_test_string).decode(),
            "encrypted_key": base64.b64encode(encrypted_encryption_key).decode()
        }, f, indent=2)

    print("Done! Please place the generated 'encrypt_params.json' file within the data directory.")


if __name__ == "__main__":
    run()
