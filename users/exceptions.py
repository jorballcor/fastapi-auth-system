from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    """Exception raised when credentials are invalid.

    Args:
        HTTPException (401): Unauthorized exception for invalid credentials.
    """

    def __init__(
        self,
        detail: list[str] | str,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserException(HTTPException):
    """Exception raised when a user is inactive.

    Args:
        HTTPException (400): Bad request exception for inactive users.
    """

    def __init__(self, detail: str = "Inactive user"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
