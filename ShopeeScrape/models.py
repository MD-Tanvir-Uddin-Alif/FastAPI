from sqlalchemy import Integer, String, Column, Float, BigInteger, DateTime, Boolean
from database_config import Base
from datetime import datetime, UTC, timezone

class Category(Base):
    __tablename__ = 'categories'
    
    catid = Column(Integer, primary_key=True, index=True)
    category_name = Column(String)
    parent_catid = Column(Integer, nullable=True)  
    parent_category_name = Column(String, nullable=True) 


class parentCategories(Base):
    
    __tablename__ = 'parent_categories'
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer)
    name = Column(String)
    time_stamp_of_scraped = Column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))

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


class ProductDetailModel(Base):
    
    __tablename__ = 'product_detail'
    
    id = Column(Integer, primary_key=True, index=True)


class DeviceModel(Base):
    
    __tablename__ = 'device'
    
    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String)
    email = Column(String)
    password = Column(String)
    cookies = Column(String)
    number_of_attem = Column(Integer, default=0)
    is_faild = Column(Boolean, default=False)
    failed_time = Column(DateTime(timezone=True), nullable=True ,default=None, onupdate=lambda: datetime.now(timezone.utc))
    update_time = Column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))