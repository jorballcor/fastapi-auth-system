class TodoAlreadyExistsException(Exception):
    """Exception raised when a Todo task already exists in the database."""

    def __init__(self, title: str):
        self.title = title
        super().__init__(f"Todo '{title}' already exists in the database.")


class UserTodoNotFoundException(Exception):
    """Exception raised when no todo is found for a user."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"No todo found for user with ID {user_id}.")