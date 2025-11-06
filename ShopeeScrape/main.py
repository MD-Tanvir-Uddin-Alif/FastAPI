from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from database_config import engine, Base, get_db
from Scraper import get_shopee_categories
from category_subcategory_scrape import scrape_category_wise_products
from models import Category, ProductsModel
from schema import CategoryOutSchema

Base.metadata.create_all(bind=engine)

app = FastAPI()

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


@app.get('/all/products/')
def get_all_products(db: Session=Depends(get_db)):
    products = db.query(Category).all()
    
    if not products:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='something went wrong'
        )
    
    return products


@app.get('/all/parent-category/')
def get_all_main_category(db: Session=Depends(get_db)):
    categories = db.query(Category).filter(Category.parent_catid==0).all()
    
    if not categories:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="something went wrong"
        )
        
    return categories


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



@app.post('/categories-wise-product/')
def trigger_category_scrape(db: Session = Depends(get_db)):
    data = db.query(Category.parent_catid, Category.catid).filter(Category.parent_catid != 0).all()
    result = [{"parent_catid": row[0], "catid": row[1]} for row in data]
    
    products = scrape_category_wise_products(result)  # Call the renamed scraping function
    
    for prod in products:
        db_product = ProductsModel(**prod)  # Use your actual model name
        db.add(db_product)
    db.commit()
    
    return {'message': f"Saved {len(products)} products to database"}