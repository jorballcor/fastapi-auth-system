from fastapi import Depends
from sqlalchemy import select
from db.access import get_db
from db.exceptions import DatabaseConnectionError, UserNotFoundException
from db.schemas import Todo, UsersDB
from models.models import TodoCreate, TodoResponse, UserCreate, UserFeatures
from users.services import get_current_user


async def get_user(username: str, db: Depends(get_db)):
    try:
        stmt = select(UsersDB).where(UsersDB.username == username)
        result = await db.execute(stmt)
        db_user = result.scalar_one_or_none()

        if db_user:
            return UserCreate(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                is_active=db_user.is_active,
                password=db_user.password,
            )

        else:
            raise UserNotFoundException(username)

    except DatabaseConnectionError as e:
        raise e.message


async def create_user_query(user: UserCreate, db: Depends(get_db)):
    """
    Create a new user in the database.

    Args:
        user (UserFeatures): The user data to be created.
        db (AsyncSession): The database session.

    Returns:
        User: The created user object.
    """
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    except DatabaseConnectionError as e:
        raise e.message

async def check_existing_user(db: Depends(get_db), username: str, email: str) -> bool:
    existing_user = await db.execute(
        select(UsersDB).where(
            (UsersDB.username == username) | 
            (UsersDB.email == email)
        )
    )
    return existing_user.scalars().first() is not None


async def get_all_todos(db: Depends(get_db), current_user = Depends(get_current_user)):
    """
    Retrieve all todos for the current user.

    Args:
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        List[TodoResponse]: A list of todos for the current user.
    """
    try:
        todos = await db.execute(
            select(Todo).where(Todo.owner_id == current_user.id)
        )
        return todos.scalars().all()

    except DatabaseConnectionError as e:
        raise e.message
    
    
async def check_existing_todo(db: Session, title: str) -> bool:
    try:
        existing_todo = await db.execute(
            select(Todo).where(
                (Todo.title == title)
            )
        )
        return existing_todo.scalars().first() is not None

    except DatabaseConnectionError as e:
        raise e.message


async def create_todo_query(input_todo: TodoCreate, db: Depends(get_db)):
    """
    Create a new todo in the database.

    Args:
        input_todo (TodoCreate): The todo data to be created.
        db (AsyncSession): The database session.

    Returns:
        TodoResponse: The created todo object.
    """
    try:
        todo = Todo(**input_todo.model_dump())
        db.add(todo)
        await db.commit()
        await db.refresh(todo)
        return TodoResponse(**todo)

    except DatabaseConnectionError as e:
        raise e.message