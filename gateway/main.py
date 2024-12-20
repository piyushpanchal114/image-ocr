import base64
import fastapi as _fastapi
import jwt
import logging
import os
import pika
import requests
import rpc_client
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logging.basicConfig(level=logging.INFO)

JWT_SECRET = os.environ.get("JWT_SECRET")
AUTH_BASE_URL = os.environ.get("AUTH_BASE_URL")
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_URL, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue="gateway_service")
channel.queue_declare(queue="ocr_service")


async def jwt_validation(token: str = _fastapi.Depends(oauth2_scheme)):
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


# Auth Endpoints
@app.post("auth/login", tags=["Authentication Service"])
async def login(user_data: UserCredentials):
    try:
        response = requests.post(f"{AUTH_BASE_URL}/api/token", json={
            "username": user_data.username, "password": user_data.password})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
    except requests.ConnectionError:
        raise HTTPException(status_code=503,
                            detail="Authentication service is down.")


@app.post("auth/register", tags=["Authentication Service"])
async def register(user_data: UserRegistration):
    try:
        response = requests.post(
            f"{AUTH_BASE_URL}/api/users",
            json={"name": user_data.name, "email": user_data.email,
                  "password": user_data.password})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
    except requests.ConnectionError:
        raise HTTPException(status_code=503,
                            detail="Authentication service is down.")


@app.post("/auth/generate-otp", tags=["Authentication Service"])
def generate_otp(user_data: GenerateOtp):
    try:
        response = requests.post(f"{AUTH_BASE_URL}/api/users/generate-otp",
                                 json={"email": user_data.email})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
    except requests.ConnectionError:
        raise HTTPException(status_code=503,
                            detail="Authentication service is down.")


@app.post("/auth/verify-otp", tags=["Authentication Service"])
def verify_otp(user_data: VerifyOtp):
    try:
        response = requests.post(f"{AUTH_BASE_URL}/api/users/verify-otp",
                                 json={"email": user_data.email,
                                       "otp": user_data.otp})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
    except requests.ConnectionError:
        raise HTTPException(status_code=503,
                            detail="Authentication service is down.")


# OCR/ML Endpoints

@app.post("/ocr", tags=["Machine Learning Service"])
def ocr(file: UploadFile = File(...),
        payload: dict = _fastapi.Depends(oauth2_scheme)):
    with open(file.filename, "rb") as buffer:
        buffer.write(file.file.read())

    ocr_rpc = rpc_client.OcrRpcClient()

    with open(file.filename, "rb") as buffer:
        file_data = buffer.read()
        file_base64 = base64.b64encode(file_data).decode()

    request_json = {
        "user_name": payload["name"],
        "user_email": payload["email"],
        "user_id": payload["id"],
        "file": file_base64
    }

    response = ocr_rpc.call(request_json)

    os.remove(file.filename)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
