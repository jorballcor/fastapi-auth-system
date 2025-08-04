from typing import Annotated
from db.access import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from db.querys import check_existing_todo, create_todo_query, delete_user_todo, get_all_todos, get_user_todo, update_user_todo
from models.models import TodoCreate, TodoResponse, TodoUpdate, UserCreate
from todos.exceptions import TodoAlreadyExistsException, UserTodoNotFoundException
from users.services import get_current_user


todo_router = APIRouter()


@todo_router.get("/todos")
async def get_todos(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user:  Annotated[UserCreate, Depends(get_current_user)]
):
    return await get_all_todos(db, current_user)


@todo_router.post("/todos", response_model=TodoResponse)
async def create_todo(
    input_todo: TodoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user:  Annotated[UserCreate, Depends(get_current_user)]
):
    if await check_existing_todo(db, input_todo.title):
        raise TodoAlreadyExistsException(title=input_todo.title)    
    
    return await create_todo_query(input_todo, db, current_user)  
    
    
@todo_router.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user:  Annotated[UserCreate, Depends(get_current_user)]
):
    return await get_user_todo(todo_id, db, current_user)


@todo_router.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_updates: TodoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user:  Annotated[UserCreate, Depends(get_current_user)]
):
    return await update_user_todo(
        todo_id,
        todo_updates,
        db,
        current_user
    )
    

@todo_router.delete("/todos/{todo_id}")
async def delete_todo(
    todo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user:  Annotated[UserCreate, Depends(get_current_user)]
):
    return await delete_user_todo(todo_id, db, current_user)