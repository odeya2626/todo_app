import sys

sys.path.append("...")
from fastapi import (
    FastAPI,
    APIRouter,
    Depends,
    Path,
    Body,
    HTTPException,
    status,
    Request,
    Response,
    Form,
)
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import JWTError, jwt
from datetime import timedelta, datetime
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from db import db_dependency
from models import User

router = APIRouter(
    prefix="/auth", tags=["auth"], responses={401: {"user": "Not authorized"}}
)
SECRET_KEY = "vghlkjk,mcxsseaerfuiojml, mnvfxdsredui786554432"
ALGORITHM = "HS256"
templates = Jinja2Templates(directory="templates")
bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class LoginForm:
    def __init__(self, request: Request) -> None:
        self.request: Request = request
        self.username: str = None
        self.password: str = None

    async def create_oath_from(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


# class CreateUserRequest(BaseModel):
#     username: str = Field(min_length=3)
#     password: str = Field(min_length=3)
#     email: str = Field(min_length=3)
#     first_name: str = Field(min_length=3)
#     last_name: str = Field(min_length=3)
#     disabled: bool = Field(default=True)
#     role: str = Field(default="user")
#     phone_number: str or None = Field(default=None)


class Token(BaseModel):
    access_token: str
    token_type: str


async def get_password_hash(password):
    return bcrypt.hash(password)


async def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)


async def authenticate_user(username: str, password: str, db):
    user = await db.execute(select(User).filter(User.username == username))
    user = user.scalar_one_or_none()
    print(user, "user")
    if not user:
        return False
    if not bcrypt.verify(password, user.password):
        return False
    return user


async def create_access_token(
    username: str, user_id: int, user_role: str, expires_delta: timedelta
):
    to_encode = {"username": username, "user_id": user_id, "user_role": user_role}
    expires = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        user_id: int = payload.get("user_id")
        user_role: str = payload.get("user_role")
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "user_id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not Found")


# @router.post("/", status_code=status.HTTP_201_CREATED)
# async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
#     create_user_model = User(
#         password=bcrypt.hash(create_user_request.password),
#         **create_user_request.dict(exclude={"password"})
#     )
#     db.add(create_user_model)
#     db.commit()

#     return create_user_model


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        return False
        # raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = await create_access_token(
        user.username, user.id, user.role, timedelta(minutes=30)
    )
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True
    # return {"access_token": token, "token_type": "bearer"}


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    try:
        print(request)
        form = LoginForm(request)
        await form.create_oath_from()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(
            response=response, form_data=form, db=db
        )
        print(validate_user_cookie)
        if not validate_user_cookie:
            msg = "Invalid username or password"
            return templates.TemplateResponse(
                "login.html", {"request": request, "msg": msg}
            )
        return response
    except HTTPException:
        msg = "Unknow error"
        return templates.TemplateResponse(
            "login.html", {"request": request, "msg": msg}
        )


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    msg = "Logout successful"
    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg}
    )
    response.delete_cookie("access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    db: db_dependency,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
):
    validation1 = await db.execute(select(User).filter(User.username == username))
    validation1 = validation1.scalar_one_or_none()
    validation2 = await db.execute(select(User).filter(User.email == email))
    validation2 = validation2.scalar_one_or_none()

    if validation1 is not None:
        msg = "Username already exists"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )
    if validation2 is not None:
        msg = "Email already exists"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )
    if password != password2:
        msg = "Password and confirm password do not match"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )

    try:
        user = User(
            username=username,
            email=email,
            password=bcrypt.hash(password),
            first_name=firstname,
            last_name=lastname,
            role="user",
            disabled=False,
        )
        db.add(user)
        await db.commit()
        msg = "Register successful"
        response = templates.TemplateResponse(
            "login.html", {"request": request, "msg": msg}
        )
        print(response)
        return response
    except HTTPException:
        msg = "Unknow error"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )

    # if validation1 is not None or validation2 is not None or password != password2:
    #     msg = "Invalid resignation information"
    #     return templates.TemplateResponse(
    #         "register.html", {"request": request, "msg": msg}
    #     )


# # Exceptions
# def get_user_exception():
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     return credentials_exception


# def token_exception():
#     token_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid authentication credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     return token_exception
