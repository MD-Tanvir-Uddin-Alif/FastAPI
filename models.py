from pydantic import BaseModel



class UserInfo(BaseModel):
    name: str
    age: int
    nationality: str
    phone_number: int
    salary: float