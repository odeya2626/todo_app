from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from typing import Annotated
from fastapi import Depends


SQLALCHEMY_DATABASE_URL = "postgresql://fwambttb:JoXQCdvCzFEVpUSYHFbPQr128CDvDDhh@horton.db.elephantsql.com/fwambttb"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:odeya2626@localhost:5432/todo_app_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todo_app.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
