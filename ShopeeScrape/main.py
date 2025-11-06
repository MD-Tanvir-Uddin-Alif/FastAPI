from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database_config import engine, Base, get_db
from Scraper import get_shopee_categories
from models import Category

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
def get_product_by_filtering(category: str, db: Session=Depends(get_db)):
    
    parent_id = db.query(Category.catid).filter(
        Category.category_name==category, 
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



@app.get('/categories-wise-product/')
def get_category_wise_product(db: Session=Depends(get_db)):
    data = db.query(Category.parent_catid, Category.catid).filter(Category.parent_catid==0).all()
    return data