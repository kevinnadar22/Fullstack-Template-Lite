from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    SIGNUP_VERIFY = "signup_verify"
    LOGIN_VERIFY = "login_verify"
    RESET_PASSWORD = "reset_password"
