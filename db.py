from sqlalchemy.ext import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from typing import Annotated
from fastapi import Depends


SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://fwambttb:JoXQCdvCzFEVpUSYHFbPQr128CDvDDhh@horton.db.elephantsql.com/fwambttb"
# SQLALCHEMY_DATABASE_URL = (
#     "postgresql+asyncpg://postgres:odeya2626@localhost:5432/todo_app_db"
# )
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todo_app.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


db_dependency = Annotated[AsyncSession, Depends(get_db)]
# db_dependency = Annotated[Session, Depends(get_db)]
