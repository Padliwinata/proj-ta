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


# def get_user_by_username(username: str):
#     connection = pymysql.connect(host=DB_HOST,
#                                  user=DB_USERNAME,
#                                  password=DB_PASSWORD,
#                                  database=DB_NAME)
#
#     try:
#         with connection.cursor() as cursor:
#             sql = "SELECT * FROM Users WHERE username = %s"
#             cursor.execute(sql, (username, ))
#             user_data = cursor.fetchone()
#             return user_data
