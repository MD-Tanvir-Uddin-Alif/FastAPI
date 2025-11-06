from pydantic import BaseModel


class CategoryOutSchema(BaseModel):
    parent_id: int
    child_id: int
    
    class Config:
        orm_mode = True
