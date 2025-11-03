from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from database import get_db, Base, engine
from schema import ProductCreate, BaseModel
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


@app.get('/all/products')
def get_all_product(db: Session = Depends(get_db)):
    all_products = db.query(Product).all()
    return all_products


@app.get('/product/{p_id}')
def Single_Product(p_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id==p_id).first()
    return product