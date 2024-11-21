import jwt
import logging
import os
import pika
from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logging.basicConfig(level=logging.INFO)

JWT_SECRET = os.environ.get("JWT_SECRET")
AUTH_BASE_URL = os.environ.get("AUTH_BASE_URL")
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue="gateway_service")
channel.queue_declare(queue="ocr_service")


async def jwt_validation(token: str):
    """Validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Models
class GenerateUserToken(BaseModel):
    username: str
    password: str


class UserCredentials(BaseModel):
    username: str
    password: str


class UserRegistration(BaseModel):
    name: str
    email: str
    password: str


class GenerateOtp(BaseModel):
    email: str


class VerifyOtp(BaseModel):
    email: str
    otp: str
