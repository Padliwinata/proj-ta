from datetime import datetime
import typing

from cryptography.fernet import Fernet
import pymysql
import uuid

from db import db_user, db_institution, db_log, db_assessment, db_point, drive, db_proof
from models import Proof, Point
from settings import SECRET_KEY, DB_HOST, DB_NAME, DB_PASSWORD, DB_USERNAME

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
    }, 'uxalzb21mwcr'),
    ({
        'address': '',
        'email': 'external@gmail.com',
        'name': 'External Reviewer',
        'phone': ''
    }, 'external')
]

beneish_report = {
    "revenue_1": 2824529865,
    "cogs_1": 1637778233,
    "sgae_1": 978404721,
    "depreciation_1": 145556996,
    "net_continuous_1": 48164343,
    "account_receivables_1": 153909929,
    "current_assets_1": 955934379,
    "ppe_1": 1520837177,
    "securities_1": 11703633,
    "total_asset_1": 2085215,
    "current_liabilities_1": 919187828,
    "total_ltd_1": 602268672,
    "cash_flow_operate_1": 292733763,
    "dsri_1": 19.89,
    "gmi_1": 0.42,
    "aqi_1": -0.99,
    "sgi_1": 2824529866,
    "depi_1": 0.12,
    "sgai_1": 0.35,
    "lvgi_1": 0.73,
    "tata_1": 1,
    "revenue_2": 3698268848,
    "cogs_2": 2017661985,
    "sgae_2": 1286510421,
    "depreciation_2": 199692257,
    "net_continuous_2": 159960247,
    "account_receivables_2": 211364131,
    "current_assets_2": 1192611390,
    "ppe_2": 1520837177,
    "securities_2": 14959054,
    "total_asset_2": 2582866504,
    "current_liabilities_2": 1086055919,
    "total_ltd_2": 631821538,
    "cash_flow_operate_2": 487884312,
    "dsri_2": 20.86,
    "gmi_2": 0.45,
    "aqi_2": -1.06,
    "sgi_2": 3698268848,
    "depi_2": 0.12,
    "sgai_2": 0.35,
    "lvgi_2": 0.67,
    "tata_2": -0.13,
    "tahun_1": 2012,
    "tahun_2": 2013,
    "id_institution": "gc8uupscjs0e",
    "beneish_m": -2
}

user_data: typing.List[typing.Dict[str, typing.Union[str, bool]]] = [
    {
        "username": "username",
        "full_name": "User Name",
        "password": "password",
        "email": "username@example.com",
        "role": "super admin",
        "id_institution": "",
        "is_active": True,
        "phone": "+6281111111111"
    },
    {
        "username": "staff_perusahaan",
        "full_name": "Staff Perusahaan",
        "password": "password",
        "email": "staff@example.com",
        "role": "staff",
        "id_institution": "gc8uupscjs0e",
        "is_active": True,
        "phone": "+6281111111112"
    },
    {
        "username": "emma_jones",
        "full_name": "Emma Jones",
        "password": "password",
        "email": "emma@example.com",
        "role": "reviewer",
        "id_institution": "gc8uupscjs0e",
        "is_active": True,
        "phone": "+6281111111113"
    },
    {
        "username": "sam_smith",
        "full_name": "Sam Smith",
        "password": "password123",
        "email": "sam@example.com",
        "role": "admin",
        "id_institution": "uxalzb21mwcr",
        "is_active": True,
        "phone": "+6281111111114"
    },
    {
        "username": "reviewer",
        "full_name": "Reviewer Account",
        "password": "reviewer",
        "email": "reviewer@gmail.com",
        "role": "reviewer",
        "id_institution": "external",
        "is_active": True,
        "phone": "+6281111111116"
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

    password_alice = f.encrypt('admin'.encode('utf-8'))

    db_user.put({
        "username": "adminperusahaan",
        "full_name": "Admin Perusahaan",
        "password": password_alice.decode('utf-8'),
        "email": "alice@example.com",
        "role": "admin",
        "id_institution": "gc8uupscjs0e",
        "is_active": True,
        "phone": "+6281111111115"
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
    assessment_res = db_assessment.fetch()
    proof_res = db_proof.fetch()
    point_res = db_point.fetch()
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

    if assessment_res.count > 0:
        for data in assessment_res.items:
            db_assessment.delete(data['key'])

    if proof_res.count > 0:
        for data in proof_res.items:
            db_proof.delete(data['key'])

    if point_res.count > 0:
        for data in point_res.items:
            db_point.delete(data['key'])

    filename_list = drive.list()['names']
    if filename_list:
        drive.delete_many(filename_list)


# def generate_data_key() -> str:
#     # Placeholder for generating a data key, modify according to your logic
#     return str(uuid.uuid4())
#
#
# def get_institution_id(id_institution):
#     # Placeholder for mapping institution ID, modify according to your logic
#     institution_map = {
#         "gc8uupscjs0e": 1,
#         "uxalzb21mwcr": 2,
#         "external": 3
#     }
#     return institution_map.get(id_institution, 0)
#
#
# # Function to insert data into the database
# def insert_user_data() -> None:
#     try:
#         # Connect to the database
#         connection = pymysql.connect(
#             host=DB_HOST,
#             user=DB_USERNAME,
#             password=DB_PASSWORD,
#             database=DB_NAME
#         )
#
#         with connection.cursor() as cursor:
#             insert_query = """
#             INSERT INTO Users (data_key, username, full_name, password, email, role, id_institution, is_active, phone)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#             for user in user_data:
#                 data_key = generate_data_key()  # You need to implement this function based on your logic
#                 if isinstance(user['password'], str):
#                     password_blob = user['password'].encode()  # Convert password to bytes
#                 user_id_institution = get_institution_id(user['id_institution'])  # Map institution ID if needed
#                 cursor.execute(insert_query, (
#                     data_key, user['username'], user['full_name'], password_blob, user['email'],
#                     user['role'], user_id_institution, user['is_active'], user['phone']
#                 ))
#
#             # Commit the transaction
#             connection.commit()
#
#     except pymysql.MySQLError as e:
#         print(f"Error: {e}")
#     finally:
#         connection.close()

institution_data2 = [
    {
        'address': 'TULT 0610',
        'email': 'iflab@example.com',
        'name': 'IFLab',
        'phone': '+6285179762170',
        'data_key': 'gc8uupscjs0e'
    },
    {
        'address': 'TULT 0604',
        'email': 'company@email.com',
        'name': 'asprak',
        'phone': '+6285179762170',
        'data_key': 'uxalzb21mwcr'
    },
    {
        'address': '',
        'email': 'external@gmail.com',
        'name': 'External Reviewer',
        'phone': '',
        'data_key': 'external'
    }
]


# Function to insert data into the database
def insert_institution_data():
    try:
        # Connect to the database
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        with connection.cursor() as cursor:
            insert_query = """
            INSERT INTO Institutions (data_key, name, address, phone, email)
            VALUES (%s, %s, %s, %s, %s)
            """
            for institution in institution_data2:
                cursor.execute(insert_query, (
                    institution['data_key'], institution['name'], institution['address'],
                    institution['phone'], institution['email']
                ))

            # Commit the transaction
            connection.commit()

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        connection.close()





