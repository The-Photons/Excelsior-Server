# IMPORTS
import os

from cryptography import fernet
from cryptography.fernet import Fernet
from yaml import safe_load, safe_dump


# FUNCTIONS
def get_key(secrets_file: os.PathLike) -> bytes:
    """
    Get key from the secrets file.
    :return: Key for Fernet.
    """

    try:
        with open(secrets_file, "r") as f:
            secrets = safe_load(f)
    except FileNotFoundError:
        secrets = None

    if secrets is None or "key" not in secrets:
        key = Fernet.generate_key()
        secrets = {"key": key}

        with open(secrets_file, "w") as f:
            safe_dump(secrets, f)
    else:
        key = secrets["key"]

    return key


def encrypt(data: bytes, key: bytes) -> bytes:
    """
    Encrypts the data using Fernet.
    :param data: Data to encrypt.
    :param key: Key for Fernet.
    :return: Encrypted data.
    """
    f = fernet.Fernet(key)
    return f.encrypt(data)


def decrypt(data: bytes, key: bytes) -> bytes:
    """
    Decrypts the data using Fernet.
    :param data: Data to decrypt.
    :param key: Key for Fernet.
    :return: Decrypted data.
    """
    f = fernet.Fernet(key)
    return f.decrypt(data)
