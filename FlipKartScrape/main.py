from database_config import Base, engine, get_db
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from models import ProductDetails

from scraper import run_all_scraper


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post('/scrape/FlipKart')
async def scrape_flipKart(db: Session = Depends(get_db)):
    data = await run_all_scraper()
    
    for item in data:
        product = ProductDetails(
            category=item["category"],
            title=item["title"],
            price=item["price"],
            image_link=item["image_link"],
            product_link=item["product_link"]
        )
        db.add(product)
    
    db.commit()
    return {'message':'scraped sucessfully', 'total_saved':len(data)}


@app.get('/product/{category}')
def get_prodcut_by_category(category: str, db: Session = Depends(get_db)):
    products = db.query(ProductDetails).filter(ProductDetails.category==category).all()
    
    if len(products):
        return{'message':'Product found', 'data':products}
    else:
        return{'message':'No product is found based on the search query'}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Something went worg"
    )