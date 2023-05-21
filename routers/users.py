import sys

sys.path.append("..")

from fastapi import (
    FastAPI,
    APIRouter,
    Depends,
    Path,
    Body,
    HTTPException,
    status,
    Request,
    Form,
)
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi.responses import RedirectResponse

from models import Todos, User
from db import db_dependency, get_db
from .auth import get_current_user, get_password_hash, verify_password

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"description": "Not found"}}
)

templates = Jinja2Templates(directory="templates")
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserRequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=3)
    password2: str = Field(min_length=3)


@router.get("/edit-pwd", response_class=HTMLResponse)
async def edit_pwd(request: Request, user: user_dependency):
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "edit-pwd.html", {"request": request, "user": user}
    )


@router.post("/edit-pwd", response_class=HTMLResponse)
async def edit_user_pwd(
    request: Request,
    user: user_dependency,
    db: db_dependency,
    username: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
):
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    if password == password2:
        return templates.TemplateResponse(
            "edit-pwd.html",
            {"request": request, "user": user, "msg": "Passwords match"},
        )

    user_model = await db.execute(select(User).filter(User.id == user.get("user_id")))
    user_model = user_model.scalars().first()
    msg = "Invalid username or password"

    if user_model is not None:
        if user_model.username == username and await verify_password(
            password, user_model.password
        ):
            user_model.password = await get_password_hash(password2)
            db.add(user_model)
            await db.commit()
            msg = "Password updated"

    return templates.TemplateResponse(
        "edit-pwd.html", {"request": request, "user": user, "msg": msg, "user": user}
    )


# from fastapi import FastAPI, APIRouter, Depends, Path, Body, HTTPException, status

# from typing import Annotated
# from pydantic import BaseModel, Field
# from passlib.context import CryptContext

# from .auth import get_current_user
# from db import db_dependency
# from models import User


# router = APIRouter(prefix="/users", tags=["users"])

# user_dependency = Annotated[dict, Depends(get_current_user)]
# bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")


# # get_user: this endpoint should return all information about the user that is currently logged in.
# @router.get("/", status_code=status.HTTP_200_OK)
# async def get_user_info(user: user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(
#             status_code=401, detail="Invalid authentication credentials"
#         )
#     return db.query(User).filter(User.id == user.get("user_id")).first()


# # change_password: this endpoint should allow a user to change their current password.
# class ChangePasswordRequest(BaseModel):
#     password: str = Field(min_length=3)
#     new_password: str = Field(min_length=3)


# @router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
# async def change_password(
#     user: user_dependency, db: db_dependency, change_password_req: ChangePasswordRequest
# ):
#     if user is None:
#         raise HTTPException(
#             status_code=401, detail="Invalid authentication credentials"
#         )
#     user_model = db.query(User).filter(User.id == user.get("user_id")).first()
#     if not bcrypt.verify(change_password_req.password, user_model.password):
#         raise HTTPException(status_code=401, detail="Invalid password")
#     user_model.password = bcrypt.hash(change_password_req.new_password)
#     db.commit()
#     return
