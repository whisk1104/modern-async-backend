from sqlalchemy.orm import Session
from . import model, schemas, utils

def get_user_by_username(db: Session, username: str):
    return db.query(model.User).filter(model.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pwd = utils.get_password_hash(user.password)
    db_user = model.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not utils.verify_password(password, user.hashed_password):
        return False
    return user

def update_user(db: Session, user: model.User, user_update: schemas.UserUpdate):
    if user_update.username:
        user.username = user_update.username
    if user_update.email:
        user.email = user_update.email
    if user_update.password:
        user.hashed_password = utils.get_password_hash(user_update.password)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: model.User):
    db.delete(user)
    db.commit()