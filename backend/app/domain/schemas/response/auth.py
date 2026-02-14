"""
Authentication Pydantic schemas for response validation.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class SignupUserResponse(BaseModel):
    id: int
    email: EmailStr
    verified: bool
    verify_token: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = "bearer"

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    refresh_token: str
    access_token: str
    token_type: str


class VerifyResetTokenResponse(BaseModel):
    valid: bool


class CommentResponse(BaseModel):
    detail: str


class VerifySignupResponse(BaseModel):
    verified: bool


class VerifyCodeTokenResponse(BaseModel):
    valid: bool


class RequestSignupTokenResponse(BaseModel):
    id: int
    email: EmailStr
    verified: bool
    verify_token: str


class CheckEmailStatusResponse(BaseModel):
    verified: bool


class RequestLoginTokenResponse(BaseModel):
    token: Optional[str] = None


class VerifyLoginResponse(BaseModel):
    verified: bool
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
