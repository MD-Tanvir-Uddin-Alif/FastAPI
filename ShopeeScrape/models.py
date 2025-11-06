from sqlalchemy import Integer, String, Column
from database_config import Base

class Category(Base):
    __tablename__ = 'categories'
    
    catid = Column(Integer, primary_key=True, index=True)
    category_name = Column(String)
    parent_catid = Column(Integer, nullable=True)  
    parent_category_name = Column(String, nullable=True)  