class UserNotFoundException(Exception):
    """Exception raised when a user is not found in the database."""

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User '{username}' not found in the database.")


class DatabaseConnectionError(Exception):
    """Exception raised when there is a database connection error."""

    def __init__(self, message: str = "Could not connect to the database."):
        super().__init__(message)
