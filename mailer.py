import typing

from mailersend import emails

api_key = "mlsn.098ac84e8ae8eea813141f0d36c6ef8bceeda6f8f5956819065fcea89d9f558b"


mailer = emails.NewEmail(api_key)

mail_body: typing.Dict[str, typing.Any] = {}

mail_from = {
    "name": "Rama Padliwinata",
    "email": "example@trial-3zxk54vn67qljy6v.mlsender.net"
}

recipients = [
    {
        "name": "Reva Doni Aprilio",
        "email": "aprilio842@gmail.com"
    }
]

reply_to = {
    "Name": "Rama Padliwinata",
    "email": "rpadliwinata@gmail.com"
}

mailer.set_mail_from(mail_from, mail_body)
mailer.set_mail_to(recipients, mail_body)
mailer.set_subject("Hello!", mail_body)
mailer.set_html_content("This is example", mail_body)
mailer.set_plaintext_content("This is also example but in plain", mail_body)
mailer.set_reply_to(reply_to, mail_body)

print(mailer.send(mail_body))


