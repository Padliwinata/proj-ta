import typing

from cryptography.fernet import Fernet

from db import db_user, db_institution
from settings import SECRET_KEY

f = Fernet(SECRET_KEY)

institution_data = [
    ({
        'address': 'TULT 0610',
        'email': 'iflab@example.com',
        'name': 'IFLab',
        'phone': '+6285179762170'
    }, 'gc8uupscjs0e'),
    ({
        'address': 'TULT 0604',
        'email': 'company@email.com',
        'name': 'asprak',
        'phone': '+6285179762170'
    }, 'uxalzb21mwcr')
]

user_data: typing.List[typing.Dict[str, typing.Union[str, bool]]] = [
    {
        "username": "username",
        "password": "password",
        "email": "username@example.com",
        "role": "super admin",
        "id_institution": "",
        "is_active": True
    },
    {
        "username": "alice_smith",
        "password": "another_secure_password",
        "email": "alice@example.com",
        "role": "admin",
        "id_institution": "gc8uupscjs0e",
        "is_active": True
    },
    {
        "username": "bob_marley",
        "password": "yet_another_secure_password",
        "email": "bob@example.com",
        "role": "staff",
        "id_institution": "gc8uupscjs0e",
        "is_active": True
    },
    {
        "username": "emma_jones",
        "password": "password",
        "email": "emma@example.com",
        "role": "reviewer",
        "id_institution": "gc8uupscjs0e",
        "is_active": True
    },
    {
        "username": "sam_smith",
        "password": "password123",
        "email": "sam@example.com",
        "role": "admin",
        "id_institution": "uxalzb21mwcr",
        "is_active": True
    }
]


def seed() -> None:
    for ins_data in institution_data:
        db_institution.put(*ins_data)

    for data in user_data:
        new_password = bytes()
        if isinstance(data['password'], str):
            new_password = f.encrypt(data['password'].encode('utf-8'))
        data['password'] = new_password.decode('utf-8')

        db_user.put(data)
