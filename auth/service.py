import os
import random
import fastapi as _fastapi
import fastapi.security as _security

import email_validator as _email_check
import jwt
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


async def create_token(user: _models.User):
    user_obj = _schemas.User.model_validate(user)
    user_dict = user_obj.model_dump()
    del user_dict["date_created"]
    token = jwt.encode(user_dict, JWT_SECRET, algorithm="HS256")
    return dict(access_token=token, token_type="bearer")


async def get_current_user(db: _orm.Session = _fastapi.Depends(get_db),
                           token: str = _fastapi.Depends(oauth2schema)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except Exception:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid token")
    return _schemas.User.model_validate(user)


def generate_otp():
    return str(random.randint(100000, 999999))

