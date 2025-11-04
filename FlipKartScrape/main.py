import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from database_config import Base, engine, get_db
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
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