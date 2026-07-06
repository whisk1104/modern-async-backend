import time
from sqlalchemy import create_engine
from app.database import engine, Base
from app.user import model  
from fastapi import FastAPI
from app.user.routes import router as user_router

def init_db():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            return
        except Exception as e:
            print(f"Database connection failed, retrying... Error: {e}")
            retries -= 1
            time.sleep(5)
    raise Exception("Database connection failed")

init_db()

app = FastAPI()
app.include_router(user_router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Success"}