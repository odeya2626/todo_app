import sys

sys.path.append(".")
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Annotated, Any, Generator
from fastapi import Depends
import pytest
import logging
from fastapi import FastAPI
from routers import auth, todos, admin, users
from fastapi.testclient import TestClient
from db import get_db
from httpx import AsyncClient


logger = logging.getLogger(__name__)


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
Base = declarative_base()


# @pytest.fixture(scope="function")
# def app() -> Generator[FastAPI, Any, None]:
#     """
#     Create an new db on each test case.
#     """
#     Base.metadata.create_all(engine)  # Create the tables.
#     app_test = start_application()
#     yield app_test
#     Base.metadata.drop_all(engine)


# with TestClient(app) as client:
#     yield client


# @pytest.mark.asyncio
# async def test_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)


# @pytest.mark.asyncio
# async def test_get_db() -> AsyncSession:
#     async with TestSession() as session:
#         yield session
