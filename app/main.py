from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.routers.api import router
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    debug=True,
    title='Template API'
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1")
def read_root():
    return {
        "message": "Welcome to the FastAPI example"
    }
