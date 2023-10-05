import sys

sys.path.append(".")

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from routers import admin, auth, todos, users

from db import Base  # isort: skip


def start_application():
    app = FastAPI()
    app.include_router(auth.router)
    app.include_router(todos.router)
    app.include_router(admin.router)
    app.include_router(users.router)
    return app


SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL, echo=True, future=True)
SessionTesting = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
