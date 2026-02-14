import re
from pathlib import Path
from typing import Any, Optional

import httpx
from loguru import logger
from pydantic import EmailStr

from app.core.config import settings


class MailService:
    """Service to handle email operations using Brevo API."""

    _instance: Optional["MailService"] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MailService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Ensure init logic runs only once
        if not hasattr(self, "_initialized"):
            self.api_key = settings.BREVO_API_KEY
            self.sender_email = settings.MAIL_FROM_EMAIL
            self.sender_name = settings.MAIL_FROM_NAME
            self.api_url = "https://api.brevo.com/v3/smtp/email"
            self._initialized = True

    async def send_mail_async(
        self, subject: str, email: EmailStr, body: dict[str, Any], template_name: str
    ) -> None:
        """
        Send an email asynchronously using Brevo.

        Args:
            subject (str): Email subject.
            email (EmailStr): Recipient email address.
            body (dict): Variables to be rendered in the template.
            template_name (str): Name of the template file in app/templates/.
        """
        try:
            html_content = self.render_template(template_name, **body)

            payload = {
                "sender": {
                    "name": self.sender_name,
                    "email": self.sender_email,
                },
                "to": [
                    {
                        "email": email,
                        "name": str(email).split("@")[0],
                    }
                ],
                "subject": subject,
                "htmlContent": html_content,
            }
            headers = {
                "api-key": self.api_key,
                "accept": "application/json",
                "content-type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url, json=payload, headers=headers
                )
                response.raise_for_status()

                logger.info(f"Email sent to {email} with subject: {subject}")
                logger.debug(f"Brevo Response: {response.json()}")

        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            raise

    def render_template(self, template_name: str, **kwargs: Any) -> str:
        """
        Render a basic HTML template with variables.

        Args:
            template_name (str): Template filename.
            **kwargs: Variables to replace in the format {{ variable_name }}.

        Returns:
            str: Rendered HTML content.
        """
        template_path = Path("app/templates") / template_name
        if not template_path.is_file():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        template_content = template_path.read_text(encoding="utf-8")

        for key, value in kwargs.items():
            pattern = r"{{\s*" + re.escape(key) + r"\s*}}"
            template_content = re.sub(pattern, str(value), template_content)

        return template_content

    # Helper methods for specific emails
    async def send_signup_verification_email(
        self, email: str, name: str, code: str
    ) -> None:
        await self.send_mail_async(
            subject="Verify Your Account",
            email=email,
            body={"name": name, "code": code},
            template_name="signup_verification.html",
        )

    async def send_login_otp_email(self, email: str, name: str, code: str) -> None:
        await self.send_mail_async(
            subject="Your Login Verification Code",
            email=email,
            body={"name": name, "code": code},
            template_name="login_otp.html",
        )

    async def send_password_reset_email(self, email: str, reset_link: str) -> None:
        await self.send_mail_async(
            subject="Reset Your Password",
            email=email,
            body={"reset_link": reset_link},
            template_name="password_reset.html",
        )


# Singleton instance
mail_service = MailService()
