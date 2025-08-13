from sqlalchemy import Column, Integer, String,ForeignKey
from task_manager.db.database import Base

class User(Base):
    __tablename__ = "users1"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)


class Task(Base):
    __tablename__ = "tasks1"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner = Column(String, nullable=False)
