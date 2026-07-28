import smtplib
from email.message import EmailMessage


def send_email(
    sender: str,
    app_password: str,
    recipient: str,
    subject: str,
    body: str,
) -> None:
    if not sender or not app_password or not recipient:
        raise RuntimeError(
            "Email settings are missing. Check EMAIL_USER, EMAIL_PASSWORD and EMAIL_TO."
        )

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(message)
