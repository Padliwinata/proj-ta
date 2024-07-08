import random
import string
from typing import Optional, Dict, Any

import deta
import pymysql.cursors

from settings import DATA_KEY, DB_HOST, DB_NAME, DB_PASSWORD, DB_USERNAME


deta_obj = deta.Deta(DATA_KEY)

db_user = deta_obj.Base("user")
db_institution = deta_obj.Base("institution")
db_proof = deta_obj.Base("proof")
db_questionnaire = deta_obj.Base("questionnaire")
db_report = deta_obj.Base("report")
db_log = deta_obj.Base("log")
db_point = deta_obj.Base("point")
db_assessment = deta_obj.Base("assessment")
db_notification = deta_obj.Base("notification")

drive = deta_obj.Drive("document")


def generate_random_string() -> str:
    characters = string.digits + string.ascii_lowercase
    random_string = ''.join(random.choice(characters) for _ in range(12))
    return random_string


def get_user_by_username(username: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username, ))
            user_data = cursor.fetchone()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_user_by_email(email: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email, ))
            user_data = cursor.fetchone()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_user_by_username_email(username: str, email: str) -> Optional[Dict[str, Any]]:
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s OR email = %s"
            cursor.execute(sql, (username, email))
            user_data = cursor.fetchone()
            if user_data:
                return dict(user_data)
            return None
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_user_by_all(username: str, email: str, phone: str) -> Optional[Dict[str, Any]]:
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s OR email = %s OR phone = %s"
            cursor.execute(sql, (username, email, phone))
            user_data = cursor.fetchone()
            if user_data:
                return dict(user_data)
            return None
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_user_by_key(key: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE data_key = %s"
            cursor.execute(sql, (key,))
            user_data = cursor.fetchone()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_all_user_by_role(role: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE role = %s"
            cursor.execute(sql, (role,))
            user_data = cursor.fetchall()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def alter_user_status(key: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE data_key = %s"
            cursor.execute(sql, (key,))
            user_data = cursor.fetchone()
            alter_query = "UPDATE users SET is_active = %s WHERE data_key = %s"
            if user_data['is_active']:
                status = 0
            else:
                status = 1
            cursor.execute(alter_query, (status, key))
            connection.commit()
            user_data['is_active'] = not user_data['is_active']
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def delete_user_by_username(username: str) -> bool:
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM users WHERE username = %s"
            cursor.execute(sql, (username, ))
            connection.commit()
            return True
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def get_institution_by_all(phone: str, email: str) -> Optional[Dict[str, Any]]:
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM institutions WHERE email = %s OR phone = %s"
            cursor.execute(sql, (phone, email))
            user_data = cursor.fetchone()
            if user_data:
                return dict(user_data)
            return None
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def insert_new_institution(name: str, address: str, phone: str, email: str) -> Optional[str]:
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO institutions (data_key, name, address, phone, email)
            VALUES (%s, %s, %s, %s, %s)
            """
            data_key = generate_random_string()
            cursor.execute(sql, (data_key, name, address, phone, email))
            connection.commit()
            # user_data = cursor.fetchone()
            return data_key
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def insert_new_user(username: str,
                    full_name: str,
                    password: str,
                    email: str,
                    phone: str,
                    role: str,
                    id_institution: str,
                    is_active: bool) -> Optional[str]:
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO users
                (data_key, id_institution, username, full_name, password, email, role, is_active, phone)
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            data_key = generate_random_string()
            cursor.execute(sql, (data_key, id_institution, username, full_name,
                                 password, email, role, is_active, phone))
            connection.commit()
            return data_key
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def insert_new_log(data: Dict[str, Any]) -> Optional[str]:
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                    INSERT INTO logs
                    (data_key, id_institution, username, email, role, tanggal, event)
                    VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                    """
            data_key = generate_random_string()
            new_data = (
                data_key,
                data['id_institution'],
                data['name'],
                data['email'],
                data['role'],
                data['tanggal'],
                'logged in'
            )
            cursor.execute(sql, new_data)
            connection.commit()
            return data_key
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()



