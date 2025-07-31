from typing import Annotated
from db.access import get_db
from fastapi import APIRouter, Depends

from db.querys import check_existing_todo, create_todo_query, get_all_todos
from models.models import TodoCreate, TodoResponse
from todos.exceptions import TodoAlreadyExistsException
from users.services import get_current_user


todo_router = APIRouter(prefix="/todo")


@todo_router.get()
async def get_todos(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user:  Annotated[UserCreate, Depends(get_current_user)]
):
    todos = await get_all_todos(db, current_user)
    return todos


@todo_router.post(response_model=TodoResponse)
async def create_todo(
    input_todo: TodoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user:  Annotated[UserCreate, Depends(get_current_user)]
):
    if await check_existing_todo(db, input_todo.title, input_todo.description):
        raise TodoAlreadyExistsException(title=input_todo.title)    
    
    created_todo = await create_todo_query(input_todo, db)
    return created_todo  
    
    
@todo_router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user:  Annotated[UserCreate, Depends(get_current_user)]
):
                   
                   ):
    """
    Retrieve a specific todo by its ID for the current user.

    Args:
        todo_id (int): The ID of the todo to retrieve.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        TodoResponse: The todo object if found, otherwise raises an exception.
    """
    todos = await db.execute(
        select(Todo).where(Todo.id == todo_id, Todo.owner_id == current_user.id)
    )
    todo = todos.scalars().first()
    
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return TodoResponse(**todo.model_dump())