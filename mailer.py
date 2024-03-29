import typing

from mailersend import emails

api_key = "mlsn.098ac84e8ae8eea813141f0d36c6ef8bceeda6f8f5956819065fcea89d9f558b"


def send_confirmation(userid: str, email: str, name: str) -> None:
    mailer = emails.NewEmail(api_key)

    mail_body: typing.Dict[str, typing.Any] = {}

    mail_from = {
        "name": "Rama Padliwinata",
        "email": "example@trial-3zxk54vn67qljy6v.mlsender.net"
    }

    recipients = [
        {
            "name": name,
            "email": email
        }
    ]

    reply_to = {
        "Name": "Rama Padliwinata",
        "email": "rpadliwinata@gmail.com"
    }

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Silakan Konfirmasi Email Anda", mail_body)
    mailer.set_html_content(
        f"Klik link ini untuk mengonfirmasi email anda <a href='https://127.0.0.1:8000/verify/{userid}'>Klik!</a>",
        mail_body
    )
    mailer.set_plaintext_content(f"Silakan klik link ini jika tulisan gagal diklik https://127.0.0.1:8000/verify/{userid}'", mail_body)
    mailer.set_reply_to(reply_to, mail_body)
    mailer.send(mail_body)

# print(mailer.send(mail_body))


