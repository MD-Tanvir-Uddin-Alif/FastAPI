from pydantic import BaseModel
from typing import Optional

class ToDoSchema(BaseModel):
    title: str
    description: str
    status: bool

class UpdateToDoSchema(BaseModel):
    title: Optional[str]=None
    description: Optional[str]=None
    status: Optional[bool]=None