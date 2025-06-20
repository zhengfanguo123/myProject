from fastapi import FastAPI

from .database import Base, engine
from .routers import users, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Community API")

app.include_router(auth.router)
app.include_router(users.router)


@app.get('/')
def read_root():
    return {"message": "Welcome to the community API"}
