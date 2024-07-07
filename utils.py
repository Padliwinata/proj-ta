from cryptography.fernet import Fernet
from settings import SECRET_KEY

f = Fernet(SECRET_KEY)


def encrypt_password(raw_password: str) -> str:
    encoded_password = raw_password.encode('utf-8')
    encrypted_password = f.encrypt(encoded_password).decode('utf-8')
    return encrypted_password
