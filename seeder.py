from datetime import datetime
import typing

from cryptography.fernet import Fernet

from db import db_user, db_institution, db_log, db_assessment, db_point, drive, db_proof
from models import Proof, Point
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
        "full_name": "User Name",
        "password": "password",
        "email": "username@example.com",
        "role": "super admin",
        "id_institution": "",
        "is_active": True
    },
    # {
    #     "username": "alice_smith",
    #     "full_name": "Alice Smith",
    #     "password": "another_secure_password",
    #     "email": "alice@example.com",
    #     "role": "admin",
    #     "id_institution": "gc8uupscjs0e",
    #     "is_active": True
    # },
    {
        "username": "bob_marley",
        "full_name": "Bob Marley",
        "password": "yet_another_secure_password",
        "email": "bob@example.com",
        "role": "staff",
        "id_institution": "gc8uupscjs0e",
        "is_active": True
    },
    {
        "username": "emma_jones",
        "full_name": "Emma Jones",
        "password": "password",
        "email": "emma@example.com",
        "role": "reviewer",
        "id_institution": "gc8uupscjs0e",
        "is_active": True
    },
    {
        "username": "sam_smith",
        "full_name": "Sam Smith",
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

    password_alice = f.encrypt('another_secure_password'.encode('utf-8'))

    db_user.put({
        "username": "alice_smith",
        "full_name": "Alice Smith",
        "password": password_alice.decode('utf-8'),
        "email": "alice@example.com",
        "role": "admin",
        "id_institution": "gc8uupscjs0e",
        "is_active": True
    }, key="ev9ag3o7lxed")


def seed_assessment() -> None:
    new_assessment = {
        'id_institution': 'gc8uupscjs0e',
        'id_admin': "ev9ag3o7lxed",
        'id_reviewer': '',
        'tanggal': datetime.now().strftime('%d %B %Y, %H:%M'),
        'hasil': 0,
        'selesai': False
    }

    db_assessment.put(new_assessment, key='lfu89u9tp9df')

    bab = [
        '1.1',
        '1.2',
        '2.1',
        '2.2',
        '3.1',
        '3.2',
        '4.1',
        '4.2',
        '5.1',
        '6.1'
    ]

    number = [10, 10, 10, 10, 8, 7, 7, 8, 15, 15]

    filenames = []
    for x in range(len(bab)):
        for i in range(number[x]):
            filenames.append(f"gc8uupscjs0e_{bab[x][0]}_{bab[x].replace('.', '')}_{i+1}.pdf")

    proofs = []
    for filename in filenames:
        proofs.append(
            Proof(
                id_user="ev9ag3o7lxed",
                url=f"/file/{filename}",
                file_name=filename
            )
        )

    for proof in proofs:
        db_proof.put(proof.dict())

    counter = 0
    points = []

    for i in range(len(bab)):
        for num in range(number[i]):
            points.append(
                Point(
                    id_assessment="lfu89u9tp9df",
                    bab=bab[i][0],
                    sub_bab=bab[i],
                    proof=proofs[counter],
                    point=num+1,
                    answer=1,
                    skor=0
                )
            )
            counter += 1

    for point in points:
        db_point.put(point.dict())
        drive.put(point.proof.file_name, path='cobafraud.pdf')


def delete_db() -> None:
    user_res = db_user.fetch()
    inst_res = db_institution.fetch()
    log_res = db_log.fetch()

    if user_res.count > 0:
        for data in user_res.items:
            db_user.delete(data['key'])

    if inst_res.count > 0:
        for data in inst_res.items:
            db_institution.delete(data['key'])

    if log_res.count > 0:
        for data in log_res.items:
            db_log.delete(data['key'])
