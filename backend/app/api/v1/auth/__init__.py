"""
Authentication API routes for user signup, login, and OAuth.

This FastAPI router module handles all authentication-related endpoints.

Routes included:
- POST /auth/register: User registration
- POST /auth/register/otp: Request registration verification token
- POST /auth/register/verify: Verify registration and activate account
- POST /auth/login: User login with credentials
- POST /auth/login/otp: Request login verification token (OTP)
- POST /auth/login/verify: Verify login OTP and issue session tokens
- POST /auth/password-reset: Request password reset link
- POST /auth/password-reset/verify: Verify password reset token
- POST /auth/password-reset/confirm: Reset user password
- GET /auth/google: Initiate Google OAuth flow
- GET /auth/google/callback: Handle Google OAuth callback
- POST /auth/logout: Logout and invalidate session
- POST /auth/refresh: Refresh access token
- POST /auth/email/status: Check if email is verified
- POST /auth/verify/token: Verify validity of any code token
"""

from fastapi import APIRouter

from .common import router as common_router
from .google import router as google_router
from .login import router as login_router
from .password import router as password_router
from .register import router as register_router

router = APIRouter(prefix="/auth", tags=["auth"])

# Include sub-routers for different authentication functionalities
router.include_router(register_router)
router.include_router(login_router)
router.include_router(google_router)
router.include_router(password_router)
router.include_router(common_router)
