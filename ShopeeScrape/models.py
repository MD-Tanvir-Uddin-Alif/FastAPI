from sqlalchemy import Integer, String, Column
from database_config import Base



class Category(Base):
    __tablename__ = 'categories'
    
    catId = Column(Integer, primary_key=True, index=True)
    parrent_name = Column(String)
    child_name = Column(String)

