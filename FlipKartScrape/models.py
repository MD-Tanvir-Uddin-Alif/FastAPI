from sqlalchemy import Column, String, Integer
from database_config import Base

class ProductDetails(Base):
    
    __tablename__ = 'Product_Details'
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    title = Column(String)
    price = Column(String)
    image_link = Column(String)
    product_link = Column(String)