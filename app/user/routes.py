import time
import asyncio
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from . import schemas, services, utils, model

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = services.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = services.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return services.create_user(db=db, user=user)

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = services.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = utils.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: schemas.UserResponse = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.UserResponse)
def update_user_me(user_update: schemas.UserUpdate, current_user: model.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.username and user_update.username != current_user.username:
        db_user = services.get_user_by_username(db, username=user_update.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already taken")
    return services.update_user(db=db, user=current_user, user_update=user_update)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(current_user: model.User = Depends(get_current_user), db: Session = Depends(get_db)):
    services.delete_user(db=db, user=current_user)
    return None

@router.get("/report-blocked")
async def get_report_blocked(current_user: model.User = Depends(get_current_user)):
    print(f"User {current_user.username} triggered blocking task")
    time.sleep(5)
    print(f"User {current_user.username} blocking task finished")
    return {
        "username": current_user.username,
        "status": "blocked"
    }

@router.get("/report-async")
async def get_report_async(current_user: model.User = Depends(get_current_user)):
    print(f"User {current_user.username} triggered async task")
    await asyncio.sleep(5)
    print(f"User {current_user.username} async task finished")
    return {
        "username": current_user.username,
        "status": "async"
    }
    
    
#Test 1
@router.get("/block-test")
async def blocking_endpoint(current_user: model.User = Depends(get_current_user)):
    print(f"User {current_user.username} triggered blocking task")
    time.sleep(5)
    print(f"User {current_user.username} blocking task finished")
    return {"status": "Blocked for 5 seconds"}
#Test 2
@router.get("/async-test")
async def async_endpoint(current_user: model.User = Depends(get_current_user)):
    print(f"User {current_user.username} triggered async task")
    await asyncio.sleep(5)
    print(f"User {current_user.username} async task finished")
    return {"status": "Non-blocking sleep for 5 seconds"}