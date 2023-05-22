from typing import Any, Generator
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .conftest import SessionTesting, engine, Base, start_application


@pytest.fixture(scope="function")
async def app() -> Generator[FastAPI, Any, None]:
    print("app")
    async with AsyncSession(engine) as session:
        async with session.begin():
            Base.metadata.create_all(bind=session.get_bind())
        app_test = start_application(session=session)
        yield app_test
        Base.metadata.drop_all(bind=session.get_bind())


@pytest.fixture(scope="function")
async def db_session(app: FastAPI) -> Generator[AsyncSession, Any, None]:
    async with engine.begin() as connection:
        async with connection.begin():
            async with SessionTesting() as session:
                try:
                    yield session
                finally:
                    await session.rollback()
                    await session.close()


@pytest.mark.usefixtures("app")
@pytest.fixture(scope="function")
async def client(
    app: FastAPI, db_session: SessionTesting
) -> Generator[AsyncClient, Any, None]:
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = await _get_test_db.__anext__
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        print("client", client)
        yield client
