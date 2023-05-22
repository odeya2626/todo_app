# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from typing import Annotated, Any, Generator
# from fastapi import Depends
# import pytest
# import logging
# from fastapi import FastAPI
# from routers import auth, todos, admin, users
# from fastapi.testclient import TestClient
# from db import get_db

# logger = logging.getLogger(__name__)


# def start_application():
#     app = FastAPI()
#     app.include_router(auth.router)
#     app.include_router(todos.router)
#     app.include_router(admin.router)
#     app.include_router(users.router)
#     return app


# SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL, echo=True, future=True)
# SessionTesting = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# Base = declarative_base()


# # db_test_dependency = Annotated[AsyncSession, Depends(get_db)]


# # SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
# # engine = create_engine(
# #     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# # )
# # Use connect_args parameter only with sqlite
# # SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# @pytest.fixture(scope="function")
# def app() -> Generator[FastAPI, Any, None]:
#     """
#     Create an new db on each test case.
#     """
#     Base.metadata.create_all(engine)  # Create the tables.
#     app_test = start_application()
#     yield app_test
#     Base.metadata.drop_all(engine)


# @pytest.fixture(scope="function")
# def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
#     connection = engine.connect()
#     transaction = connection.begin()
#     session = SessionTesting(bind=connection)
#     yield session
#     session.close()
#     transaction.rollback()
#     connection.close()


# @pytest.fixture(scope="function")
# def client(
#     app: FastAPI, db_session: SessionTesting
# ) -> Generator[TestClient, Any, None]:
#     def _get_test_db():
#         try:
#             yield db_session
#         finally:
#             pass

#     app.dependency_overrides[get_db] = _get_test_db
#     with TestClient(app) as client:
#         yield client


# # @pytest.mark.asyncio
# # async def test_models():
# #     async with engine.begin() as conn:
# #         await conn.run_sync(Base.metadata.drop_all)
# #         await conn.run_sync(Base.metadata.create_all)


# # @pytest.mark.asyncio
# # async def test_get_db() -> AsyncSession:
# #     async with TestSession() as session:
# #         yield session
