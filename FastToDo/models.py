from sqlalchemy import Column, Integer, String, Boolean
from database_config import Base


class ToDoModel(Base):
    
    __tablename__ = 'myToDo'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300))
    description = Column(String(600))
    status = Column(Boolean, default=False)
