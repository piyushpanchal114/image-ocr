import os
import fastapi as _fastapi
import fastapi.security as _security

import email_validator as _email_check
import passlib.hash as _hash
import sqlalchemy.orm as _orm

import database as _database
import models as _models
import schemas as _schemas


JWT_SECRET = os.environ.get("JWT_SECRET")
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User)\
        .filter(_models.User.email == email
                and _models.User.is_verified).first()


async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    try:
        valid = _email_check.validate_email(user.email)
        name = user.name
        email = valid.email
    except _email_check.EmailNotValidError:
        raise _fastapi.HTTPException(status_code=400,
                                     detail="Invalid email address")

    user_obj = _models.User(email=email, name=name,
                            hashed_password=_hash.bcrypt.hash(user.password))

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(email, db)

    if not user:
        return False

    if not user.is_verified:
        return False

    if not user.verify_password(password):
        return False

    return user
