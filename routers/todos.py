from fastapi import (
    FastAPI,
    APIRouter,
    Depends,
    Path,
    Body,
    HTTPException,
    status,
    Request,
)
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi.responses import RedirectResponse

from models import Todos
from db import db_dependency, get_db
from .auth import get_current_user

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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
async def read_all_by_user(request: Request, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    todos = (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("user_id"))
        .order_by(Todos.priority.desc())
        .all()
    )
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(
    request: Request,
    db: db_dependency,
    user: user_dependency,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    todo_item = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("user_id"))
        .first()
    )

    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": todo_item}
    )


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(
    request: Request,
    db: db_dependency,
    todo_id: int,
    title: str,
    description: str,
    priority: int,
    completed: bool,
):
    todo_item = db.query(Todos).filter(Todos.id == todo_id).first()
    todo_item.title = title
    todo_item.description = description
    todo_item.priority = priority
    todo_item.completed = completed
    db.add(todo_item)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.post("delete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(
    request: Request,
    db: db_dependency,
    todo_id: int,
):
    todo_item = db.query(Todos).filter(Todos.id == todo_id).first()
    db.delete(todo_item)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, db: db_dependency, todo_id: int):
    todo_item = db.query(Todos).filter(Todos.id == todo_id).first()
    todo_item.completed = True
    db.add(todo_item)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


# @router.get("/")
# async def read_all(user: user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(
#             status_code=401, detail="Invalid authentication credentials"
#         )
#     return db.query(Todos).filter(Todos.owner_id == user.get("user_id")).all()


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
