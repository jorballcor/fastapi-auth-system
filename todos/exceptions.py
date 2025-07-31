class TodoAlreadyExistsException(Exception):
    """Exception raised when a Todo task already exists in the database."""

    def __init__(self, title: str):
        self.title = title
        super().__init__(f"Todo '{title}' already exists in the database.")
