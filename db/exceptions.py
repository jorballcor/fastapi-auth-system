from fastapi import HTTPException, status

class UserNotFoundException(HTTPException):
    """Exception raised when a user is not found in the database."""

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User '{username}' not found in the database.")


class DatabaseConnectionError(HTTPException):
    """Exception raised when there is a database connection error."""

    def __init__(self, message: str = "Could not connect to the database."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=message
        )