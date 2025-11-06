from sqlalchemy import Integer, String, Column, Float, BigInteger
from database_config import Base

class Category(Base):
    __tablename__ = 'categories'
    
    catid = Column(Integer, primary_key=True, index=True)
    category_name = Column(String)
    parent_catid = Column(Integer, nullable=True)  
    parent_category_name = Column(String, nullable=True) 


class ProductsModel(Base):
    
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_catid = Column(Integer)
    catid = Column(Integer)
    price = Column(Float)
    price_before_discount = Column(Float)
    raw_discount = Column(Integer)
    discount_percentage = Column(String)
    name = Column(String)
    image = Column(String)
    sold = Column(Integer)
    historical_sold = Column(Integer)
    shop_name = Column(String)
    itemid = Column(BigInteger)
    shopid = Column(BigInteger)
    rating_star = Column(Float)
    rating_count = Column(Integer)
    shop_location = Column(String)
    stock = Column(Integer)