from fastapi import FastAPI, APIRouter, Depends, Path, Body, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import JWTError, jwt
from datetime import timedelta, datetime

from db import db_dependency
from models import User

router = APIRouter(prefix="/auth", tags=["auth"])
SECRET_KEY = "vghlkjk,mcxsseaerfuiojml, mnvfxdsredui786554432"
ALGORITHM = "HS256"

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=3)
    email: str = Field(min_length=3)
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    disabled: bool = Field(default=True)
    role: str = Field(default="user")
    phone_number: str or None = Field(default=None)


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt.verify(password, user.password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, user_role: str, expires_delta: timedelta
):
    to_encode = {"username": username, "user_id": user_id, "user_role": user_role}
    expires = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        user_id: int = payload.get("user_id")
        user_role: str = payload.get("user_role")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
        return {"username": username, "user_id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = User(
        password=bcrypt.hash(create_user_request.password),
        **create_user_request.dict(exclude={"password"})
    )
    db.add(create_user_model)
    db.commit()

    return create_user_model


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=30)
    )
    return {"access_token": token, "token_type": "bearer"}
