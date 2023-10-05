import asyncio
from typing import Any, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from main import app

from .conftest import Base, SessionTesting, engine, start_application


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    async with SessionTesting() as session:
        async with engine.begin() as conn:
            print("create_all")
            await conn.run_sync(Base.metadata.create_all)

        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async with engine.begin() as conn:
        print("drop_all")
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def client(db_session: SessionTesting) -> Generator[AsyncClient, Any, None]:
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        print("client", client)
        yield client
