import sys

sys.path.append("...")
from fastapi import FastAPI, APIRouter, Depends, Path, Body, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel, Field

from models import Todos

from .auth import get_current_user
from db import db_dependency


router = APIRouter(prefix="/admin", tags=["admin"])

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return db.query(Todos).all()


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    todo_item = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_item is not None:
        db.delete(todo_item)
        db.commit()
        return
    raise HTTPException(status_code=404, detail="Item not found")
