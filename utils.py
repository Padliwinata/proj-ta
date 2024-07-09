from typing import List, Dict, Any

from cryptography.fernet import Fernet
from settings import SECRET_KEY

f = Fernet(SECRET_KEY)


def encrypt_password(raw_password: str) -> str:
    encoded_password = raw_password.encode('utf-8')
    encrypted_password = f.encrypt(encoded_password).decode('utf-8')
    return encrypted_password


def decrypt_password(encrypted_password: str) -> str:
    return f.decrypt(encrypted_password).decode('utf-8')


def remove_dict_duplicates(list_of_dicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    unique_tuples = {tuple(sorted(d.items())) for d in list_of_dicts}
    unique_dicts = [dict(t) for t in unique_tuples]

    return unique_dicts
