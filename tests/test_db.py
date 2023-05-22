# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from typing import Annotated
# from fastapi import Depends
# import pytest
# import logging

# logger = logging.getLogger(__name__)


# SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL, echo=True, future=True)
# TestSession = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# Base = declarative_base()


# @pytest.mark.asyncio
# async def test_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)


# @pytest.mark.asyncio
# async def test_get_db() -> AsyncSession:
#     async with TestSession() as session:
#         yield session


# db_test_dependency = Annotated[AsyncSession, Depends(test_get_db)]
