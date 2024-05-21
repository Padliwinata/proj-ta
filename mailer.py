import requests
from requests import Response


# MAILGUN SMTP
def send_simple_message() -> Response:
    return requests.post(
        "https://api.mailgun.net/v3/mail.frauddeterrence.online/messages",
        auth=("api", "5a8657f139dd2b8d3a450f464a4cd43e-a2dd40a3-1ddfc8a5"),
        data={"from": "Excited User <mailgun@mail.frauddeterrence.online>",
              "to": ["aprilio842@gmail.com"],
              "subject": "Hello",
              "text": "Testing some Mailgun awesomeness!"})

