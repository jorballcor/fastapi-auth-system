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
