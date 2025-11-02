from fastapi import FastAPI
from models import UserInfo

app = FastAPI()

users = [
    UserInfo(name="Alice Johnson", age=28, nationality="American", phone_number=1234567890, salary=75000.0),
    UserInfo(name="Mohammad Rahman", age=35, nationality="Bangladeshi", phone_number=8801712345678, salary=55000.0),
    UserInfo(name="Liu Wei", age=42, nationality="Chinese", phone_number=8613812345678, salary=82000.0),
    UserInfo(name="Carlos Mendez", age=30, nationality="Mexican", phone_number=525512345678, salary=60000.0),
    UserInfo(name="Fatima Al-Farsi", age=26, nationality="Omani", phone_number=96891234567, salary=48000.0),
    UserInfo(name="John Smith", age=50, nationality="British", phone_number=447911234567, salary=91000.0),
    UserInfo(name="Akira Tanaka", age=33, nationality="Japanese", phone_number=819012345678, salary=70000.0),
    UserInfo(name="Elena Petrova", age=29, nationality="Russian", phone_number=79261234567, salary=67000.0),
    UserInfo(name="Samuel Okoro", age=38, nationality="Nigerian", phone_number=2348031234567, salary=58000.0),
    UserInfo(name="Isabelle Dubois", age=45, nationality="French", phone_number=33612345678, salary=88000.0),
]


@app.get('/')
def HelloFunction():
    return("Welcome back to me")


@app.get('/user-info')
def user_info():
    return users


@app.post('/create-user')
def Create_User(user:UserInfo):
    users.append(user)
    return user