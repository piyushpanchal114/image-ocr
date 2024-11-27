import fastapi as _fastapi
import logging
import os
import pika
import sqlalchemy.orm as _orm

import database as _database
import models as _models
import schemas as _schemas
import service as _services

# Environment variables
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")

# RabbitMQ connection
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_URL, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue="email_notification")


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = _fastapi.FastAPI()
logging.basicConfig(level=logging.INFO)
_models.Base.metadata.create_all(_models.engine)


@app.post("/api/users", tags=["User Auth"])
async def create_user(
    user: _schemas.UserCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = await _services.get_user_by_email(user.email, db)

    if db_user:
        logging.info("User with this email already exists")
        raise _fastapi.HTTPException(
            status_code=200, detail="User with this email already exists")

    user = await _services.create_user(user, db)
    return _fastapi.HTTPException(
        status_code=201, detail="User Registered Successfully")
