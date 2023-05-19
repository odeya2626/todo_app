from fastapi import FastAPI, APIRouter, Depends, Path, Body, HTTPException, status

from typing import Annotated
from pydantic import BaseModel, Field
from passlib.context import CryptContext

from .auth import get_current_user
from db import db_dependency
from models import User


router = APIRouter(prefix="/users", tags=["users"])

user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")


# get_user: this endpoint should return all information about the user that is currently logged in.
@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_info(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return db.query(User).filter(User.id == user.get("user_id")).first()


# change_password: this endpoint should allow a user to change their current password.
class ChangePasswordRequest(BaseModel):
    password: str = Field(min_length=3)
    new_password: str = Field(min_length=3)


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency, db: db_dependency, change_password_req: ChangePasswordRequest
):
    if user is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    user_model = db.query(User).filter(User.id == user.get("user_id")).first()
    if not bcrypt.verify(change_password_req.password, user_model.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    user_model.password = bcrypt.hash(change_password_req.new_password)
    db.commit()
    return
