from asgiref.sync import async_to_sync

from app.integrations import mail_service

from ..celery_app import task


@task(name="send_signup_verification_email_task")
def send_signup_verification_email_task(email: str, name: str, code: str):
    """Celery task to send signup verification email."""
    async_to_sync(mail_service.send_signup_verification_email)(email, name, code)


@task(name="send_login_otp_email_task")
def send_login_otp_email_task(email: str, name: str, code: str):
    """Celery task to send login OTP email."""
    async_to_sync(mail_service.send_login_otp_email)(email, name, code)


@task(name="send_password_reset_email_task")
def send_password_reset_email_task(email: str, reset_link: str):
    """Celery task to send password reset email."""
    async_to_sync(mail_service.send_password_reset_email)(email, reset_link)
