import sys

sys.path.append("...")
from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Path,
    Request,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import db_dependency, get_db
from models import Todos

from .auth import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])

templates = Jinja2Templates(directory="templates")


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=1, le=5)
    completed: bool


@router.get("/", response_class=HTMLResponse)
async def read_todos_user_search(
    request: Request,
    user: user_dependency,
    db: db_dependency,
    search: str | None = None,
):
    print(search)
    if search is None:
        search = ""
    try:
        if user is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        todos = await db.execute(
            select(Todos)
            .where(
                (Todos.title.contains(search)) & (Todos.owner_id == user.get("user_id"))
            )
            .order_by(Todos.completed, Todos.priority)
        )

        todos = todos.scalars().all()
        return templates.TemplateResponse(
            "home.html", {"request": request, "user": user, "todos": todos}
        )
    except Exception as e:
        db.rollback()
        print(str(e))
    # try:
    #     if user is None:
    #         return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    #     todos = await db.execute(
    #         select(Todos).filter(Todos.owner_id == user.get("user_id"))
    #     )
    #     todos = todos.scalars().all()
    #     print(todos)
    #     return templates.TemplateResponse(
    #         "home.html", {"request": request, "user": user, "todos": todos}
    #     )
    # except Exception as e:
    #     db.rollback()
    #     print(str(e))


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    try:
        user = await get_current_user(request)
        if user is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        return templates.TemplateResponse(
            "add-todo.html", {"request": request, "user": user}
        )
    except Exception as e:
        print(str(e))


@router.post("/add-todo", response_class=HTMLResponse)
async def create_new_todo(
    request: Request,
    db: db_dependency,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
):
    try:
        user = await get_current_user(request)
        if user is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        todo = Todos(
            title=title,
            description=description,
            priority=priority,
            owner_id=user.get("user_id"),
        )
        db.add(todo)
        await db.commit()
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        db.rollback()
        print(str(e))


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(
    request: Request,
    db: db_dependency,
    user: user_dependency,
    todo_id: int = Path(gt=0),
):
    try:
        if user is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        todo_item = await db.execute(
            select(Todos).where(
                (Todos.id == todo_id) & (Todos.owner_id == user.get("user_id"))
            )
        )
        todo_item = todo_item.scalars().first()

        return templates.TemplateResponse(
            "edit-todo.html", {"request": request, "user": user, "todo": todo_item}
        )
    except Exception as e:
        db.rollback()
        print(str(e))


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(
    request: Request,
    db: db_dependency,
    user: user_dependency,
    todo_id: int,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
):
    try:
        if user is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        todo_item = await db.execute(select(Todos).filter(Todos.id == todo_id))
        todo_item = todo_item.scalars().first()
        print(title)
        todo_item.title = title
        todo_item.description = description
        todo_item.priority = priority

        db.add(todo_item)
        await db.commit()
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        db.rollback()
        print(str(e))


@router.get("/delete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(
    request: Request,
    db: db_dependency,
    user: user_dependency,
    todo_id: int,
):
    try:
        if user is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

        todo_item = await db.execute(
            select(Todos)
            .filter(Todos.id == todo_id)
            .filter(Todos.owner_id == user.get("user_id"))
        )
        todo_item = todo_item.scalars().first()

        if todo_item is None:
            return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        # db.execute(select(Todos).filter(Todos.id == todo_id).delete()
        await db.delete(todo_item)

        await db.commit()
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        db.rollback()
        print(str(e))


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(
    request: Request, user: user_dependency, db: db_dependency, todo_id: int
):
    try:
        if user is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

        todo_item = await db.execute(select(Todos).filter(Todos.id == todo_id))
        todo_item = todo_item.scalar_one_or_none()

        todo_item.completed = not todo_item.completed
        db.add(todo_item)
        await db.commit()
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        db.rollback()
        print(str(e))


# @router.get("/")
# async def read_all(user: user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(
#             status_code=401, detail="Invalid authentication credentials"
#         )
#     return db.execute(select(Todos).filter(Todos.owner_id == user.get("user_id")).all()


# @router.get("/{todo_id}", status_code=status.HTTP_200_OK)
# async def read_one(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
#     todo_item = (
#         db.query(Todos)
#         .filter(Todos.id == todo_id)
#         .filter(Todos.owner_id == user.get("id"))
#         .first()
#     )
#     if todo_item is not None:
#         return todo_item
#     raise HTTPException(status_code=404, detail="Item not found")


# @router.post("", status_code=status.HTTP_201_CREATED)
# async def create_one(user: user_dependency, db: db_dependency, todo_req: TodoRequest):
#     if user is None:
#         raise HTTPException(
#             status_code=401, detail="Invalid authentication credentials"
#         )
#     todo_item = Todos(**todo_req.dict(), owner_id=user.get("id"))
#     db.add(todo_item)
#     db.commit()


# @router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def update_one(
#     user: user_dependency,
#     db: db_dependency,
#     todo_req: TodoRequest,
#     todo_id: int = Path(gt=0),
# ):
#     if user is None:
#         raise HTTPException(
#             status_code=401, detail="Invalid authentication credentials"
#         )
#     todo_item = (
#         db.query(Todos)
#         .filter(Todos.id == todo_id)
#         .filter(Todos.owner_id == user.get("id"))
#         .first()
#     )
#     if todo_item is not None:
#         todo_item.title = todo_req.title
#         todo_item.description = todo_req.description
#         todo_item.priority = todo_req.priority
#         todo_item.completed = todo_req.completed
#         db.add(todo_item)
#         db.commit()
#         return
#     raise HTTPException(status_code=404, detail="Item not found")


# @router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_one(
#     user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
# ):
#     if user is None:
#         raise HTTPException(
#             status_code=401, detail="Invalid authentication credentials"
#         )
#     todo_item = (
#         db.query(Todos)
#         .filter(Todos.id == todo_id)
#         .filter(Todos.owner_id == user.get("id"))
#         .first()
#     )
#     if todo_item is not None:
#         db.delete(todo_item)
#         db.commit()
#         return
#     raise HTTPException(status_code=404, detail="Item not found")
