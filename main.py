from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, HTTPException,status
from database import get_db, Base, engine
from schema import ProductCreate, BaseModel, UpdateProduct
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


@app.delete('/product/{p_id}')
def Delete_Product(p_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id==p_id).first()
    if product:
        db.delete(product)
        db.commit()
        raise HTTPException(
            status_code = status.HTTP_200_OK,
            detail= f"product {id} is deleted"
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message':f"unable to delete the product"}
        )



@app.put('/product/{p_id}')
def Update_Full_Product(p_id: int, product: UpdateProduct ,db: Session = Depends(get_db)):
    uProduct = db.query(Product).filter(Product.id==p_id).first()
    for key, value in product.dict(exclude_unset=True).items():
        setattr(uProduct, key, value)
    
    db.commit()
    db.refresh(uProduct)
    return uProduct

@app.patch('/product/{p_id}')
def Update_Product(p_id: int, product: UpdateProduct ,db: Session = Depends(get_db)):
    uProduct = db.query(Product).filter(Product.id==p_id).first()
    for key, value in product.dict(exclude_unset=True).items():
        setattr(uProduct, key, value)
    
    db.commit()
    db.refresh(uProduct)
    return uProduct