from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from database import get_db, Base, engine
from schema import ProductCreate
from models import Product


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post('/create/product')
def product_create(product: ProductCreate, db: Session = Depends(get_db)):
    new_Product = Product(**(product.dict()))
    db.add(new_Product)
    db.commit()
    db.refresh(new_Product)
    return new_Product