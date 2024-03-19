from db import db_user, db_institution

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

user_data = [
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

for ins_data in institution_data:
    db_institution.put(*ins_data)

for data in user_data:
    db_user.put(data)


