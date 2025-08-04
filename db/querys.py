from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.access import get_db
from db.exceptions import DatabaseConnectionError
from db.schemas import Todo, UsersDB
from models.models import TodoCreate, TodoResponse, UserCreate
from todos.exceptions import DeleteTodoException, UpdateTodoException, UserTodoNotFoundException
from users.dependencies import get_current_user



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


from sqlalchemy import select
from db.engine import AsyncSessionLocal
from users.helper import get_password_hash
from common.logger_config import logger
from users.services import SUPERUSER_EMAIL, SUPERUSER_PASSWORD, SUPERUSER_USERNAME


async def create_initial_admin_user(db: AsyncSessionLocal()):
    try:
        result = await db.execute(select(UsersDB).limit(1))
        first_user = result.scalar_one_or_none()
        if first_user:
            logger.info("Un utilisateur existe déjà, aucun admin initial créé.")
            return

        first_user = UsersDB(
            username=SUPERUSER_USERNAME,
            email=SUPERUSER_EMAIL,
            password=get_password_hash(SUPERUSER_PASSWORD),
            is_active=True,
        )
        db.add(first_user)
        await db.commit()
        logger.info("Utilisateur admin initial créé")
    except Exception as e:
        logger.error(f"Échec de la création de l'utilisateur admin initial : {e}")


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
    
    
async def check_existing_todo(db: Depends(get_db), title: str) -> bool:
    try:
        existing_todo = await db.execute(
            select(Todo).where(
                (Todo.title == title)
            )
        )
        return existing_todo.scalars().first() is not None

    except DatabaseConnectionError as e:
        raise e.message


async def create_todo_query(
    input_todo: TodoCreate, 
    db: AsyncSession,
    current_user: UsersDB
):
    try:
        todo = Todo(
            title=input_todo.title,
            description=input_todo.description,
            done=input_todo.done,
            owner_id=current_user.id  
        )
        db.add(todo)
        await db.commit()
        await db.refresh(todo)
        return TodoResponse.from_orm(todo)
    except DatabaseConnectionError as e:
        await db.rollback()
        raise e.message
    

async def fetch_user_todo(
    todo_id: int, 
    db: Depends(get_db), 
    current_user = Depends(get_current_user)
) -> TodoResponse:
    todos = await db.execute(
            select(Todo).where(
                Todo.id == todo_id, 
                Todo.owner_id == current_user.id
        ))
    todo = todos.scalars().first()
    return todo


async def get_user_todo(
    todo_id: int, 
    db: Depends(get_db), 
    current_user = Depends(get_current_user)
):
    try:
        todo = fetch_user_todo(todo_id, db, current_user)
        if not todo:
            raise UserTodoNotFoundException(todo_id)
        
        return TodoResponse(**todo.model_dump())
    
    except DatabaseConnectionError as e:
        raise e.message
    
    
async def update_user_todo(
    todo_id: int,
    todo_updates: TodoCreate, 
    db: Depends(get_db),
    current_user = Depends(get_current_user)
) -> TodoResponse:
    try:
        existing_todo = fetch_user_todo(todo_id, db, current_user)
        if not existing_todo:
            raise UserTodoNotFoundException(todo_id)
        
        update_data = todo_updates.model_dump(exclude_unset=True)  # Ignore None/empty fields
        for field, value in update_data.items():
            setattr(existing_todo, field, value)
        
        await db.commit()
        await db.refresh(existing_todo)  # Get updated values
        
        return TodoResponse(**existing_todo.model_dump())
    
    except DatabaseConnectionError as e:
        await db.rollback()
        raise e.message
    
    except Exception as e:
        await db.rollback()
        raise UpdateTodoException(todo_id=todo_id)
        
        
async def delete_user_todo(
    todo_id: int,
    db: Depends(get_db),
    current_user = Depends(get_current_user)
) -> dict:
    try:
        todo = fetch_user_todo(todo_id, db, current_user)
        if not todo:
            raise UserTodoNotFoundException(todo_id)
        
        await db.delete(todo)
        await db.commit()
        
        return {"message": f"Todo {todo_id} deleted successfully"}
    
    except DatabaseConnectionError as e:
        await db.rollback()
        raise e.message
    
    except Exception as e:
        await db.rollback()
        raise DeleteTodoException(todo_id=todo_id)