from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from src.settings.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM     = settings.MAIL_FROM,
    MAIL_PORT     = settings.MAIL_PORT,
    MAIL_SERVER   = settings.MAIL_SERVER,
    MAIL_STARTTLS =settings.MAIL_STARTTLS,
    MAIL_SSL_TLS  =settings.MAIL_SSL_TLS,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
)

async def send_email(
    email_to: EmailStr,
    token: str
):
    message = MessageSchema(
        subject="🛡 Підтвердження Email на SmartMessenger",
        recipients=[email_to],
        body=(
            f"Вставте цей токен у поле верифікації:\n\n"
            f"{token}\n\n"
            f"Це посилання дійсне 24 години.\n\n"
            f"Якщо ви не реєструвалися на SmartMessenger — просто проігноруйте цей лист."
        ),
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)



async def send_generic_email(
    email_to: EmailStr,
    subject: str,
    body: str
):
    """
    Відправляє лист на будь-яку тему з будь-яким тілом.
    """
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype="plain",
    )
    fm = FastMail(conf)
    await fm.send_message(message)