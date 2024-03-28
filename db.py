import deta


deta_obj = deta.Deta("c0YK3LGkSzAM_WPS5wNp7NafechQa2id7Q7Sd9Z8UaxmZ")

db_user = deta_obj.Base("user")
db_institution = deta_obj.Base("institution")
db_proof = deta_obj.Base("proof")
db_questionnaire = deta_obj.Base("questionnaire")
db_report = deta_obj.Base("report")
db_log = deta_obj.Base("log")
db_point = deta_obj.Base("point")

drive = deta_obj.Drive("document")
