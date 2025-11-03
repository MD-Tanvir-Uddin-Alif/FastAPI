from pydantic import BaseModel
from typing import Optional


class BaseProduct(BaseModel):
    name: str
    description : str


class ProductCreate(BaseModel):
    name: str
    description: str


class UpdateProduct(BaseModel):
    name : Optional[str]=None
    description : Optional[str]=None
