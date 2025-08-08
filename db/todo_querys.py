from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.exceptions import DatabaseConnectionError
from db.schemas import Todo
from models.models import TodoCreate, TodoUpdate, UserCreate  # make sure UserCreate has `.id`

async def get_all_todos(
    db: AsyncSession,
    current_user: UserCreate,
) -> List[Todo]:
    """
    Return all todos (ORM objects) for the current user.
    """
    try:
        result = await db.execute(select(Todo).where(Todo.owner_id == current_user.id))
        return result.scalars().all()
    except DatabaseConnectionError:
        # Let the endpoint convert to an HTTP 500
        raise

async def check_existing_todo(
    db: AsyncSession,
    title: str,
    current_user: UserCreate,
) -> bool:
    """
    Check if a todo with the same title already exists for this user.
    """
    try:
        result = await db.execute(
            select(Todo).where(Todo.title == title, Todo.owner_id == current_user.id)
        )
        return result.scalars().first() is not None
    except DatabaseConnectionError:
        raise

async def create_todo_query(
    input_todo: TodoCreate,
    db: AsyncSession,
    current_user: UserCreate,
) -> Todo:
    """
    Insert and return the created ORM Todo.
    """
    try:
        todo = Todo(
            title=input_todo.title,
            description=input_todo.description,
            done=input_todo.done,
            owner_id=current_user.id,
        )
        db.add(todo)
        await db.commit()
        await db.refresh(todo)
        return todo
    except DatabaseConnectionError:
        await db.rollback()
        raise

async def fetch_user_todo(
    todo_id: int,
    db: AsyncSession,
    current_user: UserCreate,
) -> Optional[Todo]:
    """
    Return a single ORM Todo for this user, or None if not found.
    """
    result = await db.execute(
        select(Todo).where(Todo.id == todo_id, Todo.owner_id == current_user.id)
    )
    return result.scalars().first()

async def get_user_todo(
    todo_id: int,
    db: AsyncSession,
    current_user: UserCreate,
) -> Optional[Todo]:
    """
    Alias that fetches a single todo; kept for compatibility.
    """
    try:
        return await fetch_user_todo(todo_id, db, current_user)
    except DatabaseConnectionError:
        raise

async def update_user_todo(
    todo_id: int,
    todo_updates: TodoUpdate,
    db: AsyncSession,
    current_user: UserCreate,
) -> Optional[Todo]:
    """
    Apply partial/full updates to a todo. Returns updated ORM object or None if not found.
    """
    try:
        existing = await fetch_user_todo(todo_id, db, current_user)
        if not existing:
            return None

        # Accept partial updates (tests send PUT with partial body)
        update_data = todo_updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)

        await db.commit()
        await db.refresh(existing)
        return existing
    except DatabaseConnectionError:
        await db.rollback()
        raise

async def delete_user_todo(
    todo_id: int,
    db: AsyncSession,
    current_user: UserCreate,
) -> bool:
    """
    Delete a todo. Returns True if deleted, False if not found.
    """
    try:
        todo = await fetch_user_todo(todo_id, db, current_user)
        if not todo:
            return False

        await db.delete(todo)
        await db.commit()
        return True
    except DatabaseConnectionError:
        await db.rollback()
        raise
