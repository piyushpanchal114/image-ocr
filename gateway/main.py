import logging
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logging.basicConfig(level=logging.INFO)
