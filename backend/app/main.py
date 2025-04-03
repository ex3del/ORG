from fastapi import FastAPI, Depends
from .database import engine, Base, get_db
from .models import User, Document, ChatSession, Message  # Import to register models
from sqlalchemy.orm import Session

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

