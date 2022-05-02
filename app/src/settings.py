from distutils.command.config import config
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

import os

import motor.motor_asyncio

SECRET_KEY = "4ab5be85c8c56eecdd547f7831979be83de58a6768d10a314f54cda4e4d67ffe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# hashing
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# setting up oauth2_scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


# Database variables
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
db_user=os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
DB_URL = "mongodb+srv://"+db_user+":"+db_password+"@lima-labs.j4xof.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
db = client.users
component_document = client.components