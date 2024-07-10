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


def get_user_by_institution_role(id_institution: str, role: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id_institution = %s AND role = %s"
            cursor.execute(sql, (id_institution, role))
            user_data = cursor.fetchall()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


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


def get_user_by_role_institution(role: str, institution: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE role = %s AND id_institution = %s"
            cursor.execute(sql, (role, institution))
            user_data = cursor.fetchall()
            return user_data
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


def get_institution_by_key(key: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM institutions WHERE data_key = %s"
            cursor.execute(sql, (key, ))
            user_data = cursor.fetchone()
            if user_data:
                return dict(user_data)
            return None
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
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
                    (data_key, id_institution, name, email, role, tanggal, event)
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
                data['event']
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


def get_notification_by_receiver(id_user: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM notifications WHERE id_user = %s"
            cursor.execute(sql, (id_user,))
            user_data = cursor.fetchall()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def insert_new_notification(data: Dict[str, Any]):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                        INSERT INTO notifications
                        (data_key, id_user, event, message, date)
                        VALUES
                        (%s, %s, %s, %s, %s)
                        """
            data_key = generate_random_string()
            new_data = (
                data_key,
                data['id_receiver'],
                data['event'],
                data['message'],
                data['date']
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


def get_log_by_role_institution(role: str, institution: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM logs WHERE role = %s AND id_institution = %s"
            cursor.execute(sql, (role, institution))
            user_data = cursor.fetchall()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def delete_assessment():
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM assessments"
            cursor.execute(sql)
            connection.commit()
            # user_data = cursor.fetchone()
            return True
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def insert_new_assessment(data: Dict[str, Any]):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                    INSERT INTO assessments
                    (data_key,
                    id_institution,
                    id_admin,
                    id_reviewer_internal,
                    id_reviewer_external,
                    tanggal_mulai,
                    hasil_internal,
                    hasil_external,
                    tanggal_nilai,
                    is_done)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
            data_key = generate_random_string()
            query_params = (
                data_key,
                data['id_institution'],
                data['id_admin'],
                data['id_reviewer_internal'],
                data['id_reviewer_external'],
                data['tanggal'],
                data['hasil_internal'],
                data['hasil_external'],
                data['tanggal_nilai'],
                data['is_done']
            )
            cursor.execute(sql, query_params)
            connection.commit()
            # user_data = cursor.fetchone()
            return data_key
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def get_unfinished_assessments_by_institution(key: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM assessments WHERE id_institution = %s AND is_done = 0"
            cursor.execute(sql, (key, ))
            user_data = cursor.fetchone()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_assessment_for_external():
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT *
            FROM assessments
            WHERE id_reviewer_internal IS NOT NULL
                AND is_done = 1
                AND id_reviewer_external IS NULL
            """
            cursor.execute(sql)
            user_data = cursor.fetchall()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_assessment_for_internal(id_institution: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM assessments WHERE id_institution = %s AND id_reviewer_internal = '' AND is_done = 1"
            cursor.execute(sql, (id_institution, ))
            user_data = cursor.fetchall()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_assessment_by_key(key: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM assessments WHERE data_key = %s"
            cursor.execute(sql, (key,))
            user_data = cursor.fetchone()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_assessment_by_institution(id_institution: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM assessments WHERE id_institution = %s"
            cursor.execute(sql, (id_institution,))
            user_data = cursor.fetchall()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def update_user_by_key(data: Dict[str, Any], key: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                    UPDATE users
                    SET id_institution = %s,
                        username = %s,
                        full_name = %s,
                        password = %s,
                        email = %s,
                        role = %s,
                        is_active = %s,
                        phone = %s
                    WHERE data_key = %s
                    """
            query_params = (
                data['id_institution'],
                data['username'],
                data['full_name'],
                data['password'],
                data['email'],
                data['role'],
                data['is_active'],
                data['phone'],
                key
            )
            cursor.execute(sql, query_params)
            connection.commit()
            return key
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def update_assessment_by_key(data: Dict[str, Any], key: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE assessments
                SET id_institution = %s,
                    id_admin = %s,
                    id_reviewer_internal = %s,
                    id_reviewer_external = %s,
                    tanggal_mulai = %s,
                    hasil_internal = %s,
                    hasil_external = %s,
                    tanggal_nilai = %s,
                    is_done = %s
                WHERE data_key = %s
                """
            query_params = (
                data['id_institution'],
                data['id_admin'],
                data['id_reviewer_internal'],
                data['id_reviewer_external'],
                data['tanggal_mulai'],
                data['hasil_internal'],
                data['hasil_external'],
                data['tanggal_nilai'],
                data['is_done'],
                key
            )
            cursor.execute(sql, query_params)
            connection.commit()
            return key
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_points_by_all(id_assessment: str, bab: str, sub_bab: str, point: float):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM points WHERE id_assessment = %s AND bab = %s AND sub_bab = %s AND point = %s"
            cursor.execute(sql, (id_assessment, bab, sub_bab, point))
            user_data = cursor.fetchone()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_points_by_key(key: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM points WHERE data_key = %s"
            cursor.execute(sql, (key, ))
            user_data = cursor.fetchone()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_points_by_proof_filename(filename: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT points.*
            FROM points
            JOIN proof ON points.id_proof = proof.data_key
            WHERE proof.file_name = %s
            """
            cursor.execute(sql, (filename,))
            user_data = cursor.fetchone()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_points_by_assessment(id_assessment: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM points WHERE id_assessment = %s"
            cursor.execute(sql, (id_assessment, ))
            user_data = cursor.fetchall()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_points_by_assessment_sub_bab(id_assessment: str, sub_bab: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM points WHERE id_assessment = %s AND sub_bab = %s ORDER BY point"
            cursor.execute(sql, (id_assessment, sub_bab))
            user_data = cursor.fetchall()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def update_points_by_key(data: Dict[str, Any], key: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
            UPDATE points
            SET id_assessment = %s,
                id_proof = %s,
                bab = %s,
                sub_bab = %s,
                point = %s,
                answer = %s,
                skor = %s
            WHERE data_key = %s
            """
            query_params = (
                data['id_assessment'],
                data['proof'],
                data['bab'],
                data['sub_bab'],
                data['point'],
                data['answer'],
                data['skor'],
                key
            )
            cursor.execute(sql, query_params)
            connection.commit()
            return key
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def get_proof_by_filename(filename: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM proof WHERE file_name = %s"
            cursor.execute(sql, (filename,))
            user_data = cursor.fetchone()
            return user_data
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def insert_new_proof(id_user: str, url: str, file_name: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO proof (data_key, id_user, url, file_name)
                VALUES (%s, %s, %s, %s)
                """
            data_key = generate_random_string()
            cursor.execute(sql, (data_key, id_user, url, file_name))
            connection.commit()
            # user_data = cursor.fetchone()
            return data_key
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def delete_proof_by_key(key: str):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                    DELETE FROM proof WHERE data_key = %s
                    """
            cursor.execute(sql, (key, ))
            connection.commit()
            # user_data = cursor.fetchone()
            return key
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def insert_new_point(data: Dict[str, Any]):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO points
                (data_key, id_assessment, id_proof, bab, sub_bab, point, answer, skor)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
            data_key = generate_random_string()
            query_params = (
                data_key,
                data['id_assessment'],
                data['proof'],
                data['bab'],
                data['sub_bab'],
                data['point'],
                data['answer'],
                data['skor']
            )
            cursor.execute(sql, query_params)
            connection.commit()
            # user_data = cursor.fetchone()
            return data_key
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def insert_new_report(data: Dict[str, Any]):
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USERNAME,
                                 password=DB_PASSWORD,
                                 database=DB_NAME,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                        INSERT INTO logs
                        (data_key, id_institution, name, email, role, tanggal, event)
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
                data['event']
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


