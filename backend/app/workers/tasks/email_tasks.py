# from asgiref.sync import async_to_sync

# from ..celery_app import task


# @task(name="send_signup_verification_email_task")
# def send_signup_verification_email_task(email: str, name: str, code: str):
#     """Celery task to send signup verification email."""
#     async_to_sync(mail_service.send_signup_verification_email)(email, name, code)


