import smtplib
from email.message import EmailMessage

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'javad.n077@gmail.com'
EMAIL_PORT_SSL = 465
EMAIL_HOST_PASSWORD = 'cvveluwegjiaenal'
DEFAULT_FROM_EMAIL = 'pinterest'

OTP_CODE_VALID_SECONDS = 300


def send_otp_code(email, code):
    msg = EmailMessage()
    msg['Subject'] = 'confirm email'
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = email
    msg.set_content(f'you can confirm your email by this code: {code}')

    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT_SSL) as server:
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)


def reset_password(email, code):
    msg = EmailMessage()
    msg['Subject'] = 'reset password'
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = email
    msg.set_content(f'use this code to reset your password: {code}')

    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT_SSL) as server:
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)


def get_time(seconds):
    if seconds < 60:
        return f'{seconds} seconds'
    elif seconds < 3600:
        if seconds // 60 == 1:
            return '1 minute'
        return f'{seconds // 60} minutes'
    elif seconds < 86400:
        if seconds // 3600 == 1:
            return '1 hour'
        return f'{seconds // 3600} hours'
    elif seconds < 604800:
        if seconds // 86400 == 1:
            return '1 day'
        return f'{seconds // 86400} days'
    elif seconds // 604800 == 1:
        return '1 week'
    return f'{seconds // 604800} weeks'

