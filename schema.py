from pydantic import BaseModel



class BaseProduct(BaseModel):
    name: str
    description : str


class ProductCreate(BaseModel):
    name: str
    description: str
