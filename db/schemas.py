from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base 

Base = declarative_base()


class UsersDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    is_active = Column(Boolean, default=True)


class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    done = Column(Boolean, default=False)
    owner_id = Column(Integer, nullable=False)  # Foreign key to UsersDB