from fastapi import HTTPException, status


class TodoAlreadyExistsException(HTTPException):
    """Exception raised when a Todo task already exists in the database."""

    def __init__(self, title: str):
        self.title = title
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Todo '{title}' already exists in the database."
        )


class UserTodoNotFoundException(HTTPException):
    """Exception raised when no todo is found for a user."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No todo found for user with ID {user_id}."
        )
        

class DeleteTodoException(HTTPException):
    """Exception raised when a todo cannot be deleted."""

    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Todo with ID {todo_id} could not be deleted."
        )
        

class UpdateTodoException(HTTPException):
    """Exception raised when a todo cannot be updated."""

    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Todo with ID {todo_id} not found, it could not be updated."
        )