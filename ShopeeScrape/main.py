from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
import time

from database_config import engine, Base, get_db
from Scraper import get_shopee_categories
from category_subcategory_scrape import scrape_category_wise_products
from scrape_product_details import scrape_shopee_product
from models import Category, ProductsModel, parentCategories
from schema import CategoryOutSchema

Base.metadata.create_all(bind=engine)

app = FastAPI()


#------------------------------
#scrape category from shopee
#------------------------------
@app.post('/scrape-category')
def Category_Scrapa_and_save(db: Session = Depends(get_db)):
    categories = get_shopee_categories()
    
    for cat in categories:
        new_cat = Category(
            catid=cat['catid'],  
            category_name=cat['category_name'],  
            parent_catid=cat['parent_catid'], 
            parent_category_name=cat['parent_category_name']  
        )
        db.add(new_cat)
    
    db.commit() 
    return {"message": f"Saved {len(categories)} categories to DB!"}

#------------------------------
# get all the category
#------------------------------
@app.get('/all/products/')
def get_all_products(db: Session=Depends(get_db)):
    products = db.query(Category).all()
    
    if not products:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='something went wrong'
        )
    
    return products


#------------------------------
# get all the parent category
#------------------------------
@app.get('/all/parent-category/')
def get_all_main_category(db: Session=Depends(get_db)):
    categories = db.query(Category).filter(Category.parent_catid==0).all()
    if not categories:
        return JSONResponse( status_code=status.HTTP_404_NOT_FOUND, content="something went wrong" )
    return categories


#--------------------------------------------
# see child catetogry by parent category id
#--------------------------------------------
@app.get('/product/{category}')
def get_product_by_filtering(category: int, db: Session=Depends(get_db)):
    
    parent_id = db.query(Category.catid).filter(
        Category.catid==category, 
        Category.parent_catid==0
    ).scalar()  
    
    if parent_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Parent category not found"}
        )
    
    sub_categories = db.query(Category).filter(Category.parent_catid==parent_id).all()
    
    if not sub_categories:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "No sub-categories found for this parent"}
        )
    
    return sub_categories


#--------------------------------------
# product fetched by Parent Category
#--------------------------------------
# @app.post('/categories-wise-product/')
# def trigger_category_scrape(parent_ID: int ,db: Session = Depends(get_db)):
#     data = db.query(Category.parent_catid, Category.catid).filter(Category.parent_catid == parent_ID).all()
#     result = [{"parent_catid": row[0], "catid": row[1]} for row in data]
    
#     products = scrape_category_wise_products(result)  
    
#     for prod in products:
#         db_product = ProductsModel(**prod) 
#         db.add(db_product)
#     db.commit()
    
#     return {'message': f"Saved {len(products)} products to database"}

@app.post('/categories-wise-product/')
def trigger_category_scrape(db: Session = Depends(get_db)):
    parents = db.query(parentCategories.parent_id).all()
    parent_ids = [row[0] for row in parents]

    total_saved = 0
    
    for idx, parent_id in enumerate(parent_ids):
        data = db.query(Category.parent_catid, Category.catid).filter(Category.parent_catid == parent_id).all()
        result = [{"parent_catid": row[0], "catid": row[1]} for row in data]
        
        products = scrape_category_wise_products(result)
        
        for prod in products:
            db_product = ProductsModel(**prod)
            db.add(db_product)
        db.commit()
        
        total_saved += len(products)
        
        parent = db.query(parentCategories).filter(parentCategories.parent_id == parent_id).first()
        if parent:
            parent.time_stamp_of_scraped = datetime.now(ZoneInfo('UTC'))
            db.commit()
        
        if idx < len(parent_ids) - 1:
            time.sleep(600)
    return {'message': f"Saved {total_saved} products to database across all parents"}



#------------------------------------------------
# see product details by shop and product id
#------------------------------------------------
@app.post('/product/{shopId}/{productId}/')
def product_details(shopId: int, productId: int, db: Session=Depends(get_db)):
    details = scrape_shopee_product(shopId, productId)
    return details