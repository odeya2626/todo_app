from db import Base, engine
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    email = Column(String, index=True, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    disabled = Column(Boolean, default=True)
    role = Column(String, default="user")
    phone = Column(String, nullable=True)
    # address_id = Column(Integer, ForeignKey("address.id"), nullable=True)

    todos = relationship("Todos", back_populates="owner")
    address = relationship("Address", back_populates="user_address")


class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    priority = Column(Integer, index=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="todos")


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, index=True)
    street = Column(String, index=True)
    suite = Column(String, index=True)
    city = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_address = relationship("User", back_populates="address")


User.__table__.create(bind=engine, checkfirst=True)
Todos.__table__.create(bind=engine, checkfirst=True)
Address.__table__.create(bind=engine, checkfirst=True)
