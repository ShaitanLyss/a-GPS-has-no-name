from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.graphql import graphql_app

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(graphql_app, prefix="/graphql")


origins = ["http://localhost:5173", "http://localhost:8080", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
