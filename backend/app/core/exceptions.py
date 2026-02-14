# app/exceptions.py


class AppException(Exception):
    status_code: int = 500
    default_detail: str = "Internal Server Error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail


class NotFoundError(AppException):
    status_code = 404
    default_detail = "Resource not found"


class BadRequestError(AppException):
    status_code = 400
    default_detail = "Bad request"


class ConflictError(AppException):
    status_code = 409
    default_detail = "Conflict"


class UnauthorizedError(AppException):
    status_code = 401
    default_detail = "Unauthorized"


class GoogleAuthException(AppException):
    status_code = 400
    default_detail = "Google authentication failed"
