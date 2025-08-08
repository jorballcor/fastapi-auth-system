from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.access import get_db
from db.exceptions import DatabaseConnectionError
from db.todo_querys import (
    check_existing_todo,
    create_todo_query,
    delete_user_todo,
    get_all_todos,
    get_user_todo,
    update_user_todo,
)
from models.models import TodoCreate, TodoResponse, TodoUpdate, UserCreate
from todos.exceptions import DeleteTodoException, TodoAlreadyExistsException, UpdateTodoException, UserTodoNotFoundException
from users.services import get_current_user

todo_router = APIRouter()


@todo_router.get("/todos", response_model=List[TodoResponse])
async def get_todos(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserCreate, Depends(get_current_user)],
):
    try:
        todos = await get_all_todos(db, current_user)
        return [TodoResponse.model_validate(t) for t in todos]
    except DatabaseConnectionError as e:
        # Surface DB issues as 500s at the API edge
        #raise HTTPException(status_code=500, detail=str(e))
        raise e.message  


@todo_router.post("/todos", response_model=TodoResponse)
async def create_todo(
    input_todo: TodoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserCreate, Depends(get_current_user)],
):
    try:
        if await check_existing_todo(db, input_todo.title, current_user):
            # Tests only check status code; message is clear for clients
            #raise HTTPException(status_code=400, detail="Todo with this title already exists")
            raise TodoAlreadyExistsException(title=input_todo.title)

        todo = await create_todo_query(input_todo, db, current_user)
        return TodoResponse.model_validate(todo)
    except DatabaseConnectionError as e:
        raise e.message  # Surface DB issues as 500s at the API edge


@todo_router.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserCreate, Depends(get_current_user)],
):
    try:
        todo = await get_user_todo(todo_id, db, current_user)
        if not todo:
            # Exact text expected by tests
            #raise HTTPException(status_code=404, detail="Todo not found")
            raise UserTodoNotFoundException(user_id=current_user.id)
        return TodoResponse.model_validate(todo)
    except DatabaseConnectionError as e:
        raise e


@todo_router.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_updates: TodoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserCreate, Depends(get_current_user)],
):
    try:
        updated = await update_user_todo(todo_id, todo_updates, db, current_user)
        if not updated:
            #raise HTTPException(status_code=404, detail="Todo not found")
            raise UpdateTodoException(todo_id=todo_id)
        return TodoResponse.model_validate(updated)
    except DatabaseConnectionError as e:
        raise e


@todo_router.delete("/todos/{todo_id}")
async def delete_todo(
    todo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserCreate, Depends(get_current_user)],
):
    try:
        deleted = await delete_user_todo(todo_id, db, current_user)
        if not deleted:
            #raise HTTPException(status_code=404, detail="Todo not found")
            raise DeleteTodoException(todo_id=todo_id)
        # Matches tests: exact string with the id
        return {"message": f"Todo {todo_id} deleted successfully"}
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=500, detail=str(e))
