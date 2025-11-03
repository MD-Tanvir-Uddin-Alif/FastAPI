from sqlalchemy import Column, Integer, String
from database_config import Base


class ToDoModel(Base):
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String)