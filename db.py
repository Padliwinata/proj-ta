import deta


deta_obj = deta.Deta("c0RpcWGk6yZe_SPvZvMUFeQUqoqoNj6tTfocaibRkMouJ")

db_user = deta_obj.Base("user")
db_institution = deta_obj.Base("institution")
db_proof = deta_obj.Base("proof")
db_questionnaire = deta_obj.Base("questionnaire")
db_report = deta_obj.Base("report")
db_log = deta_obj.Base("log")
db_point = deta_obj.Base("point")
db_assessment = deta_obj.Base("assessment")

test_db_user = deta_obj.Base("test_user")
test_db_institution = deta_obj.Base("test_institution")
test_db_proof = deta_obj.Base("test_proof")
test_db_questionnaire = deta_obj.Base("test_questionnaire")
test_db_report = deta_obj.Base("test_report")
test_db_log = deta_obj.Base("test_log")
test_db_point = deta_obj.Base("test_point")
test_db_assessment = deta_obj.Base("test_assessment")

drive = deta_obj.Drive("document")
